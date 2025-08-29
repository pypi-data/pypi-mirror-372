from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum, auto

from pydantic import BaseModel

type Header = Mapping[str, str | bytes | None]


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
