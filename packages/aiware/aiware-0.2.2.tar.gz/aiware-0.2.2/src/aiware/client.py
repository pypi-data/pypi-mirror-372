from types import TracebackType
from typing import Optional, Self

from aiware.common.auth import AbstractTokenAuth
from aiware.graphql.client import AiwareGraphQL, AiwareGraphQLFactory
from aiware.search.client import AiwareSearch, AiwareSearchFactory

class Aiware[G: AiwareGraphQL, S: AiwareSearch]:
    def __init__(
        self,
        *,
        graphql_endpoint: str,
        search_endpoint: str,
        graphql_factory: AiwareGraphQLFactory[G] = lambda endpoint, auth: AiwareGraphQL(url=endpoint, auth=auth),
        search_factory: AiwareSearchFactory[S] = lambda endpoint, auth: AiwareSearch(url=endpoint, auth=auth),
        auth: Optional[AbstractTokenAuth],
    ):
        self.auth: Optional[AbstractTokenAuth] = auth
        self.graphql_endpoint: str = graphql_endpoint
        self.search_endpoint: str = search_endpoint

        self.graphql_factory: AiwareGraphQLFactory = graphql_factory
        self.search_factory: AiwareSearchFactory = search_factory

        self.graphql: G = self.graphql_factory(endpoint=self.graphql_endpoint, auth=self.auth)
        self.search: S = self.search_factory(endpoint=self.search_endpoint, auth=self.auth)

    def __enter__(self: Self) -> Self:
        self.graphql.__enter__()
        self.search.__enter__()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_value: BaseException | None = None,
        traceback: TracebackType | None = None,
    ) -> None:
        self.graphql.__exit__(exc_type, exc_value, traceback)
        self.search.__exit__(exc_type, exc_value, traceback)

    def with_auth(self, auth: Optional[AbstractTokenAuth]) -> "Aiware[G, S]":
        return Aiware[G, S](
            graphql_endpoint=self.graphql_endpoint,
            search_endpoint=self.search_endpoint,
            graphql_factory=self.graphql_factory,
            search_factory=self.search_factory,
            auth=auth
        )
