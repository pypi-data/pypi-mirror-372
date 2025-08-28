import os

from anzar._api.client import HttpClient

from anzar._models.auth import AuthResponse
from anzar._models.user import User
from anzar._utils.errors import Error
from anzar._utils.storage import TokenStorage
from anzar._utils.types import NoType, TokenType
from anzar._utils.validator import Validator


class AuthManager:
    def __init__(self, httpClient: HttpClient) -> None:
        self._http_client: HttpClient = httpClient

        self._API_URL: str = os.getenv("API_URL", "http://localhost:3000")
        assert self._API_URL is not None, "Env was unable to load"
        self.__endpoints: dict[str, str] = {
            "login": f"{self._API_URL}/auth/login",
            "register": f"{self._API_URL}/auth/register",
            "user": f"{self._API_URL}/user",
            "logout": f"{self._API_URL}/auth/logout",
        }

    def register(self, username: str, email: str, password: str) -> Error | User:
        req = Validator().construct_register(username, email, password)
        if isinstance(req, Error):
            return req

        url = self.__endpoints["register"]
        response = self._http_client.post(url, req, AuthResponse)

        return response.user if isinstance(response, AuthResponse) else response

    def login(self, email: str, password: str):
        req = Validator().construct_login(email, password)
        if isinstance(req, Error):
            return req

        url = self.__endpoints["login"]
        response = self._http_client.post(url, req, AuthResponse)

        return response.user if isinstance(response, AuthResponse) else response

    def getUser(self):
        url = self.__endpoints["user"]
        response = self._http_client.get(url, User)
        return response

    def logout(self):
        url = self.__endpoints["logout"]
        response = self._http_client.post(url, None, NoType)
        TokenStorage().clear()

        return response

    def isLoggedIn(self):
        return TokenStorage().load(TokenType.AccessToken.name) is not None


# def main():
#     from pprint import pprint
#     from anzar._api.http_interceptor import HttpInterceptor
#
#     authManager = AuthManager(HttpClient(HttpInterceptor()))
#
#     # username, email, password = "Hakou", "hakouguelfen@gmail.com", "hakouguelfen"
#     # user = authManager.register(username, email, password)
#     # pprint(user)
#
#     # email, password = "hakouguelfen@gmail.com", "hakouguelfen"
#     # user = authManager.login(email, password)
#     # pprint(user)
#
#     user = authManager.getUser()
#     pprint(user)
#
#     response = authManager.logout()
#     pprint(response)
#
#
# if __name__ == "__main__":
#     main()
