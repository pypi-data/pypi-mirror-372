from aiware.common.schemas import BaseSchema
from aiware.common.sdo import TypedSDO
from aiware.search.async_client import AsyncAiwareSearch
from aiware.search.models import (
    SdoSliceSearchResult,
    SearchRequestFilter,
    SearchSDOsRequest,
)
from aiware.search._models_generated import SearchResultsPage


from pydantic import Field


from typing import Annotated, Any, Dict, List, Optional, Type


class TypedSdoSliceSearchResult[T: BaseSchema](SearchResultsPage):
    results: List[TypedSDO[T]] = Field(default_factory=lambda: [])

    @staticmethod
    def from_sdo_search_result[S: BaseSchema](
        schema_cls: Type[S], schema_id: str, search_result: SdoSliceSearchResult
    ) -> "TypedSdoSliceSearchResult[S]":
        search_result_dict = search_result.model_dump(
            mode="python"
        )
        search_result_dict.pop("results", [])

        return TypedSdoSliceSearchResult.model_validate(
            {
                **search_result_dict,
                "results": [
                    TypedSDO.from_json(
                        schema_cls=schema_cls, schema_id=schema_id, json_data=result
                    )
                    for result in search_result.results or []
                ],
            }
        )


async def search_typed_sdos[S: BaseSchema](
    aiware: AsyncAiwareSearch,
    schema_cls: Type[S],
    schema_id: str,
    query: SearchRequestFilter,
    sort: Annotated[
        Optional[List[Dict[str, Any]]],
        Field(
            description="See https://github.com/veritone/core-search-server#sort-statements."
        ),
    ] = None,
    offset: Annotated[
        Optional[float],
        Field(
            description="Used for paging, indicates the zero-base index of the first result. If not provided, defaults to 0."
        ),
    ] = None,
    limit: Annotated[
        Optional[float],
        Field(
            description="Maximum of results to return. Cannot exceed 100. Defaults to 10."
        ),
    ] = None,
) -> TypedSdoSliceSearchResult[S]:
    untyped_search_result = await aiware.search_sdos(
        SearchSDOsRequest(
            index=["mine"],
            type=schema_id,
            query=query,
            sort=sort,
            offset=offset,
            limit=limit,
        )
    )

    return TypedSdoSliceSearchResult.from_sdo_search_result(
        schema_cls=schema_cls, schema_id=schema_id, search_result=untyped_search_result
    )
