import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from .dassco_test_client import client
import pytest
import time


ASSET_GUID = "dassco_storageclient_test_fileproxy"
INSTITUTION_NAME = "test-institution"
COLLECTION_NAME = "test-collection"
FILE_NAME = "requirements.txt"

@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown():
    # before
    body = {
        "asset_guid": ASSET_GUID,
        "asset_pid": ASSET_GUID,
        "institution": INSTITUTION_NAME,
        "pipeline": "test-pipeline",
        "collection": COLLECTION_NAME,
        "workstation": "test-workstation",
        "status": "WORKING_COPY",
        "digitiser": "Anders And",
        "issues": []
    }
    
    try:
        res = client.assets.create(body, 1)
        if res.get("status_code") != 200:
            print("Asset may already exist. Continuing with tests.")
    except Exception as e:
        print(f"Warning: asset creation failed with exception: {e}")
    
    # run tests
    yield

    # after
    
    try:
        client.file_proxy.delete_share(INSTITUTION_NAME, COLLECTION_NAME, ASSET_GUID, ["Test user"], 1)
        client.assets.delete_metadata(ASSET_GUID)
    except Exception as e:
        print(f"Failed to clean up: {e}")
    
        
@pytest.mark.order(1)
def test_delete_share():
    res = client.file_proxy.delete_share(INSTITUTION_NAME, COLLECTION_NAME, ASSET_GUID, ["Test user"], 1)
    assert res.status_code == 200


@pytest.mark.order(2)
def test_open_share():
    res = client.file_proxy.open_share(INSTITUTION_NAME, COLLECTION_NAME, ASSET_GUID, ["Test user"], 1)
    assert res.status_code == 200


@pytest.mark.order(3)
def test_upload_file():
    res = client.file_proxy.upload(FILE_NAME, INSTITUTION_NAME, COLLECTION_NAME, ASSET_GUID, 1)
    assert res.status_code == 200
    

@pytest.mark.order(4)
def test_get_file():
    res = client.file_proxy.get_file(INSTITUTION_NAME, COLLECTION_NAME, ASSET_GUID, FILE_NAME)
    file = open(FILE_NAME, 'rb')
    file_data = file.read()
    file.close()
    assert res.status_code == 200
    assert res.content == file_data


@pytest.mark.order(5)
def test_list_available_files():
    res = client.file_proxy.list_available_files(ASSET_GUID)
    assert res.status_code == 200


@pytest.mark.order(6)
def test_list_file_info():
    res = client.file_proxy.list_file_info(ASSET_GUID)
    assert res.status_code == 200


@pytest.mark.order(7)
def test_delete_file():
    res = client.file_proxy.delete_file(INSTITUTION_NAME, COLLECTION_NAME, ASSET_GUID, FILE_NAME)
    assert res.status_code == 204
