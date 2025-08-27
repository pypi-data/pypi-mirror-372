from typing import Dict, Optional, Self, cast, Protocol
import httpx
from aiware.common.auth import AbstractTokenAuth
from aiware.search.models import SdoSliceSearchResult, SearchSDOsRequest, VectorSearchRequest
from aiware.search._models_generated import SearchRequest, SliceSearchResult, VectorSearchResults

class AsyncAiwareSearch:
    def __init__(
        self,
        url: str = "",
        auth: Optional[AbstractTokenAuth] = None,
        headers: Optional[Dict[str, str]] = None,
        http_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self.url = url
        self.auth = auth
        self.headers = headers
        self.http_client = http_client if http_client else httpx.AsyncClient(headers=headers, auth=auth)

    async def __aenter__(self: Self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: object,
        exc_val: object,
        exc_tb: object,
    ) -> None:
        await self.http_client.aclose()

    async def search_media(self, request: SearchRequest) -> SliceSearchResult:
        data = request.model_dump(mode='json', exclude_unset=True)
        response = await self.http_client.post("/", json=data)
        response.raise_for_status()

        return SliceSearchResult.model_validate_json(response.text)

    async def search_sdos(self, request: SearchSDOsRequest) -> SdoSliceSearchResult:
        return (await self.search_media(request=cast(SearchRequest, request))).as_model(SdoSliceSearchResult)

    async def vector_search(self, request: VectorSearchRequest) -> VectorSearchResults:
        data = request.model_dump(mode='json', exclude_unset=True)
        response = await self.http_client.post("/vector", json=data)
        response.raise_for_status()

        return VectorSearchResults.model_validate_json(response.text)

class AsyncAiwareSearchFactory[S: AsyncAiwareSearch](Protocol):
    def __call__(self, endpoint: str, auth: Optional[AbstractTokenAuth]) -> S:
        ...
