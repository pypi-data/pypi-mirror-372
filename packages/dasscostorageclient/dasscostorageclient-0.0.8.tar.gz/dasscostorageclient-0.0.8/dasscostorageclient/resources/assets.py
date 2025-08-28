from typing import List
from .models.specimen import SpecimenModel
from ..utils import *
from pydantic import TypeAdapter, Field, BaseModel
from datetime import datetime
from .models.httpinfo import HTTPInfoModel
from .models.issues import IssueModel
from .models.legality import LegalityModel
from .models.external_publisher import ExternalPublisherModel


class AssetModel(BaseModel):
    asset_locked: bool
    asset_subject: str | None
    audited: bool
    camera_setting_control: str | None
    collection: str
    complete_digitiser_list: list[str]
    digitiser: str | None
    external_publishers: list[ExternalPublisherModel] | None
    file_formats: list[str]
    funding: list[str]
    guid: str = Field(alias='asset_guid')
    http_info: HTTPInfoModel | None = Field(alias='httpInfo')
    institution: str
    internal_status: str
    issues: list[IssueModel] | None
    legality: LegalityModel | None
    make_public: bool
    metadata_source: str | None
    metadata_version: str | None
    # mime_type: str | None
    mos_id: str | None
    multi_specimen: bool
    parent_guids: list[str]
    payload_type: str | None
    asset_pid: str 
    pipeline: str
    push_to_specify: bool
    restricted_access: list[str]
    specify_attachment_remarks: str | None
    specify_attachment_title: str | None
    specimens: list[SpecimenModel]
    status: str
    tags: dict | None


class EventModel(BaseModel):
    user: str | None
    timestamp: str | None
    event: str
    pipeline: str | None


class AssetStatus(BaseModel):
    guid: str = Field(alias='asset_guid')
    parent_guid: list[str]
    error_timestamp: datetime | None
    status: str
    error_message: str | None
    share_allocation_mb: int | None


class Assets:

    def __init__(self, access_token):
        self.access_token = access_token

    def get(self, guid: str):
        """
        Gets the metadata of the given asset

        Args:
            guid (str): The guid of the asset to be retrieved

        Returns:
            An Asset object that contains the metadata
        """
        res = send_request(
            RequestMethod.GET,
            self.access_token,
            f"/v1/assetmetadata/{guid}")

        return {
            'data': AssetModel.model_validate(res.json()),
            'status_code': res.status_code
        }

    def create(self, body: dict, allocation_mb: int):
        """
        Creates a new asset

        Args:
            body (dict): The metadata of the new asset
            allocation_mb (int): The amount of storage allocated for the new asset

        Returns:
            An Asset object that contains the metadata of the created asset
        """
        res = send_request(
            RequestMethod.POST,
            self.access_token,
            f"/v1/assetmetadata?allocation_mb={allocation_mb}",
            body)

        return {
            'data': AssetModel.model_validate(res.json()),
            'status_code': res.status_code
        }

    def update(self, guid: str, body: dict):
        """
        Updates the asset with the given guid

        Args:
            guid (str): The guid of the asset to be updated
            body (dict): The metadata to be updated in the given asset

        Returns:
            An Asset object that contains the metadata of the updated asset
        """
        res = send_request(
            RequestMethod.PUT,
            self.access_token,
            f"/v1/assetmetadata/{guid}",
            body)

        return {
            'data': AssetModel.model_validate(res.json()),
            'status_code': res.status_code
        }
    
    def unlock(self, guid: str):
        """
        Changes the asset locked to false for the given guid

        Args:
            guid (str): The guid of the asset to be unlocked

        Returns:
            The status code of the call along with an empty data field for conistency
        """
        res = send_request(
            RequestMethod.PUT,
            self.access_token,
            f"/v1/assetmetadata/{guid}/unlock"            
        )
        return{
            "data": None,
            "status_code": res.status_code
        }

    def list_events(self, guid: str):
        """
        Lists the events of the given asset

        Args:
            guid (str): The guid of the asset

        Returns:
            A list of Event objects
        """
        res = send_request(
            RequestMethod.GET,
            self.access_token,
            f"/v1/assetmetadata/{guid}/events")

        ta = TypeAdapter(List[EventModel])

        return {
            'data': ta.validate_python(res.json()),
            'status_code': res.status_code
        }

    def get_status(self, guid: str):
        res = send_request(
            RequestMethod.GET,
            self.access_token,
            f"/v1/assets/status/{guid}")

        return {
            'data': AssetStatus.model_validate(res.json()),
            'status_code': res.status_code
        }

    def list_in_progress(self, only_failed=False):
        res = send_request(
            RequestMethod.GET,
            self.access_token,
            f"/v1/assets/inprogress?onlyFailed={only_failed}")

        ta = TypeAdapter(List[AssetStatus])

        return {
            'data': ta.validate_python(res.json()),
            'status_code': res.status_code
        }

    def delete_metadata(self, guid: str):
        """
        Deletes the metadata from ars of an asset

        Args:
            guid (str): The guid of the asset

        Returns:
            Status code of the call        
        """
        res = send_request(
            RequestMethod.DELETE,
            self.access_token,
            f"/v1/assetmetadata/{guid}/deleteMetadata"
        )
        return{
            "data": None,
            "status_code": res.status_code
        }

