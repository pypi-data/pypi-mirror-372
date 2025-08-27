from typing import Awaitable, Callable

from aiware.graphql.base.exceptions import GraphQLClientError

def catch_not_found[T](fn: Callable[..., T]) -> T | None:
    try:
        return fn()
    except GraphQLClientError as e:
        if "not found" in e.__str__(): return None
        else: raise e

async def acatch_not_found[T](fn: Awaitable[T]) -> T | None:
    try:
        return await fn
    except GraphQLClientError as e:
        if "not found" in e.__str__(): return None
        else: raise e
