import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from dasscostorageclient.core.models import Institution
from tests.dassco_test_client import mockClient, base_url

API_URL = f"{base_url}/ars/api"


def test_can_create_institution(requests_mock):
    institution_name = 'new-institution'
    requests_mock.post(API_URL + "/v1/institutions", json={'name': institution_name})
    inst = mockClient.institutions.create(institution_name)
    assert inst.name == institution_name


def test_can_list_institutions(requests_mock):
    requests_mock.get(API_URL + "/v1/institutions", json=[{'name': 'test-institution'}, {'name': 'ld'}])
    institutions = mockClient.institutions.list()
    assert institutions == [Institution(name="test-institution"), Institution(name='ld')]


def test_can_call_get_institution(requests_mock):
    institution_name = "test-institution"
    requests_mock.get(API_URL + f"/v1/institutions/{institution_name}", json={'name': institution_name})
    inst = mockClient.institutions.get(institution_name)
    assert inst.name == institution_name
