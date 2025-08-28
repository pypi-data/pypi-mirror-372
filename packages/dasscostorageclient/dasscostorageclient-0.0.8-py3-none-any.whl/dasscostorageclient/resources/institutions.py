from ..core.models import Institution
from ..core.utils import json_to_model
from ..utils import *
from typing import List


class Institutions:

    def __init__(self, access_token):
        self.access_token = access_token

    def list(self):
        """
        Gets a list of all institutions

        Returns:
            A list of institutions
        """
        res = send_request(RequestMethod.GET, self.access_token, "/v1/institutions")
        return json_to_model(List[Institution], res.json())

    def get(self, name: str):
        """
        Gets the institution with the given name

        Args:
            name (str): The name of the institution to be retrieved

        Returns:
             The retrieved institution
        """
        res = send_request(RequestMethod.GET, self.access_token, f"/v1/institutions/{name}")

        if res.status_code == 204:
            raise Exception(f"The institution {name} does not exist")

        return json_to_model(Institution, res.json())

    def create(self, name: str):
        """
          Creates an institution with the given name

          Args:
              name (str): The name of the institution to be created

          Returns:
              The created institution
        """
        body = {
            'name': name,
        }
        res = send_request(RequestMethod.POST, self.access_token, "/v1/institutions", body)
        return json_to_model(Institution, res.json())
