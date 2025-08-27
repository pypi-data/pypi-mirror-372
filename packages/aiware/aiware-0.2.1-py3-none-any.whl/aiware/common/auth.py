import os
import httpx
from abc import ABC, abstractmethod

from pydantic import SecretStr


class AbstractAiwareToken(SecretStr, ABC):
    @abstractmethod
    def is_api_key(self) -> bool:
        pass

    @abstractmethod
    def is_jwt(self) -> bool:
        pass


class AiwareSessionToken(AbstractAiwareToken):
    def __init__(self, secret_value: str):
        super().__init__(secret_value=secret_value)

    def is_api_key(self):
        return False

    def is_jwt(self):
        return False


class AiwareApiKey(AbstractAiwareToken):
    def __init__(self, secret_value: str):
        super().__init__(secret_value=secret_value)

    def is_api_key(self):
        return True

    def is_jwt(self):
        return False


class AiwareJWT(AbstractAiwareToken):
    def __init__(self, secret_value: str):
        super().__init__(secret_value=secret_value)

    def is_api_key(self):
        return False

    def is_jwt(self):
        return True


class AbstractTokenAuth(httpx.Auth, ABC):
    @abstractmethod
    def get_token(self) -> AbstractAiwareToken:
        pass

    def sync_auth_flow(self, request):
        token = self.get_token()
        request.headers["Authorization"] = f"Bearer {token.get_secret_value()}"
        yield request

    async def async_auth_flow(self, request):
        token = self.get_token()
        request.headers["Authorization"] = f"Bearer {token.get_secret_value()}"
        yield request


class EnvAuth(AbstractTokenAuth):
    def get_token(self):
        session_token = os.environ.get("VERITONE_SESSION_ID")

        if session_token is not None:
            return AiwareSessionToken(session_token)

        api_key = os.environ.get("VERITONE_API_KEY")
        if api_key is not None:
            return AiwareApiKey(api_key)

        raise Exception("No VERITONE_SESSION_ID or VERITONE_API_KEY env variable found")


class TokenAuth(AbstractTokenAuth):
    def __init__(self, token: AbstractAiwareToken):
        super().__init__()
        self.token: AbstractAiwareToken = token

    def get_token(self) -> AbstractAiwareToken:
        return self.token
