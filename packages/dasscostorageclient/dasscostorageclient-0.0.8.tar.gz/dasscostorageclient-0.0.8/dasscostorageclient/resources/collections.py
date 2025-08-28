from typing import List

from ..core.models import Collection
from ..core.utils import json_to_model
from ..utils import *


class Collections:

    def __init__(self, access_token):
        self.access_token = access_token

    def list(self, institution_name: str):
        """
        Gets a list of all collections in a given institution

        Args:
            institution_name (str): The name of the given institution

        Returns:
            A list of collections
        """
        res = send_request(RequestMethod.GET, self.access_token, f"/v1/institutions/{institution_name}/collections")
        return json_to_model(List[Collection], res.json())

    def create(self, institution_name: str, collection_name: str):
        """
          Creates a collection in a given institution

          Args:
              institution_name (str): The name of the institution to create the collection in
              collection_name (str): The name of the collection to be created

          Returns:
              The created collection
        """
        body = {
            'name': collection_name,
        }
        res = send_request(RequestMethod.POST, self.access_token, f"/v1/institutions/{institution_name}/collections", body)
        return json_to_model(Collection, res.json())
