from pydantic import BaseModel, ValidationError
from requests import Response

from anzar._utils.errors import Error

from anzar._models.auth import LoginRequest, RegisterRequest


class Validator:
    def construct_register(
        self, username: str, email: str, password: str
    ) -> RegisterRequest | Error:
        try:
            return RegisterRequest(username=username, email=email, password=password)

        except ValidationError as e:
            ctx = e.errors()[0].get("ctx")

            reason: str | None = ctx.get("reason") if ctx else None
            return Error(error=reason or "Data is not validated")

    def construct_login(self, email: str, password: str) -> LoginRequest | Error:
        try:
            return LoginRequest(email=email, password=password)
        except ValidationError as e:
            ctx = e.errors()[0].get("ctx")

            reason: str | None = ctx.get("reason") if ctx else None
            return Error(error=reason or "Data is not validated")

    def validate[T: BaseModel](self, model_type: type[T], res: Response) -> T | Error:
        try:
            return model_type.model_validate(res.json())
        except ValidationError as _:
            return Error(error="")
