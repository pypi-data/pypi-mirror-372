# DaSSCo Storage Client

A simple client library used to call the DaSSco Storage API


### Installation

Requires Python 3.10+

```
python -m pip install dasscostorageclient 
```


### Getting started

```
from dasscostorageclient import DaSSCoStorageClient

client_id = 'CLIENT_ID'
client_secret = 'CLIENT_SECRET'

client = DaSSCoStorageClient(client_id, client_secret)

institutions = client.institutions.get()

```
