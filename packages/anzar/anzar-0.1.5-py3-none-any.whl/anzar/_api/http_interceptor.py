import os
from typing import Any, override

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from anzar._models.auth import AuthResponse, JWTTokens
from anzar._utils.config import Config
from anzar._utils.logger import logger
from anzar._utils.storage import TokenStorage
from anzar._utils.types import Token, TokenType


class HttpInterceptor(requests.Session):
    def __init__(self) -> None:
        super().__init__()
        self.API_URL: str = os.getenv("API_URL", "http://localhost:3000")
        self.storage: TokenStorage = TokenStorage()
        self.banned_endpoints: list[str] = ["auth/login", "auth/register"]
        self.refresh_endpoints: list[str] = ["auth/logout", "auth/refreshToken"]

        # Retry logic (optional)
        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.mount("http://", adapter)
        self.mount("https://", adapter)

    def __extractTokenFromCache(self, tokenType: TokenType) -> Token | None:
        token = self.storage.load(tokenType.name)
        return Token.new(token, tokenType) if token else None

    def __isUrlPartOf(self, url: str | bytes, endpoints: list[str]) -> bool:
        return any(url == f"{self.API_URL}/{endpoint}" for endpoint in endpoints)

    def __get_appropriate_token(self, url: str | bytes) -> Token | None:
        if self.__isUrlPartOf(url, self.banned_endpoints):
            return None

        if self.__isUrlPartOf(url, self.refresh_endpoints):
            return self.__extractTokenFromCache(TokenType.RefreshToken)

        return self.__extractTokenFromCache(TokenType.AccessToken)

    def __handle_auth_response(
        self, url: str | bytes, response: requests.Response
    ) -> None:
        if not response.ok:
            return

        if url == f"{self.API_URL}/auth/refreshToken":
            jwtTokens = JWTTokens.model_validate(response.json())
        elif self.__isUrlPartOf(url, self.banned_endpoints):
            auth_response = AuthResponse.model_validate(response.json())
            jwtTokens = JWTTokens(
                accessToken=auth_response.accessToken,
                refreshToken=auth_response.refreshToken,
            )
        else:
            return

        self.storage.save(jwtTokens)

    def __send_request(
        self, method: str | bytes, url: str | bytes, *args, **kwargs
    ) -> requests.Response:
        token = self.__get_appropriate_token(url)
        kwargs["headers"] = Config().headers(token=token)
        return super().request(method, url, timeout=30, *args, **kwargs)

    @override
    def request(
        self,
        method: str | bytes,
        url: str | bytes,
        _refresh_attempted: bool = False,
        *args: Any,
        **kwargs: Any,
    ) -> requests.Response:
        # PRE-REQUEST INTERCEPTION
        logger.info(f"{method} {url}")
        response = self.__send_request(method, url, *args, **kwargs)

        # POST-RESPONSE INTERCEPTION
        logger.info(f"Response: {response.status_code}")
        if (
            response.status_code == 401
            and not self.__isUrlPartOf(url, self.banned_endpoints)
            and not self.__isUrlPartOf(url, self.refresh_endpoints)
            and not _refresh_attempted
        ):
            # header: Content-Type: application/x-www-form-urlencoded
            response = self.request(
                method="POST",
                url=f"{self.API_URL}/auth/refreshToken",
                _refresh_attempted=True,
                *args,
                **kwargs,
            )

            response = self.__send_request(method, url, *args, **kwargs)

        self.__handle_auth_response(url, response)

        return response
