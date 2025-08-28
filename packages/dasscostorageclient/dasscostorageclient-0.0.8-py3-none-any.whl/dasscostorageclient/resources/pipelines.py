from typing import List

from ..core.models import Pipeline
from ..core.utils import json_to_model
from ..utils import *


class Pipelines:

    def __init__(self, access_token):
        self.access_token = access_token

    def list(self, institution_name: str):
        """
        Gets a list of all pipelines in a given institution

        Args:
            institution_name (str): The name of the given institution

        Returns:
            A list pipelines
        """
        res = send_request(RequestMethod.GET, self.access_token, f"/v1/institutions/{institution_name}/pipelines")
        return json_to_model(List[Pipeline], res.json())

    def create(self, institution_name: str, pipeline_name: str):
        """
          Creates a pipeline in a given institution

          Args:
              institution_name (str): The name of the institution to create the pipeline in
              pipeline_name (str): The name of the pipeline to be created

         Returns:
            The created pipeline
        """
        body = {
            'name': pipeline_name,
        }
        res = send_request(RequestMethod.POST, self.access_token, f"/v1/institutions/{institution_name}/pipelines", body)
        return json_to_model(Pipeline, res.json())
