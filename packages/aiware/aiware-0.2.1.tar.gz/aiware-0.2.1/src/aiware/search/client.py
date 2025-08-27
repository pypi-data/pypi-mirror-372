from typing import Dict, Optional, Self, cast, Protocol
import httpx
from aiware.common.auth import AbstractTokenAuth
from aiware.search.models import SdoSliceSearchResult, SearchSDOsRequest, VectorSearchRequest
from aiware.search._models_generated import SearchRequest, SliceSearchResult, VectorSearchResults

class AiwareSearch:
    def __init__(
        self,
        url: str = "",
        auth: Optional[AbstractTokenAuth] = None,
        headers: Optional[Dict[str, str]] = None,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        self.url = url
        self.auth = auth
        self.headers = headers
        self.http_client = http_client if http_client else httpx.Client(headers=headers, auth=auth)

    def __enter__(self: Self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: object,
        exc_val: object,
        exc_tb: object,
    ) -> None:
        self.http_client.close()

    def search_media(self, request: SearchRequest) -> SliceSearchResult:
        data = request.model_dump(mode='json', exclude_unset=True)
        response = self.http_client.post("/", json=data)
        response.raise_for_status()

        return SliceSearchResult.model_validate_json(response.text)

    def search_sdos(self, request: SearchSDOsRequest) -> SdoSliceSearchResult:
        return (self.search_media(request=cast(SearchRequest, request))).as_model(SdoSliceSearchResult)

    def vector_search(self, request: VectorSearchRequest) -> VectorSearchResults:
        data = request.model_dump(mode='json', exclude_unset=True)
        response = self.http_client.post("/vector", json=data)
        response.raise_for_status()

        return VectorSearchResults.model_validate_json(response.text)

class AiwareSearchFactory[S: AiwareSearch](Protocol):
    def __call__(self, endpoint: str, auth: Optional[AbstractTokenAuth]) -> S:
        ...
