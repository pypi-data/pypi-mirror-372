import dotenv

from ._api.client import HttpClient
from ._api.http_interceptor import HttpInterceptor

_ = dotenv.load_dotenv()


def get_anzar_auth():
    from ._auth.authenticator import AuthManager

    return AuthManager(HttpClient(HttpInterceptor()))


AnzarAuth = get_anzar_auth()
__all__ = ["AnzarAuth"]
