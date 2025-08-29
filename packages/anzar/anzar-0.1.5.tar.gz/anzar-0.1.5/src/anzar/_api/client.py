from pydantic import BaseModel
import requests
from requests.models import Response

from anzar._api.http_interceptor import HttpInterceptor
from anzar._utils.errors import Error
from anzar._utils.logger import logger
from anzar._utils.validator import Validator


class HttpClient:
    def __init__(self, http_interceptor: HttpInterceptor):
        self.http_interceptor: HttpInterceptor = http_interceptor
        self.accessToken: str | None = None

    def health_check(self, url: str) -> bool:
        try:
            response = requests.get(url)
            return response.status_code in (200, 201)
        except Exception as _:
            logger.error(
                "The server is currently unavailable. Please check the server status or try again later."
            )
            raise ConnectionError("Server is down: Unable to establish connection")

    def get[T: BaseModel](self, url: str, model_type: type[T]) -> T | Error:
        response: Response = self.http_interceptor.get(url)

        if response.status_code in (200, 201):
            return model_type.model_validate(response.json())
        else:
            return Error.model_validate(response.json())

    def post[T: BaseModel](
        self, url: str, data: BaseModel | None, model_type: type[T]
    ) -> T | Error:
        payload = data.model_dump() if data else None
        response: Response = self.http_interceptor.post(url, json=payload)

        if response.status_code in (200, 201):
            return Validator().validate(model_type, response)
        else:
            return Error.model_validate(response.json())
