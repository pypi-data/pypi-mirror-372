from dotenv import load_dotenv
import os

load_dotenv()

DASSCO_BASE_URL = os.getenv("DASSCO_BASE_URL") or "https://biovault.dassco.dk"
DASSCO_TOKEN_PATH = os.getenv("DASSCO_TOKEN_PATH") or "/keycloak/realms/dassco/protocol/openid-connect/token"

