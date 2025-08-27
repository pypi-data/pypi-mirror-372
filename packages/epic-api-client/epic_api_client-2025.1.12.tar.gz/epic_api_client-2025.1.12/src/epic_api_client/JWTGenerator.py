#    ____   # -------------------------------------------------- #
#   | ^  |  # JWT Generator for AUMC	                         #
#   \  --   # o.m.vandermeer@amsterdamumc.nl	                 #
# \_| ﬤ| ﬤ  # If you like this code, treat him to a coffee! ;)	 #
#   |_)_)   # -------------------------------------------------- #

# JWT Generator is needed to generate JWT tokens for authentication purposes
import jwt
import time
import uuid
from typing import Optional
from cryptography.hazmat.primitives.serialization import pkcs12

class JWTGenerator:
    def __init__(self, pfx_file_path: str, pfx_password: str, alg: str = "RS384", kid: Optional[str] = None, jku: Optional[str] = None):
        self.private_key = self._load_private_key_from_pfx(pfx_file_path, pfx_password)
        self.alg = alg
        self.kid = kid
        self.jku = jku
        self.dino = "Mrauw!"
        
    def _load_private_key_from_pfx(self, pfx_file_path: str, pfx_password: str):
        with open(pfx_file_path, 'rb') as pfx_file:
            pfx_data = pfx_file.read()
        private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(pfx_data, pfx_password.encode())
        return private_key

    def create_jwt(self, client_id: str, aud: str):
        # Header
        headers = {
            "alg": self.alg,
            "typ": "JWT"
        }
        if self.kid:
            headers["kid"] = self.kid
        if self.jku:
            headers["jku"] = self.jku

        # Payload
        now = int(time.time())
        exp = now + 300  # JWT expiration time (5 minutes)
        payload = {
            "iss": client_id,
            "sub": client_id,
            "aud": aud,
            "jti": str(uuid.uuid4()),
            "exp": exp,
            "nbf": now,
            "iat": now
        }

        # Generate JWT
        token = jwt.encode(payload, self.private_key, algorithm=self.alg, headers=headers)
        return token

