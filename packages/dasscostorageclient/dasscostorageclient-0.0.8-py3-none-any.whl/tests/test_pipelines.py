import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from dasscostorageclient.core.models import Pipeline
from tests.dassco_test_client import mockClient, base_url

API_URL = f"{base_url}/ars/api"


def test_can_list_pipelines(requests_mock):
    institution_name = "test-institution"
    requests_mock.get(API_URL + f"/v1/institutions/{institution_name}/pipelines",
                      json=[{'name': 'test-pipeline', 'institution': institution_name}])
    pipelines = mockClient.pipelines.list(institution_name)
    assert pipelines == [Pipeline(name="test-pipeline", institution=institution_name)]


def test_can_create_pipeline(requests_mock):
    institution_name = "test-institution"
    pipeline_name = 'new-pipeline'
    requests_mock.post(API_URL + f"/v1/institutions/{institution_name}/pipelines",
                       json={'name': pipeline_name, 'institution': institution_name})
    pip = mockClient.pipelines.create(institution_name, pipeline_name)
    assert pip.name == pipeline_name
    assert pip.institution == institution_name
