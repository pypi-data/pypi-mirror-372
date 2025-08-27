from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum, auto
from typing import Generic, TypeVar, override

from pydantic import BaseModel

Header = Mapping[str, str | bytes | None]
T = TypeVar("T", bound=BaseModel)


class NoType(BaseModel):
    status: str | None


class TokenType(Enum):
    AccessToken = auto()
    RefreshToken = auto()


@dataclass()
class Token:
    value: str
    tokenType: TokenType

    @classmethod
    def new(cls, value: str, tokenType: TokenType):
        return cls(value, tokenType)


R = TypeVar("R")


class Result(Generic[R]):
    @property
    def is_ok(self) -> bool: ...
    @property
    def is_err(self) -> bool: ...


class Ok(Result[R]):
    def __init__(self, value: R) -> None:
        self.value: R = value

    @property
    @override
    def is_ok(self) -> bool:
        return True

    @property
    @override
    def is_err(self) -> bool:
        return False


class Err(Result[R]):
    def __init__(self, error: str) -> None:
        self.error: str = error

    @property
    @override
    def is_ok(self) -> bool:
        return False

    @property
    @override
    def is_err(self) -> bool:
        return True
