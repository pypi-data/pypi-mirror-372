# -*- coding: utf-8 -*-
# noqa: E501
# pylint: disable=C0301
"""Facilitate the users' interaction with the 24SEA API (https://api/24sea/eu) by providing pandas interfaces to the API endpoints.

The subpackages are:

- :mod:`api_24sea.datasignals`: Contains:
  * :class:`DataSignals` class, which is an accessor for transforming data
    signals from the 24SEA API into pandas DataFrames.
  * :mod:`api_24sea.datasignals.core`: Contains the core :class:`API` and
    :class:`AsyncAPI` classes, providing synchronous and asynchronous
    interfaces for interacting with the 24SEA API - DataSignals app.
    Serialization/deserialization methods are also provided to save and
    load API instances with their authentication state.
  * :mod:`api_24sea.datasignals.fatigue`: Contains the :class:`FatigueAccessor`
    class, which is a pandas DataFrame accessor for converting cycle-count
    columns into :class:`py_fatigue.CycleCount` objects.
  * :mod:`api_24sea.schemas`: Contains pydantic models for validating input
    parameters.

The submodules are:

- :mod:`api_24sea.abc`: Contains the AuthABC abstract base class, which provides
  a common interface for authentication classes.
- :mod:`api_24sea.exceptions`: Contains custom exceptions for the package.
- :mod:`api_24sea.singleton`: Contains the :class:`Singleton` class, which
  is a metaclass to facilitate the implementation usage with and without
  extras.
- :mod:`api_24sea.utils`: Contains utility functions and classes to help
  manage requests to the 24SEA API.
- :mod:`api_24sea.version`: Contains the version number of the package.
"""

from . import datasignals

__all__ = ["datasignals"]

from .version import __version__ as __version__  # noqa: F401

from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)  # type: ignore[name-defined]
