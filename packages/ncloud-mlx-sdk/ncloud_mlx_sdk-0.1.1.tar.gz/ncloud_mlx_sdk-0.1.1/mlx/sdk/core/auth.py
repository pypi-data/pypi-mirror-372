#
# ML expert Platform
# Copyright (c) 2025-present NAVER Cloud Corp.
# Apache-2.0
#

from datetime import datetime
from typing import Dict, Optional, Union

import jwt

from .config import ConfigFile, TokenType
from .errors import InvalidTokenError

__all__ = ["Token"]


class Token:
    """
    Token class to handle different types of tokens.
    """

    NoExpirationTime = -1

    def __init__(
        self,
        token: str,
        token_type: Union[TokenType, str],
        refresh_token: str = None,
    ):
        """
        Initialize the Token instance.

        :param token: Token string (access_token for KEYCLOAK, apikey for
                      MLX_API_KEY, sa_token for K8S_SA)
        :param token_type: TokenType (KEYCLOAK|MLX_API_KEY|K8S_SA)
        :param refresh_token: Token refresh string(optional, KEYCLOAK
                              Type only)
        """

        def _validate():
            return token or refresh_token and isinstance(token_type, TokenType)

        if isinstance(token_type, str):
            # Convert string to Enum
            try:
                token_type = TokenType(token_type)
            except ValueError:
                raise InvalidTokenError(f"Invalid token type:{token_type}")

        if not _validate():
            raise InvalidTokenError(f"Invalid Token: {token_type} / token: {token}")

        self._token = token
        self._refresh_token = refresh_token
        self._type = token_type
        self._infos = {}

        if self._type == TokenType.KEYCLOAK:
            # TODO: check iss if equal to cluster info
            decoded_token = jwt.decode(
                token or refresh_token, options={"verify_signature": False}
            )
            self._infos.update(decoded_token)

        self.account = self._infos.get("preferred_username", None)

    def __repr__(self):
        return (
            f"Token(type={self._type}, token_value={self._token}, "
            f"account={self.account})"
        )

    def display(self, no_redact: bool = False) -> str:
        from mlx.sdk.core.util import redact

        return redact(self.token, no_redact)

    def save(self):
        config_file = ConfigFile()

        # TODO : validate account accross all tokens saved in conf file
        if self.account:
            config_file.account = self.account

        if self.type == TokenType.KEYCLOAK:
            # Save access_token and refresh_token of Keycloak response
            config_file.keycloak_access_token = self.token
            config_file.keycloak_refresh_token = self.refresh_token

            # TODO: Reset apikey key when account name is changed

        elif self.type == TokenType.MLX_API_KEY:
            config_file.apikey = self.token

        elif self.type == TokenType.K8S_SA:
            config_file.k8s_token = self.token
            # TODO: set credential to kubeconfig

    @staticmethod
    def logout():
        Token.clear()

    @staticmethod
    def clear():
        ConfigFile().clear()
        # TODO: clear kubeconfig

    @property
    def type(self) -> TokenType:
        return self._type

    @property
    def token(self) -> str:
        return self._token

    @token.setter
    def token(self, token: str):
        self._token = token

    @property
    def access_token(self) -> str:
        """Alias for token property."""
        return self._token

    @access_token.setter
    def access_token(self, token: str):
        """Alias for token property."""
        self._token = token

    @property
    def refresh_token(self) -> str:
        return self._refresh_token

    @refresh_token.setter
    def refresh_token(self, refresh_token: str):
        self._refresh_token = refresh_token

    @property
    def preferred_user(self) -> Optional[str]:
        """Return the token's preferred_username."""
        return self._infos.get("preferred_username")

    @property
    def account(self) -> Optional[str]:
        """Return the token's account name."""
        return self._infos.get("account")

    @account.setter
    def account(self, account: str):
        self._infos["account"] = account

    @property
    def info(self) -> Dict[str, str]:
        """Return the token's raw infos."""
        return self._infos

    @property
    def expires_at(self) -> Optional[datetime]:
        """Return the token's expiration date."""
        timestamp = self._infos.get("exp", Token.NoExpirationTime)
        if timestamp == Token.NoExpirationTime:
            return None
        return datetime.fromtimestamp(timestamp)

    @property
    def expired(self) -> bool:
        """Return the token's expired status."""
        expires_at = self.expires_at
        if expires_at is None:
            return False
        return expires_at < datetime.now()
