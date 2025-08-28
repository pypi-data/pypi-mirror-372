import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from dasscostorageclient.core.models import Collection
from tests.dassco_test_client import mockClient, base_url

API_URL = f"{base_url}/ars/api"


def test_can_list_collections(requests_mock):
    institution_name = "test-institution"
    requests_mock.get(API_URL + f"/v1/institutions/{institution_name}/collections",
                      json=[{'name': 'test-collection', 'institution': institution_name}])
    institutions = mockClient.collections.list(institution_name)
    assert institutions == [Collection(name="test-collection", institution=institution_name)]


def test_can_create_collection(requests_mock):
    institution_name = "test-institution"
    collection_name = 'new-collection'
    requests_mock.post(API_URL + f"/v1/institutions/{institution_name}/collections",
                       json={'name': collection_name, 'institution': institution_name})
    collection = mockClient.collections.create(institution_name, collection_name)
    assert collection.name == collection_name
    assert collection.institution == institution_name
