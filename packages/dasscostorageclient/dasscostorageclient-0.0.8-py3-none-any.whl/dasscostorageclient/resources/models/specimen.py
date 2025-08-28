from pydantic import BaseModel, Field

class SpecimenModel(BaseModel):
    institution: str | None
    collection: str | None
    barcode: str
    pid: str = Field(alias='specimen_pid')
    preparation_types: list[str]
    asset_preparation_type: str | None
    specimen_id: int | None
    specify_collection_object_attachment_id: int | None
    asset_detached: bool

