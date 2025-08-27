from enum import Enum
from typing import Annotated, Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field
from aiware.common.schemas import BaseSchema, JSONData
from aiware.search._models_generated import (
    SearchRequest,
    SearchAggregationRequest,
    SearchScrollRequest,
    SearchAutoCompleteRequest,
    SearchMentionsRequest,
    DetailedError,
    SearchResultsPage,
    SearchAggregateResults,
    TdoMetadata,
    TdoSliceMetadata,
    TdoResult,
    TdoSliceResult,
    SliceResult,
    TdoSearchResult,
    TdoMetadataSearchResult,
    SliceSearchResult,
    CountSearchResult,
    AutocompleteFieldResult,
    AutocompleteFieldResults,
    AutocompleteResult,
    TextSnippet,
    MentionResult,
    MentionsSearchResults,
    AuditLogSearchRequest,
    AuditLogResult,
    VectorSearchRequestSemanticSearchVectorSimilarity,
    VectorSearchRequestSemanticSearchTextSimilarity,
    VectorSearchRequestSemanticSearchImageSimilarity,
    VectorSearchRequestSemanticSearchAudioSimilarity,
    VectorSearchRequestSemanticSearchRescoringInputRescoringOperation,
    VectorSearchRequestSemanticSearchRescoringInputMatchType,
    VectorSearchRequestSemanticSearchRescoringInput,
    VectorSearchRequestSemanticSearchOptimization,
    VectorSearchRequestSemanticSearch,
    VectorSearchRequestFilterOperator,
    Components,
    VectorSearchResultsResultMetaData,
    VectorSearchResultsResultSery,
    Filter,
    Error,
    AuditLogSearchResults,
    VectorSearchRequestFilter as BaseVectorSearchRequestFilter
)

# overrides

class SearchRequestFilterOperator(Enum):
    query_string = 'query_string'
    term = 'term'
    terms = 'terms'
    range = 'range'
    exists = 'exists'
    or_ = 'or'
    and_ = 'and'

class SearchRequestFilter(BaseModel):
    operator: Optional[SearchRequestFilterOperator] = None
    conditions: Optional[List["SearchRequestFilter"]] = None
    field: Optional[str] = None
    value: Optional[str] = None
    gt: Optional[str] = None
    gte: Optional[str] = None
    lt: Optional[str] = None
    lte: Optional[str] = None
    not_: Annotated[Optional[bool], Field(alias='not')] = None

SearchRequestFilter.model_rebuild()

class BaseRequest(BaseSchema):
    sort: Annotated[
        Optional[List[Dict[str, Any]]],
        Field(
            description='See https://github.com/veritone/core-search-server#sort-statements.'
        ),
    ] = None
    offset: Annotated[
        Optional[float],
        Field(
            description='Used for paging, indicates the zero-base index of the first result. If not provided, defaults to 0.'
        ),
    ] = None
    limit: Annotated[
        Optional[float],
        Field(
            description='Maxiumum of results to return. Cannot exceed 100. Defaults to 10.'
        ),
    ] = None

class SearchSDOsRequest(BaseRequest):
    index: Annotated[
        List[str],
        Field(
            description='There are two pre-defined indexes called "global" and "mine", where "global" is the global index while "mine" is the index associated with your application.'
        ),
    ]
    type: Annotated[str, Field(description="SDO schema id")]
    query: Annotated[
        SearchRequestFilter,
        Field(
            description='See https://github.com/veritone/core-search-server#query-statements.'
        ),
    ]

class VectorSearchRequestFilter(BaseVectorSearchRequestFilter):
    operator: Optional[VectorSearchRequestFilterOperator] = None
    conditions: Optional[List["VectorSearchRequestFilter"]] = None # pyright: ignore[reportIncompatibleVariableOverride]
    field: Optional[str] = None
    value: Optional[str] = None
    gt: Optional[str] = None
    gte: Optional[str] = None
    lt: Optional[str] = None
    lte: Optional[str] = None
    not_: Annotated[Optional[bool], Field(alias='not')] = None

VectorSearchRequestFilter.model_rebuild()

class VectorSearchRequest(BaseRequest):
    semanticSearch: Optional[VectorSearchRequestSemanticSearch] = None
    filters: Optional[List[VectorSearchRequestFilter]] = None
    select: List[str] # this is currently required

class VectorSearchResultsResultVector(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    score: float
    similarity: float

class VectorSearchResultsResult(BaseModel):
    model_config = ConfigDict(extra='allow')

    score: float
    recordingId: str # pyright: ignore[reportGeneralTypeIssues, reportIncompatibleVariableOverride]
    vectors: List[VectorSearchResultsResultVector]

class VectorSearchResults(BaseModel):
    results: Optional[List[VectorSearchResultsResult]] = None
    totalCount: Optional[float] = None

class SdoSliceSearchResult(SearchResultsPage):
    results: Optional[List[JSONData]] = None


__all__ = [
    "SearchRequest",
    "SearchAggregationRequest",
    "SearchScrollRequest",
    "SearchAutoCompleteRequest",
    "SearchMentionsRequest",
    "DetailedError",
    "SearchResultsPage",
    "SearchAggregateResults",
    "TdoMetadata",
    "TdoSliceMetadata",
    "TdoResult",
    "TdoSliceResult",
    "SliceResult",
    "TdoSearchResult",
    "TdoMetadataSearchResult",
    "SliceSearchResult",
    "CountSearchResult",
    "AutocompleteFieldResult",
    "AutocompleteFieldResults",
    "AutocompleteResult",
    "TextSnippet",
    "MentionResult",
    "MentionsSearchResults",
    "AuditLogSearchRequest",
    "AuditLogResult",
    "VectorSearchRequestSemanticSearchVectorSimilarity",
    "VectorSearchRequestSemanticSearchTextSimilarity",
    "VectorSearchRequestSemanticSearchImageSimilarity",
    "VectorSearchRequestSemanticSearchAudioSimilarity",
    "VectorSearchRequestSemanticSearchRescoringInputRescoringOperation",
    "VectorSearchRequestSemanticSearchRescoringInputMatchType",
    "VectorSearchRequestSemanticSearchRescoringInput",
    "VectorSearchRequestSemanticSearchOptimization",
    "VectorSearchRequestSemanticSearch",
    "VectorSearchRequestFilterOperator",
    "Components",
    "VectorSearchResultsResultMetaData",
    "VectorSearchResultsResultSery",
    "Filter",
    "Error",
    "AuditLogSearchResults",
    # overrides
    "SearchRequestFilterOperator",
    "SearchRequestFilter",
    "SearchSDOsRequest",
    "VectorSearchRequestFilter",
    "VectorSearchResultsResultVector",
    "VectorSearchResultsResult",
    "VectorSearchResults",
    "VectorSearchRequest",
    "SdoSliceSearchResult"
]
