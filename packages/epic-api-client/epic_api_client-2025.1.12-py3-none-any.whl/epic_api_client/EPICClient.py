#    ____   # -------------------------------------------------- #
#   | ^  |  # EPICClient for AUMC               				 #
#   \  --   # o.m.vandermeer@amsterdamumc.nl        			 #
# \_| ﬤ| ﬤ  # If you like this code, treat him to a coffee! ;)	 #
#   |_)_)   # -------------------------------------------------- #

from json import dumps
from epic_api_client.EPICHttpClient import EPICHttpClient
from epic_api_client.FHIRExtension import FHIRExtension
from epic_api_client.JWTGenerator import JWTGenerator
import requests
import warnings
import importlib


class EPICClient(EPICHttpClient):
    def __init__(
        self,
        base_url: str = None,
        headers: dict = None,
        client_id: str = None,
        jwt_generator: JWTGenerator = None,
        use_unix_socket: bool = False,
        debug_mode: bool = False,
    ):
        super().__init__(base_url, headers, client_id, jwt_generator, use_unix_socket, debug_mode)
        # Pass `self` to extensions
        self.check_for_updates("epic_api_client")
        self.fhir = FHIRExtension(self)
        self.internal = None  # Initialize as None

        try:
            # Attempt to import from the new separate package
            from epic_internal_extension.InternalExtension import InternalExtension
            self.internal = InternalExtension(self)
            # Optional: print a success message or log
            print("INFO: epic_internal_extension loaded successfully.")
        except ImportError:
            # This is expected if the internal extension is not installed
            print(
                "INFO: epic_internal_extension not found. Internal features will be unavailable. "
                "Install epic-internal-extension package for internal functionality."
            )
        except Exception as e:
            # Catch any other error during import or instantiation
            print(f"WARNING: Failed to load epic_internal_extension: {e}")
        self.dino = "Mrauw!"

    def check_for_updates(self, package_name):
        try:
            # Get the installed version
            current_version = importlib.metadata.version(package_name)

            # Query the PyPI API for the latest version
            response = requests.get(
                f"https://pypi.org/pypi/{package_name}/json", timeout=5
            )
            response.raise_for_status()  # Raise HTTPError for bad responses

            latest_version = response.json()["info"]["version"]

            # Compare versions
            if current_version != latest_version:
                print(
                    f"Update available: {package_name} {latest_version} (current: {current_version}).\n"
                    f"Run `pip install --upgrade {package_name}` to update."
                )
            else:
                print(f"{package_name} is up to date: {current_version}")
        except requests.ConnectionError:
            print("No internet connection. Skipping version check.")
        except Exception as e:
            print(f"Version check failed: {e}")


