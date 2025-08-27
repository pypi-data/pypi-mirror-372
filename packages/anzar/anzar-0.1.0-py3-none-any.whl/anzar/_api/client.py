from requests.models import Response

from anzar._models.auth import LoginRequest, RegisterRequest
from anzar._api.http_interceptor import HttpInterceptor
from anzar._utils.errors import Error
from anzar._utils.types import T
from anzar._utils.validator import Validator


class HttpClient:
    def __init__(self, http_interceptor: HttpInterceptor):
        self.http_interceptor: HttpInterceptor = http_interceptor
        self.accessToken: str | None = None

    def get(self, url: str, model_type: type[T]) -> T | Error:
        response: Response = self.http_interceptor.get(url)

        if response.status_code in (200, 201):
            return model_type.model_validate(response.json())
        else:
            return Error.model_validate(response.json())

    def post(
        self,
        url: str,
        data: LoginRequest | RegisterRequest | None,
        model_type: type[T],
    ) -> T | Error:
        if data:
            response: Response = self.http_interceptor.post(url, json=data.__dict__)
        else:
            response = self.http_interceptor.post(url)

        if response.status_code in (200, 201):
            return Validator().validate(model_type, response)
        else:
            return Error.model_validate(response.json())
