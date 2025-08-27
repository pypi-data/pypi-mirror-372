# -*- coding: utf-8 -*-
"""Custom exceptions for the 24SEA API."""


class AuthenticationError(Exception):
    """An exception to raise when the user is not authenticated."""

    pass


class ProfileError(Exception):
    """An exception to raise when the user is authenticated, but its profile
    is not properly configured."""

    pass


class DataSignalsError(Exception):
    """An exception to raise when the data signals are not properly
    configured."""

    pass
