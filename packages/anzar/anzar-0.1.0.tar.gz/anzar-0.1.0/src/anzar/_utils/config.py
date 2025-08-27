from anzar._utils.types import Header, Token, TokenType


class Config:
    def headers(self, token: Token | None) -> Header:
        default_headers = {
            "Content-Type": "application/json",
            "User-Agent": "Anzar-SDK/1.0",
        }
        if token is not None:
            if token.tokenType == TokenType.AccessToken:
                default_headers["authorization"] = f"Bearer {token.value}"
            if token.tokenType == TokenType.RefreshToken:
                default_headers["x-refresh-token"] = f"Bearer {token.value}"

        return default_headers
