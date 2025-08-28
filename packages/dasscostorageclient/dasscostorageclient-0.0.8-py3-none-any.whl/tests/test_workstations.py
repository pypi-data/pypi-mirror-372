import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from dasscostorageclient.core.enums import WorkstationStatus
from dasscostorageclient.core.models import Workstation
from tests.dassco_test_client import mockClient, base_url

API_URL = f"{base_url}/ars/api"


def test_can_create_workstation(requests_mock):
    institution_name = "test-institution"
    workstation_name = 'ws-01'
    status = WorkstationStatus.IN_SERVICE

    requests_mock.post(API_URL + f"/v1/institutions/{institution_name}/workstations",
                       json={'name': workstation_name, 'status': status.value, 'institution': institution_name})

    ws = mockClient.workstations.create(institution_name, workstation_name, status)

    assert ws.name == workstation_name


def test_can_list_workstations(requests_mock):
    institution_name = "test-institution"
    workstation_name = 'ws-01'
    status = WorkstationStatus.IN_SERVICE

    requests_mock.get(API_URL + f"/v1/institutions/{institution_name}/workstations",
                       json=[{'name': workstation_name, 'status': status.value, 'institution': institution_name}])

    workstations = mockClient.workstations.list(institution_name)

    assert workstations == [Workstation(name=workstation_name, status=status, institution=institution_name)]


# def test_can_update_workstation():
#     institution_name = "test-institution"
#     workstation_name = "ti-ws-01"
#     body = {
#         'name': workstation_name,
#         'status': 'IN_SERVICE'
#     }
#     res = client.workstations.update(institution_name, workstation_name, body)
#     assert res.status_code == 204
