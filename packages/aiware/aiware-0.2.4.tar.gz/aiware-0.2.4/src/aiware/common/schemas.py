from typing import Any, Type, cast
from pydantic import BaseModel, ConfigDict, model_serializer
from datetime import datetime

class JSONData(BaseModel):
    """
    Basic wrapper class to avoid JSONData graphql scalar to be typed as Any.

    See `[tool.ariadne-codegen.scalars.JSONData]` section in pyproject.toml.
    """
    value: Any

    def __init__(self, /, value: Any = None, **data: Any):
        super().__init__(**{
            "value": value or data
        })


    def as_model[T: BaseModel](self, cls: Type[T]) -> T:
        """cast to pydantic type"""
        return cls.model_validate(cast(Any, self.value))

    def as_schema[T: "BaseSchema"](self, cls: Type[T]) -> T:
        """cast to sdo schema type"""
        return self.as_model(cls)
    
    def __repr__(self):
        return f"JSONData({self.value.__repr__()})"
    
    def __str__(self):
        return self.value.__str__()

    @model_serializer
    def ser_model(self) -> Any:
        return self.value


def parse_jsondata(value: Any) -> "JSONData":
    return JSONData(value=value)


def serialize_jsondata(jsondata: "JSONData") -> Any:
    return jsondata.model_dump(mode="json")

def serialize_datetime(dt: datetime) -> str:
    # strip microseconds from ISO 8601
    return dt.isoformat(timespec='milliseconds').replace('+00:00', 'Z')

class BaseSchema(BaseModel):
    model_config = ConfigDict(
        extra='allow',
        json_encoders={datetime: serialize_datetime}
    )

    def as_model[T: BaseModel](self, cls: Type[T]) -> T:
        """cast to pydantic type"""
        return cls.model_validate(self.model_dump(mode="json", serialize_as_any=True))
    
    def dump_sdo(self) -> "JSONData":
        return JSONData(value=self.model_dump(mode="json", exclude_unset=True, exclude_none=True, serialize_as_any=True))
