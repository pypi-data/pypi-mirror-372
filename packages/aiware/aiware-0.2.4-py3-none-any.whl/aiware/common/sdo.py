from pydantic import BaseModel
from aiware.common.schemas import BaseSchema, JSONData


import uuid
from datetime import datetime
from typing import Any, Optional, Type, cast
from uuid import UUID


class TypedSDO[T: BaseSchema](BaseModel):
    """
    A representation of SDO with stricter typing and reasonable null handling
    """

    schema_cls: Type[T]

    id: str
    schemaId: str
    createdDateTime: Optional[datetime]
    modifiedDateTime: Optional[datetime]
    data: T  # pyright: ignore[reportIncompatibleVariableOverride]

    @staticmethod
    def from_json[S: BaseSchema](
        schema_cls: Type[S], schema_id: str, json_data: BaseModel
    ) -> "TypedSDO[S]":
        value = json_data.model_dump(mode="python", serialize_as_any=True)

        id = value.pop("id", None)
        createdDateTime: str | None = value.pop("createdDateTime", None)
        modifiedDateTime: str | None = value.pop("modifiedDateTime", None)

        data = value["data"] if "data" in value else value

        return TypedSDO.model_validate(
            {
                "schema_cls": schema_cls,
                "id": id,
                "schemaId": schema_id,
                "createdDateTime": createdDateTime,
                "modifiedDateTime": modifiedDateTime,
                "data": JSONData(value=data).as_schema(schema_cls),
            }
        )

    @staticmethod
    def new[S: BaseSchema](
        schema_id: str,
        data: S,
        id: Optional[UUID] = None,
        created_datetime: Optional[datetime] = None,
        modified_datetime: Optional[datetime] = None,
    ) -> "TypedSDO[S]":
        return TypedSDO(
            id=(id or uuid.uuid4()).__str__(),
            createdDateTime=created_datetime or datetime.now(),
            modifiedDateTime=modified_datetime,
            schemaId=schema_id,
            schema_cls=data.__class__,
            data=data,
        )


