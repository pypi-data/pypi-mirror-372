# -*- coding: utf-8 -*-
"""Abstract base class for authentication mixin."""

import logging
import os
from typing import Optional
from warnings import simplefilter

import httpx
import pandas as pd

from . import utils as U

simplefilter(action="ignore", category=pd.errors.PerformanceWarning)

logging.basicConfig(format="%(message)s", level=logging.WARNING)


class AuthABC:
    """Abstract base class for authentication mixin."""

    def __init__(self):
        self.base_url: str = f"{U.BASE_URL}"
        self._username: Optional[str] = None
        self._password: Optional[str] = None
        self._auth: Optional[httpx.BasicAuth] = None
        self._authenticated: bool = False
        self._permissions_overview: Optional[pd.DataFrame] = None

    def _set_auth(
        self, username: Optional[str], password: Optional[str]
    ) -> None:
        """Set the authentication credentials."""
        self._username = username
        self._password = password
        self._auth = httpx.BasicAuth(self._username, self._password)  # type: ignore  # pylint: disable=C0301  # noqa:E501
        self._authenticated = False

    def _clear_auth(self) -> None:
        """Clear the authentication credentials."""
        self._username = None
        self._password = None
        self._auth = None
        self._authenticated = False

    def _is_authenticated(self) -> bool:
        """Check if the client is authenticated."""
        return self._authenticated

    def _authenticate(self, username: str, password: str) -> bool:
        """Authenticate the client with the given credentials."""
        self._set_auth(username, password)
        self._authenticated = True
        return True

    @property
    def authenticated(self) -> bool:
        """Whether the client is authenticated"""
        return self._authenticated

    def _lazy_authenticate(self) -> bool:
        """Attempt authentication using environment variables"""
        if self._username and self._password:
            self.authenticate(self._username, self._password)
            return True
        username = (
            os.getenv("API_24SEA_USERNAME")
            or os.getenv("24SEA_API_USERNAME")
            or os.getenv("TWOFOURSEA_API_USERNAME")
            or os.getenv("API_TWOFOURSEA_USERNAME")
        )
        password = (
            os.getenv("API_24SEA_PASSWORD")
            or os.getenv("24SEA_API_PASSWORD")
            or os.getenv("TWOFOURSEA_API_PASSWORD")
            or os.getenv("API_TWOFOURSEA_PASSWORD")
        )
        if username and password:
            self.authenticate(username, password)
            return True
        return False

    @property
    @U.require_auth
    def permissions_overview(self) -> Optional[pd.DataFrame]:
        """Get the permissions overview DataFrame."""
        return self._permissions_overview

    @U.validate_call(config=dict(arbitrary_types_allowed=True))
    def authenticate(
        self,
        username: str,
        password: str,
        permissions_overview: Optional[pd.DataFrame] = None,
    ):
        """Meta for authenticate method"""
        self._permissions_overview = (
            permissions_overview
            if permissions_overview is not None
            else self._permissions_overview
        )
        return self
