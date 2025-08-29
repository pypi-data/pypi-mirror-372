import keyring

from anzar._models.auth import JWTTokens
from anzar._utils.types import TokenType


SERVICE_NAME = "AnzarSDK"

ACCESS_TOKEN = TokenType.AccessToken.name
REFRESH_TOKEN = TokenType.RefreshToken.name


class TokenStorage:
    def save(self, tokens: JWTTokens):
        try:
            keyring.set_password(SERVICE_NAME, ACCESS_TOKEN, tokens.accessToken)
            keyring.set_password(SERVICE_NAME, REFRESH_TOKEN, tokens.refreshToken)
        except Exception as e:
            print(e)

    def load(self, username: str):
        try:
            return keyring.get_password(SERVICE_NAME, username)
        except Exception as e:
            print(e)

    def clear(self):
        keyring.delete_password(SERVICE_NAME, ACCESS_TOKEN)
        keyring.delete_password(SERVICE_NAME, REFRESH_TOKEN)
