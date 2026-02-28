from pydantic import BaseModel, ConfigDict, HttpUrl
from datetime import datetime


class LinkCreate(BaseModel):
    original_url: HttpUrl

class LinkResponse(BaseModel):
    id: int
    original_url: str
    short_code: str
    click_count: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
