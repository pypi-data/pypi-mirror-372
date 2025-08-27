#    ____   # -------------------------------------------------- #
#   | ^  |  # EPICClient for AUMC               				 #
#   \  --   # o.m.vandermeer@amsterdamumc.nl        			 #
# \_| ﬤ| ﬤ  # If you like this code, treat him to a coffee! ;)	 #
#   |_)_)   # -------------------------------------------------- #

from json import dumps
from epic_api_client.SimpleHttpClient import SimpleHttpClient
from epic_api_client.JWTGenerator import JWTGenerator
import requests
from epic_api_client.EPICLib import get_socket


class EPICHttpClient(SimpleHttpClient):
    def __init__(
        self,
        base_url: str = None,
        headers: dict = None,
        client_id: str = None,
        jwt_generator: JWTGenerator = None,
        use_unix_socket: bool = False,
        debug_mode: bool = False,
    ):
        socket_path = get_socket("web-callout") if use_unix_socket else None
        super().__init__(base_url, headers, use_unix_socket, socket_path=socket_path, debug_mode=debug_mode)
        self.set_header("Epic-Client-ID", client_id)
        if base_url is None:
            raise ValueError("No base URL provided. For example sandbox URL is https://vendorservices.epic.com/some-interconnect-oauth/")
        else:
            print("base url: ", self.base_url)
        self.jwt_generator = jwt_generator
        self.client_id = client_id
        self.dino = "Mrauw!"

    def set_token(self, token: str):
        self.set_header("Authorization", f"Bearer {token}")
        self.set_header("Accept", "application/fhir+json")

    def obtain_access_token(self) -> dict:
        parts = self.client_id.split('-')
        if len(parts) > 1:
            last_part = parts[-1]
            sanitized_id = f"<rest of client id>-{last_part}"
        else:
            sanitized_id = "<client id>"        
        token_endpoint = self.base_url + "/oauth2/token"
        print(f"obtaining access token for {sanitized_id} at {self.base_url}...")
        # Generate JWT
        jwt_token = self.jwt_generator.create_jwt(self.client_id, token_endpoint)

        # Set up the POST request data
        data = {
            "grant_type": "client_credentials",
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": jwt_token,
        }

        # POST the JWT to the token endpoint
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(token_endpoint, data=data, headers=headers)
        response_data = response.json()
        # Check for successful response
        if response.status_code == 200:
            print("authentication successful")
            self.access_token = response_data.get("access_token")
            self.set_token(self.access_token)
            # self.set_header('prefer', 'return=representation')
            if "scope" in response_data:
                print("scope of client id: ", response_data["scope"])
            else:
                print("no scope of client id available")
            return response.json()  # Returns the access token and other data
        else:
            print("Response Status Code:", response.status_code)
            print("Response Text:", response.text)
            response.raise_for_status()

    def print_json(self, json_object: dict):
        """
        Prints a JSON object in a readable, formatted way.

        Args:
        json_object (dict): The JSON object to be printed.
        """
        formatted_json = dumps(json_object, indent=2, sort_keys=True)
        print(formatted_json)