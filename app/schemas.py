from datetime import datetime

from pydantic import BaseModel


class LinkCreate(BaseModel):
    original_url : str
    custom_alias: str | None = None
    expires_at : datetime | None = None

class LinkResponse(LinkCreate):
    short_code : str
    created_at : datetime
    is_active: bool