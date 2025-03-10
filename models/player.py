# models/player.py
from .base import MongoBaseModel
from datetime import datetime
from pydantic import Field, constr

class Player(MongoBaseModel):
    name: constr(min_length=1, max_length=100, strip_whitespace=True) = Field() # type: ignore
    is_online: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
