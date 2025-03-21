from bson import ObjectId
from pydantic import BaseModel, Field
# from pydantic.json import ENCODERS_BY_TYPE
from typing import Any

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: Any):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

# ENCODERS_BY_TYPE[ObjectId] = str