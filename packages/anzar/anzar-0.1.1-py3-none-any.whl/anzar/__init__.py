import dotenv
import logging

from ._api.client import HttpClient
from ._api.http_interceptor import HttpInterceptor

_ = dotenv.load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def get_anzar_auth():
    from ._auth.authenticator import AuthManager

    return AuthManager(HttpClient(HttpInterceptor()))


AnzarAuth = get_anzar_auth()
__all__ = ["AnzarAuth"]
