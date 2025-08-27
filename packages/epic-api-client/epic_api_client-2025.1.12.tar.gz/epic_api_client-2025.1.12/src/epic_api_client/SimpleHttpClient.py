#    ____   # -------------------------------------------------- #
#   | ^  |  # SimpleHttpClient for AUMC                          #
#   \  --   # o.m.vandermeer@amsterdamumc.nl                     #
# \_| ﬤ| ﬤ  # If you like this code, treat him to a coffee! ;)   #
#   |_)_)   # -------------------------------------------------- #

# SimpleHttpClient is needed to make HTTP requests to an API endpoint

import requests
import requests_unixsocket
import json as json_module  # Import json with a different name to avoid parameter conflicts
import re
from urllib.parse import urlparse, urlunparse
from xml.dom.minidom import parseString


class SimpleHttpClient:
    def __init__(
        self,
        base_url: str = None,
        headers: dict = None,
        use_unix_socket: bool = False,
        socket_path: str = None,
        debug_mode: bool = False,
    ) -> None:
        self.base_url = base_url
        self.headers = headers if headers is not None else {}
        self.use_unix_socket = use_unix_socket
        self.socket_path = socket_path
        self.debug_mode = debug_mode
        self.dino = "Mrauw!"
        if self.use_unix_socket and not self.socket_path:
            raise ValueError(
                "Socket path must be provided when use_unix_socket is True"
            )

    def set_header(self, key: str, value: str) -> None:
        self.headers[key] = value

    def get(self, endpoint: str, params: dict = None, extra_headers: dict = {}) -> dict:
        return self._request(
            "GET", endpoint, params=params, extra_headers=extra_headers
        )

    def post(
        self,
        endpoint: str,
        data: dict = None,
        json: dict = None,
        extra_headers: dict = {},
    ) -> dict:
        return self._request(
            "POST", endpoint, data=data, json=json, extra_headers=extra_headers
        )

    def put(
        self,
        endpoint: str,
        data: dict = None,
        json: dict = None,
        extra_headers: dict = {},
    ) -> dict:
        return self._request(
            "PUT", endpoint, data=data, json=json, extra_headers=extra_headers
        )

    def delete(self, endpoint: str, extra_headers: dict = {}) -> dict:
        return self._request("DELETE", endpoint, extra_headers=extra_headers)

    def patch(
        self,
        endpoint: str,
        data: dict = None,
        json: dict = None,
        extra_headers: dict = {},
    ) -> dict:
        return self._request(
            "PATCH", endpoint, data=data, json=json, extra_headers=extra_headers
        )
    
    def _sanitize_headers(self, headers: dict) -> dict:
        """Sanitize sensitive header information for debug output."""
        if not headers:
            return headers
            
        sanitized = headers.copy()
        
        # Sanitize Authorization header (typically bearer tokens)
        if 'Authorization' in sanitized:
            sanitized['Authorization'] = "<bearer token>"
            
        # Sanitize Epic-Client-ID header
        if 'Epic-Client-ID' in sanitized:
            client_id = sanitized['Epic-Client-ID']
            # Extract the last part after the last dash
            parts = client_id.split('-')
            if len(parts) > 1:
                last_part = parts[-1]
                sanitized['Epic-Client-ID'] = f"<rest of client id>-{last_part}"
            else:
                sanitized['Epic-Client-ID'] = "<client id>"
                
        return sanitized

    def _request(
        self,
        method: str,
        endpoint: str,
        params: dict = None,
        data: dict = None,
        json: dict = None,
        extra_headers: dict = {},
    ) -> dict:
        url = self._build_url(endpoint)
        headers = {**self.headers, **extra_headers}
        
        if self.debug_mode:
            print(f"\n{'='*50}")
            print(f"=== HTTP REQUEST ===")
            print(f"{'='*50}")
            print(f"\n> {method} {url}")
            
            # Sanitize headers before printing
            sanitized_headers = self._sanitize_headers(headers)
            print("\n> Headers:")
            print(json_module.dumps(sanitized_headers, indent=4))
            
            if params:
                print("\n> Params:")
                print(json_module.dumps(params, indent=4))
                
            if data:
                print("\n> Data:")
                print(json_module.dumps(data, indent=4))
                
            if json:
                print("\n> JSON:")
                print(json_module.dumps(json, indent=4))
            
            print(f"\n{'='*50}\n")
            
        if self.use_unix_socket:
            return self._request_unix_socket(
                method, url, params=params, data=data, json=json, headers=headers
            )
        else:
            response = requests.request(
                method, url, headers=headers, params=params, data=data, json=json
            )
            
            if self.debug_mode:
                print(f"\n{'='*50}")
                print(f"=== HTTP RESPONSE ===")
                print(f"{'='*50}")
                print(f"\n> Status: {response.status_code}")
                
                # Sanitize response headers before printing
                sanitized_resp_headers = self._sanitize_headers(dict(response.headers))
                print("\n> Headers:")
                print(json_module.dumps(sanitized_resp_headers, indent=4))
                
                print("\n> Content:")
                # Try to format JSON content if possible
                try:
                    content_json = response.json()
                    print(json_module.dumps(content_json, indent=4))
                except ValueError:
                    # If not JSON, just print the text
                    print(response.text)
                print(f"\n{'='*50}\n")
                
            return self._handle_response(response)

    def _request_unix_socket(self, method: str, url: str, **kwargs) -> dict:
        parsed = urlparse(url)
        new_url = urlunparse(
            (
                "http+unix",
                self.socket_path,  # use Unix socket path
                parsed.path,
                parsed.params,
                parsed.query,
                parsed.fragment,
            )
        )
        if "headers" not in kwargs:
            kwargs["headers"] = {}
        kwargs["headers"]["host"] = parsed.netloc

        session = requests_unixsocket.Session()
        response = session.request(method=method, url=new_url, **kwargs)
        return self._handle_response(response)

    def _build_url(self, endpoint: str) -> str:
        if self.base_url:
            return f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        return endpoint

    def _handle_response(self, response: requests.Response) -> dict:
        try:
            response.raise_for_status()  # Raise an HTTPError on bad responses (4xx and 5xx)
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred: {e}")
            print("Response Text:", response.text)
            return None
        content_type = response.headers.get("Content-Type", "")
        if "application/xml" in content_type or "text/xml" in content_type:
            return self._pretty_print_xml(response.text)
        try:
            return response.json()  # Try to return JSON if possible
        except ValueError:
            return response.text  # Fallback to text if no JSON

    def _pretty_print_xml(self, xml_str: str) -> str:
        dom = parseString(xml_str)
        return dom.toprettyxml()
