from pydantic import BaseModel

class LegalityModel(BaseModel):
    copyright: str | None
    license: str | None
    credit: str | None