from pydantic import BaseModel
from datetime import datetime

class ExternalPublisherModel(BaseModel):
    name: str