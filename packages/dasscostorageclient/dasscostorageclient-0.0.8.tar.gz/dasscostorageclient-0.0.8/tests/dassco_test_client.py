import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

import requests_mock
from dotenv import load_dotenv
from dasscostorageclient.dassco_storage_client import DaSSCoStorageClient

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
base_url = "https://biovault.dassco.dk"

client = DaSSCoStorageClient(client_id, client_secret)

TOKEN_URL = base_url + "/keycloak/realms/dassco/protocol/openid-connect/token"

with requests_mock.Mocker() as m:
    m.post(TOKEN_URL, json={'access_token': '123'})
    mockClient = DaSSCoStorageClient('client_id', 'client_secret')
    
