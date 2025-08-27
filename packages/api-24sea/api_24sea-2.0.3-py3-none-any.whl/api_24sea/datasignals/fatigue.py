# -*- coding: utf-8 -*-
"""Convert cycle-count columns in the DataFrame, if any, to
:class:`py_fatigue.CycleCount` objects. This functionality is available
only if the extra :mod:`py_fatigue` package is installed."""
# from typing import TYPE_CHECKING, NewType

import pandas as pd

from ..singleton import Singleton as S

try:
    swifter = S.swifter
except ImportError:
    pass


try:
    # delete the accessor to avoid warning
    del pd.DataFrame.fatigue  # type: ignore[assignment]
except AttributeError:
    pass


@pd.api.extensions.register_dataframe_accessor("fatigue")
class FatigueAccessor:
    """Accessor for the :mod:`py_fatigue` package."""

    def __init__(self, _obj: pd.DataFrame):
        self._obj = _obj
        self._validate()

    def _validate(self) -> None:
        if S.py_fatigue.CycleCount is None:
            raise ImportError(
                "The `py_fatigue` package is required for this functionality.\n"
                "Reinstall api-24sea with the `fatigue` extra, i.e.,\n"
                "pip install api-24sea[fatigue]"
            )
        # Check that the dataframe contains columns starting with "CC_",
        # otherwise raise a FatigueError
        if not any(col.startswith("CC_") for col in self._obj.columns):
            raise ValueError(
                "The DataFrame does not contain any columns starting with "
                "'CC_', which are required for this functionality."
            )
        # Check that the datafame index is of type DatetimeIndex
        if not isinstance(self._obj.index, pd.DatetimeIndex):
            raise ValueError(
                "The DataFrame index must be of type DatetimeIndex for this "
                "functionality. Currently, the index is of type "
                f"{type(self._obj.index)}."
            )

    def cycle_counts_to_objects(self) -> pd.DataFrame:
        """Convert cycle-count columns in the DataFrame to
        :class:`py_fatigue.CycleCount`"""
        self._validate()
        for col in self._obj.columns:
            if col.startswith("CC_"):
                # fmt: off
                self._obj[col] = self._obj.swifter.progress_bar(
                    desc=(f"\033[32;1mConverting \033[22;34m{col} "
                          "\033[32;1m...")
                ).apply(lambda row: S.py_fatigue.CycleCount.from_rainflow(
                    row[col],
                    name=col[3:],
                    timestamp=row.name)
                 if isinstance(row[col], dict) else row[col], axis=1)
                # fmt: on
        return self._obj
