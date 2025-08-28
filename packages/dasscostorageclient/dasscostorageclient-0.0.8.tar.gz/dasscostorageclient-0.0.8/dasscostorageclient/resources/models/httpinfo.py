import pydantic


class HTTPInfoModel(pydantic.BaseModel):
    path: str
    hostname: str
    total_storage_mb: int
    cache_storage_mb: int
    remaining_storage_mb: int
    allocated_storage_mb: int
    allocation_status_text: str | None
    http_allocation_status: str
