from typing import List

from ..core.enums import WorkstationStatus
from ..core.models import Workstation
from ..core.utils import json_to_model
from ..utils import *


class Workstations:

    def __init__(self, access_token):
        self.access_token = access_token

    def list(self, institution_name: str):
        """
        Gets a list of all workstations in a given institution

        Args:
            institution_name (str): The name of the given institution

        Returns:
            A list of Workstation objects
        """
        res = send_request(RequestMethod.GET, self.access_token, f"/v1/institutions/{institution_name}/workstations")
        return json_to_model(List[Workstation], res.json())

    def create(self, institution_name: str, workstation_name: str, status: WorkstationStatus = WorkstationStatus.IN_SERVICE):
        """
           Creates a workstation in a given institution

           Args:
               institution_name (str): The name of the given institution
               workstation_name (str): The name of the workstation to be created
               status (WorkstationStatus): The status of the workstation to be created. The options are: IN_SERVICE or OUT_OF_SERVICE

           Returns:
               The created Workstation object
        """
        body = {
            'name': workstation_name,
            'status': status.value
        }
        res = send_request(RequestMethod.POST, self.access_token, f"/v1/institutions/{institution_name}/workstations", body)
        return json_to_model(Workstation, res.json())

    def update(self, institution_name: str, workstation_name: str, body: dict):
        """
        Updates a workstation in a given institution

        Args:
            institution_name (str): The name of the given institution
            workstation_name (str): The name of the workstation to be updated
            body (dict): The fields to be updated in the given workstation

        Returns:
            Currently returns empty data as a 204 (No Content) status code is returned by the API
        """
        return send_request(RequestMethod.PUT, self.access_token,
                            f"/v1/institutions/{institution_name}/workstations/{workstation_name}", body)
