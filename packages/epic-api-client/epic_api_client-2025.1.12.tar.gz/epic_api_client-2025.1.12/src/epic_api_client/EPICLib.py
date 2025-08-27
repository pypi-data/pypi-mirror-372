#    ____   # -------------------------------------------------- #
#   | ^  |  # EPICLib for AUMC               				     #
#   \  --   # o.m.vandermeer@amsterdamumc.nl        			 #
# \_| ﬤ| ﬤ  # If you like this code, treat him to a coffee! ;)	 #
#   |_)_)   # -------------------------------------------------- #

import os
import requests_unixsocket
from urllib.parse import quote_plus

def is_cloud() -> bool:
    return os.getenv("EPIC_CAPABILITY_SOCK_ROOT") is not None

def get_socket(capability_name: str) -> str:
    """Retrieves the socket path for the given capability name."""
    if not is_cloud():
        return "local"  # Handle local environment as needed

    cap_sock_root = os.environ["EPIC_CAPABILITY_SOCK_ROOT"]
    info_sock = os.environ["EPIC_CAPABILITY_INFO_SOCK"]

    # Build URL to capability metadata endpoint
    info_socket_path = quote_plus(f"{cap_sock_root}/{info_sock}")
    url = f"http+unix://{info_socket_path}/v1"

    # Fetch metadata
    response = requests_unixsocket.get(url)
    response.raise_for_status()
    metadata = response.json().get("capabilities", [])

    # Find capability and extract address
    for cap in metadata:
        if cap.get("name") == capability_name:
            address = cap.get("address")
            if not address:
                raise ValueError(f"Capability '{capability_name}' missing address.")
            full_socket = quote_plus(f"{cap_sock_root}/{address}")
            return full_socket

    raise KeyError(f"Capability '{capability_name}' not found.")

# Usage example:
socket = get_socket("web-callout")
print(socket)  # Outputs the formatted socket path for cloud use