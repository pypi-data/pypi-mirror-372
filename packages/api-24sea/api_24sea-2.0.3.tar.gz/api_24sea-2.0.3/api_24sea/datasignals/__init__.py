# -*- coding: utf-8 -*-
"""The module for the DataSignals pandas accessor containing the main class
and the methods to authenticate, get metrics, and get data from the 24SEA API.
"""
from __future__ import annotations

import datetime
from typing import Any, Dict, List, Optional, Union
from warnings import simplefilter

import httpx
import pandas as pd

from .. import exceptions as E
from .. import utils as U

# Local imports
from .core import API

try:
    # delete the accessor to avoid warning
    del pd.DataFrame.datasignals  # type: ignore[assignment]
except AttributeError:
    pass

# This filter is used to ignore the PerformanceWarning that is raised when
# the DataFrame is modified in place. This is the case when we add columns
# to the DataFrame in the get_data method.
# This is the only way to update the DataFrame in place when using accessors
# and performance is not an issue in this case.
# See https://stackoverflow.com/a/76306267/7169710 for reference.
simplefilter(action="ignore", category=pd.errors.PerformanceWarning)


@pd.api.extensions.register_dataframe_accessor("datasignals")
class DataSignals:
    """Accessor for working with data signals coming from the 24SEA API."""

    def __init__(self, pandasdata: pd.DataFrame):
        """Initialize the DatasignalsAPI class.

        Parameters
        ----------
        pandasdata : pd.DataFrame
            Input DataFrame containing data to be processed.

        Attributes
        ----------
        base_url : str
            Base URL for the datasignals API endpoint.
        _username : str, optional
            Username for API authentication.
        _password : str, optional
            Password for API authentication.
        _auth : httpx.BasicAuth, optional
            Authentication object for API requests.
        _authenticated : bool
            Flag indicating authentication status.
        _selected_metrics : pd.DataFrame, optional
            DataFrame containing selected metrics.
        __api : C.API
            API client instance for making requests.
        """

        self._obj: pd.DataFrame = pandasdata
        self.__api: API = API()
        self.__sync_with_api()

    def __sync_with_api(self):
        """Sync the local DataFrame with the API."""
        self.base_url: str = self.__api.base_url
        self._username: Optional[str] = self.__api._username
        self._password: Optional[str] = self.__api._password
        self._auth: Optional[httpx.BasicAuth] = self.__api._auth
        self._authenticated: bool = self.__api._authenticated
        self._metrics_overview: Optional[pd.DataFrame] = (
            self.__api._metrics_overview
        )
        self._selected_metrics: Optional[pd.DataFrame] = (
            self.__api._selected_metrics
        )

    def _lazy_authenticate(self) -> bool:
        """Attempt authentication using environment variables"""
        self._authenticated = self.__api._lazy_authenticate()
        return self._authenticated

    @property
    def authenticated(self) -> bool:
        """Return the authentication status."""
        return self._authenticated

    @property
    @U.require_auth
    def metrics_overview(self) -> Optional[pd.DataFrame]:
        """Get the metrics overview DataFrame."""
        return self.__api.metrics_overview

    @U.validate_call(config=dict(arbitrary_types_allowed=True))
    def authenticate(
        self,
        username: str,
        password: str,
        __metrics_overview: Optional[pd.DataFrame] = None,  # type: ignore
    ) -> pd.DataFrame:
        """Authenticate the user with the 24SEA API. Additionally, define
        the ``metrics_overview`` dataframe as __api.metrics_overview.

        Parameters
        ----------
        username : str
            The username to authenticate.
        password : str
            The password to authenticate.

        Returns
        -------
        pd.DataFrame
            The authenticated DataFrame.
        """
        if not self._lazy_authenticate():
            self.__api = self.__api.authenticate(
                username, password, __metrics_overview
            )
        self.__sync_with_api()
        return self._obj

    @property
    @U.require_auth
    def selected_metrics(self) -> pd.DataFrame:
        """Return the selected metrics for the query."""
        # Get the selected metrics as the self._obj columns that are available
        # in the metrics_overview DataFrame
        return self.__api.selected_metrics(self._obj)

    @U.require_auth
    @U.validate_call
    def __get_data(
        self,
        sites: Optional[Union[List[str], str]],
        locations: Optional[Union[List[str], str]],
        metrics: Union[List[str], str],
        start_timestamp: Union[str, datetime.datetime],
        end_timestamp: Union[str, datetime.datetime],
    ):
        """Get the data signals from the 24SEA API.

        Parameters
        ----------
        sites : Optional[Union[List, str]]
            The site name or List of site names. If None, the site will be
            inferred from the metrics.
        locations : Optional[Union[List, str]]
            The location name or List of location names. If None, the location
            will be inferred from the metrics.
        metrics : Union[List, str]
            The metric name or List of metric names. It must be provided.
            They do not have to be the entire metric name, but can be a part
            of it. For example, if the metric name is
            ``"mean_WF_A01_windspeed"``, the user can equivalently provide
            ``sites="wf"``, ``locations="a01"``, ``metric="mean windspeed"``.
        start_timestamp : Union[str, datetime.datetime]
            The start timestamp for the query. It must be in ISO 8601 format,
            e.g., ``"2021-01-01T00:00:00Z"`` or a datetime object.
        end_timestamp : Union[str, datetime.datetime]
            The end timestamp for the query. It must be in ISO 8601 format,
            e.g., ``"2021-01-01T00:00:00Z"`` or a datetime object.

        Returns
        -------
        pd.DataFrame
            The DataFrame containing the data signals.
        """
        return self.__api.get_data(
            sites=sites,
            locations=locations,
            metrics=metrics,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            outer_join_on_timestamp=True,
            data=self._obj,
            as_dict=False,
        )

    def as_dict(
        self, metrics_map: Optional[pd.DataFrame] = None
    ) -> Dict[str, Dict[str, pd.DataFrame]]:
        """Return the DataFrames as a dictionary where the keys are the sites
        and the values are a dictionary where the keys are locations and the
        values are dataframes for each location.

        Parameters
        ----------
        metrics_map : Optional[pd.DataFrame], optional
            The DataFrame containing the metrics map. If None, the
            ``selected_metrics`` attribute will be used. Default is None.

        Returns
        -------
        Dict[str, Dict[str, pd.DataFrame]]
            The dictionary containing the dataframes for each site.

        Example
        -------
        >>> import pandas as pd
        >>> import api_24sea as sea
        >>> df = pd.DataFrame({
        ...     "timestamp": ["2021-01-01", "2021-01-02"],
        ...     "mean_WF_A01_windspeed": [10.0, 11.0],
        ...     "mean_WF_A02_windspeed": [12.0, 13.0]
        ... })
        >>> metrics_map = pd.DataFrame({
        ...     "site": ["wf", "wf"],
        ...     "location": ["a01", "a02"],
        ...     "metric": ["mean_WF_A01_windspeed", "mean_WF_A02_windspeed"]
        ... })
        >>> df.datasignals.as_dict(metrics_map)
        # output
        {
            "wf": {
                "a01": pd.DataFrame({
                    "timestamp": ["2021-01-01", "2021-01-02"],
                    "mean_WF_A01_windspeed": [10.0, 11.0]
                }),
                "a02": pd.DataFrame({
                    "timestamp": ["2021-01-01", "2021-01-02"],
                    "mean_WF_A02_windspeed": [12.0, 13.0]
                })
            }
        }
        """
        # We need to reset the dataframe index to get the timestamp column
        # as a column and not as the index.
        self._obj = U.parse_timestamp(self._obj, keep_index_only=False)
        if metrics_map is None:
            if self.selected_metrics is None:
                raise E.DataSignalsError(
                    "\033[31mThe \033[1mas_dict \033[22mmethod can only be "
                    "called when the selected_metrics attribute is set or when "
                    "the metrics_map argument is provided."
                )
            metrics_map = self.selected_metrics
        # fmt: off
        __melted = pd.melt(self._obj, id_vars=["timestamp"],
                           var_name="metric", value_name="value")
        __merged = pd.merge(__melted, metrics_map, on="metric", how="left")
        __srt = __merged[["timestamp", "site", "location", "metric", "value"]] \
                        .sort_values(by=["timestamp", "location"]) \
                        .reset_index(drop=True)
        __df = __srt.pivot_table(index=["site", "location", "timestamp"],
                                    columns="metric", values="value",
                                    aggfunc="first").reset_index()
        # fmt: on
        if __df.empty:
            raise E.DataSignalsError(
                "\033[31mThe \033[1mas_dict \033[22mmethod can only be called "
                "when the DataFrame is not empty."
            )
        if not all(
            c_ in __df.columns for c_ in ["site", "location", "timestamp"]
        ):
            raise E.DataSignalsError(
                "\033[31mThe \033[1mas_dict \033[22mmethod can only be called "
                "when the site, location, and timestamp columns are available."
            )
        if not isinstance(__df.index, pd.RangeIndex):
            raise E.DataSignalsError(
                "\033[31mThe \033[1mas_dict \033[22mmethod can only be called "
                "when the index is a \033[1mRangeIndex.\n"
                "\033[22mThe index is currently a \033[1m"
                f"{type(__df.index).__name__}.\n"
            )
        # Group the DataFrame by site and location
        groups = __df.groupby(["site", "location"])
        __dict: Dict[str, Dict[str, pd.DataFrame]] = {}
        for (s_, l_), group in groups:
            s_ = s_.lower()
            l_ = l_.upper()
            if s_ not in __dict:
                __dict[s_] = {}
            # Manipulate the group to remove columns with all NaN values
            # and set the index to the timestamp column.
            # This operation cannot be done safely in api-24sea.
            _df: pd.DataFrame = group.drop(["site", "location"], axis=1).dropna(
                axis=1, how="all"
            )
            _df = U.parse_timestamp(_df)
            if l_ not in __dict[s_]:
                __dict[s_][l_] = _df
            # Pass also the authentication, and __api to the DataFrame
            ds = getattr(__dict[s_][l_], "datasignals", None)
            if not ds:
                __dict[s_][l_].datasignals = DataSignals(__dict[s_][l_])
            ds = __dict[s_][l_].datasignals
            # pass down the same API client and sync its state
            ds.__api = self.__api
            ds.__sync_with_api()
        return __dict

    def get_data(
        self,
        sites: Optional[Union[List, str]],
        locations: Optional[Union[List, str]],
        metrics: Union[List, str],
        start_timestamp: Union[str, datetime.datetime],
        end_timestamp: Union[str, datetime.datetime],
    ) -> Optional[
        Union[
            pd.DataFrame,
            Dict[str, Union[Dict[str, pd.DataFrame], Dict[str, Any]]],
            List[Union[Any, str]],
        ]
    ]:
        """Get the data signals from the 24SEA API.

        Parameters
        ----------
        sites : Optional[Union[List, str]]
            The site name or List of site names. If None, the site will be
            inferred from the metrics.
        locations : Optional[Union[List, str]]
            The location name or List of location names. If None, the location
            will be inferred from the metrics.
        metrics : Union[List, str]
            The metric name or List of metric names. It must be provided.
            They do not have to be the entire metric name, but can be a part
            of it. For example, if the metric name is
            ``"mean_WF_A01_windspeed"``, the user can equivalently provide
            ``sites="wf"``, ``locations="a01"``, ``metric="mean windspeed"``.
        start_timestamp : Union[str, datetime.datetime]
            The start timestamp for the query. It must be in ISO 8601 format,
            e.g., ``"2021-01-01T00:00:00Z"`` or a datetime object.
        end_timestamp : Union[str, datetime.datetime]
            The end timestamp for the query. It must be in ISO 8601 format,
            e.g., ``"2021-01-01T00:00:00Z"`` or a datetime object.

        Returns
        -------
        Union[pd.DataFrame, Dict[str, Dict[str, pd.DataFrame]]]
            The DataFrame containing the data signals, or the dictionary
            containing the dataframes for each site and location.
        """
        return self.__get_data(
            sites=sites,
            locations=locations,
            metrics=metrics,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
        )
