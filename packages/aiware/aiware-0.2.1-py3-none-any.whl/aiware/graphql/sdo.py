from typing import List, Type

from aiware.common.sdo import TypedSDO
from aiware.graphql.client_generated.fragments import SDOPage

from aiware.common.schemas import BaseSchema
from aiware.common.utils import not_none


class TypedSDOPage[T: BaseSchema](SDOPage):
    records: List[TypedSDO[T]]  # pyright: ignore[reportIncompatibleVariableOverride]
    count: int  # pyright: ignore[reportIncompatibleVariableOverride]

    @staticmethod
    def from_sdo_page[S: BaseSchema](
        schema_cls: Type[S], sdo_page: SDOPage
    ) -> "TypedSDOPage[S]":
        return TypedSDOPage(
            **{
                **sdo_page.model_dump(),
                "records": [
                    TypedSDO.from_json(
                        schema_cls,
                        schema_id=not_none(record).schemaId,
                        json_data=not_none(record),
                    )
                    for record in not_none(sdo_page.records)
                ],
                "count": sdo_page.count or 0,
            }
        )
