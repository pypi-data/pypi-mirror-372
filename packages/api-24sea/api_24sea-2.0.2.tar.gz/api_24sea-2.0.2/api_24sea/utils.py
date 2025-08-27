# -*- coding: utf-8 -*-
"""Utility functions and classes."""
import asyncio
import datetime
import logging
import multiprocessing
import time
import warnings
from collections import defaultdict
from types import CoroutineType
from typing import Any, DefaultDict, Dict, Iterable, List, Optional, Union

import httpx
import pandas as pd
from shorthand_datetime import parse_shorthand_datetime
from tqdm import tqdm
from tqdm.asyncio import tqdm_asyncio
from tqdm.contrib.logging import logging_redirect_tqdm

# Local imports
from . import exceptions as E
from . import version

BASE_URL = "https://api.24sea.eu/routes/v1/"
PYDANTIC_V2 = version.parse_version(version.__version__).major >= 2

if PYDANTIC_V2:
    from pydantic import field_validator  # type: ignore
    from pydantic import BaseModel, validate_call

else:
    from pydantic import BaseModel, validator  # noqa: F401

    # Fallback for validate_call (acts as a no-op)
    def validate_call(*args, **kwargs):
        # Remove config kwarg if present since it's not supported in v1
        if "config" in kwargs:
            del kwargs["config"]

        def decorator(func):
            return func

        if args and callable(args[0]):
            return decorator(args[0])
        return decorator

    # Shim for field_validator to behave like validator
    def field_validator(field_name, *args, **kwargs):
        def decorator(func):
            # Convert mode='before' to pre=True for v1 compatibility
            if "mode" in kwargs:
                if kwargs["mode"] == "before":
                    kwargs["pre"] = True
                del kwargs["mode"]
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                return validator(field_name, *args, **kwargs)(func)

        return decorator


def handle_request(
    url: str,
    params: Dict,
    auth: Optional[httpx.BasicAuth],
    headers: Optional[Dict[str, str]] = {"accept": "application/json"},
    max_retries: int = 10,
    timeout: int = 3600,
) -> httpx.Response:
    """Handle the request to the 24SEA API and manage errors using httpx.

    This function will handle the request to the 24SEA API and manage any
    errors that may arise. If the request is successful, the response object
    will be returned. Otherwise, an error will be raised.

    Parameters
    ----------
    url : str
        The URL to which to send the request.
    params : dict
        The parameters to send with the request.
    auth : httpx.BasicAuth
        The authentication object.
    headers : dict
        The headers to send with the request.

    Returns
    -------
    httpx.Response
        The response object if the request was successful, otherwise error.
    """
    if auth is None:
        auth = httpx.BasicAuth("", "")
    retry_count = 0

    while True:
        try:
            # fmt: off
            r_ = httpx.get(url, params=params, auth=auth, headers=headers,
                           timeout=timeout)
            # fmt: on
            if r_.status_code != 502 or retry_count >= max_retries:
                break
            retry_count += 1
            if retry_count <= max_retries:
                time.sleep(3)
                continue
        except httpx.RequestError as exc:
            raise exc
    # fmt: off
    if r_.status_code in [400, 401, 403, 404, 503, 504]:
        print(f"Request failed because: \033[31;1m{r_.text}\033[0m")
        r_.raise_for_status()
    elif r_.status_code in [500, 501, 502]:
        print("\033[31;1mServer-side error. Try to run again the query. If the"
              "error persists, you will need to contact support at "
              "\033[32;1;4msupport.api@24sea.eu\033[0m")
        r_.raise_for_status()
    elif r_.status_code > 400:
        print("Request failed with status code: "
              f"\033[31;1m{r_.status_code}\033[0m")
        r_.raise_for_status()
    # fmt: on
    return r_


async def handle_request_async(
    url: str,
    params: Dict,
    auth: Optional[httpx.BasicAuth],
    headers: Optional[Dict[str, str]] = {"accept": "application/json"},
    max_retries: int = 10,
    timeout: int = 1800,
) -> httpx.Response:
    """Asynchronously handle the request to the 24SEA API using httpx's
    AsyncClient."""
    retry_count = 0
    async with httpx.AsyncClient(
        auth=auth, headers=headers, timeout=timeout
    ) as client:
        while True:
            try:
                r_ = await client.get(url, params=params)
                if r_.status_code != 502 or retry_count >= max_retries:
                    break
                retry_count += 1
                if retry_count <= max_retries:
                    await asyncio.sleep(3)
                    continue
            except (httpx.NetworkError, httpx.TimeoutException) as exc:
                raise exc
        # fmt: off
        if r_.status_code in [400, 401, 403, 404, 502, 503, 504]:
            logging.error(f"Request failed because: \033[31;1m{r_.text}\033[0m")
            r_.raise_for_status()
        elif r_.status_code == 500:
            logging.error("\033[31;1mInternal server error. You will need to "
                          "contact support at \033[32;1;4msupport.api@24sea.eu"
                          "\033[0m")
            r_.raise_for_status()
        elif r_.status_code > 400:
            logging.error("Request failed with status code: "
                          f"\033[31;1m{r_.status_code}\033[0m")
            r_.raise_for_status()
        # fmt: on
        return r_


def default_to_regular_dict(d_: Union[DefaultDict, Dict]) -> Dict:
    """Convert a defaultdict to a regular dictionary."""
    if isinstance(d_, defaultdict):
        return {k: default_to_regular_dict(v) for k, v in d_.items()}
    return d_


def require_auth(func):
    """Decorator to ensure authentication before executing a method"""

    def wrapper(self, *args, **kwargs):
        """Wrapper function to check authentication."""
        if not self.authenticated:
            self._lazy_authenticate()
        if not self.authenticated:
            raise E.AuthenticationError(
                "\033[31;1mAuthentication needed before querying the metrics.\n"
                "\033[0mUse the \033[34;1mdatasignals.\033[0mauthenticate("
                "\033[32;1m<username>\033[0m, \033[32;1m<password>\033[0m) "
                "method."
            )
        return func(self, *args, **kwargs)

    return wrapper


# def require_auth_async(func):
#     """Decorator to ensure authentication before executing a method"""

#     async def wrapper(self, *args, **kwargs):
#         """Wrapper function to check authentication."""
#         if not self.authenticated:
#             await self._lazy_authenticate()
#         if not self.authenticated:
#             raise E.AuthenticationError(
#                 "\033[31;1mAuthentication needed before querying the metrics.\n"
#                 "\033[0mUse the \033[34;1mdatasignals.\033[0mauthenticate("
#                 "\033[32;1m<username>\033[0m, \033[32;1m<password>\033[0m) "
#                 "method."
#             )
#         return await func(self, *args, **kwargs)

#     return wrapper


def parse_timestamp(
    df: pd.DataFrame,
    formats: Iterable[str] = ("ISO8601", "mixed"),
    dayfirst: bool = False,
    keep_index_only: bool = True,
) -> pd.DataFrame:
    """Parse timestamp column in DataFrame using multiple format attempts.

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame containing timestamp column or index
    formats : Iterable[str], default ('ISO8601', 'mixed')
        List of datetime format strings to try
    dayfirst : bool, default False
        Whether to interpret dates as day first

    Returns
    -------
    pandas.DataFrame
        DataFrame with parsed timestamp column

    Raises
    ------
    ValueError
        If timestamp parsing fails with all formats
    """
    series = None
    d_e = (
        f"No format matched the timestamp index/column among {formats}.\n"
        "            Try calling `parse_timestamp` manually with another "
        "format, e.g.,\n"
        "            \033[32;1m>>>\033[31;1m import\033[0m api_24sea.utils "
        "\033[31;1mas \033[0mU\n"
        "            \033[32;1m>>>\033[0m U.parse_timestamp(df,\n"
        "                                  formats=\033[32m[\033[36m"
        "'YYYY-MM-DDTHH:MM:SSZ'\033[32m]\033[0m,\n"
        "                                  dayfirst=\033[34mFalse\033[0m)"
    )

    if df.index.name == "timestamp":
        if "timestamp" in df.columns:
            # fmt: off
            logging.warning("Both index and column named 'timestamp' found. "
                            "Index takes precedence.")
            # fmt: on
            # Drop the column if it's not the index
            df.drop(columns="timestamp", inplace=True)
        series = df.index.to_series()
    else:
        if "timestamp" in df.columns:
            if df["timestamp"].isnull().all():
                # fmt: off
                raise E.DataSignalsError("`data` must include a 'timestamp' "
                                         "column or indices convertible to "
                                         "timestamps.")
                # fmt: on
            series = df["timestamp"]
    if series is None:
        raise E.DataSignalsError(d_e)
    try:
        # Try parsing with different formats
        for fmt in formats:
            try:
                df["timestamp"] = pd.to_datetime(
                    series, format=fmt, dayfirst=dayfirst, errors="raise"
                )
                if keep_index_only:
                    df.set_index("timestamp", inplace=True)
                return df
            except ValueError:
                continue
        # fmt: off
        # If all previous attempts failed, it means that pandas version
        # is not compatible with the formats provided, therefore try
        # with the following formats.
        formats = ["%Y-%m-%dT%H:%M:%S%z", "%d.%m.%YT%H:%M:%S.%f%z",
                   "%Y-%m-%dT%H:%M:%SZ", "%d.%m.%YT%H:%M:%S.%fZ"]
        # fmt: on
        df["timestamp"] = pd.NaT
        for fmt in formats:
            temp_series = pd.to_datetime(series, format=fmt, errors="coerce")
            df["timestamp"].fillna(temp_series, inplace=True)
        if keep_index_only:
            df.set_index("timestamp", inplace=True)
        return df
    except Exception as exc:
        logging.error(f"All timestamp parsing attempts failed: {str(exc)}")
        raise E.DataSignalsError("Could not parse timestamp data") from exc


def estimate_chunk_size(
    tasks: list,
    start_timestamp: Union[str, datetime.datetime],
    end_timestamp: Union[str, datetime.datetime],
    grouped_metrics: Iterable,
    selected_metrics: Union[pd.DataFrame, None] = None,
    target: str = "metric",
):
    """
    Estimate the optimal chunk size for processing tasks based on the expected
    data volume.
    This function calculates the estimated size of the data request in megabytes
    (MB) by considering the number of data points, the number of tasks, and the
    bytes required per metric. It then determines an appropriate chunk size for
    processing the tasks efficiently.

    Parameters
    ----------
    tasks : list
        List of tasks to be processed.
    query : object
        Query object containing at least `start_timestamp` and `end_timestamp`
        attributes.
    grouped_metrics : iterable
        Iterable of grouped metrics, where each group is a tuple (key, group),
        and group is typically a DataFrame.
    selected_metrics : pandas.DataFrame or None
        DataFrame containing selected metrics with at least a "metric" column
        and optionally a "data_group" column.
    target : str, default "metric"
        The target column name in `selected_metrics` and `grouped_metrics`

    Returns
    -------
    dict
        Dictionary with the following keys:
            - "total_mb": float, estimated total size of the request in MB.
            - "n_tasks": int, number of tasks.
            - "chunk_size": int, recommended chunk size for processing.

    Notes
    -----
    - The function assumes each data point is a float64 (8 bytes) unless
      overridden by the "data_group".
    - The number of data points is estimated as one every 10 minutes between the
      start and end timestamps.
    - Chunk size is determined based on the estimated total data size.
    """

    def parse_dt(dt):
        if isinstance(dt, str):
            try:
                return pd.to_datetime(dt)
            except pd._libs.tslibs.parsing.DateParseError:  # type: ignore
                _dt = parse_shorthand_datetime(dt)
                if _dt is not None:
                    dt = _dt.replace(tzinfo=None)
        return dt

    start_dt = parse_dt(start_timestamp)
    end_dt = parse_dt(end_timestamp)
    n_minutes = (end_dt - start_dt).total_seconds() / 60  # type: ignore
    n_points = int(n_minutes // 10) + 1
    n_tasks = len(tasks)
    # Build a dictionary of bytes per metric
    bytes_per_metric = {}
    if selected_metrics is not None:
        for _, row in selected_metrics.iterrows():
            metric = row[target]
            data_group = str(row.get("data_group", "")).lower()
            if data_group == "fatigue":
                bytes_per_metric[metric] = 200
            elif data_group == "mpe":
                bytes_per_metric[metric] = 50
            elif data_group == "mdl":
                bytes_per_metric[metric] = 50
            else:
                bytes_per_metric[metric] = 8
    total_bytes = 0
    for _, group in grouped_metrics:
        if isinstance(group, pd.DataFrame):
            group_met = group[target].tolist()
        else:
            group_met = [group[target]] if hasattr(group, target) else []
        group_bytes = sum(bytes_per_metric.get(m, 8) for m in group_met)
        total_bytes += n_points * group_bytes

    # Check for negative or zero values (sanity check)
    if total_bytes <= 0 or n_points <= 0:
        total_bytes = 0
    total_mb = total_bytes / (1024 * 1024)

    # Determine chunk_size
    if total_mb < 40:
        chunk_size = n_tasks
    elif total_mb < 80:
        chunk_size = max(1, n_tasks // 2)
    elif total_mb < 160:
        chunk_size = max(1, n_tasks // 4)
    else:
        chunk_size = max(1, n_tasks // 8)

    logging.info(f"Estimated request size: {total_mb:.2f} MB")
    return {
        "total_mb": total_mb,
        "n_tasks": n_tasks,
        "chunk_size": chunk_size,
    }


async def gather_in_chunks(
    tasks: List[CoroutineType], chunk_size: int = 5, timeout: int = 3600
) -> List:
    results = []
    chunk_results = []
    with logging_redirect_tqdm():
        total_tasks = len(tasks)

        if total_tasks == 1:
            desc = "API-24SEA get_data"
        elif chunk_size == 1:
            desc = f"API-24SEA get_data [total locations: {total_tasks}]"
        else:
            # fmt: off
            desc = (f"API-24SEA get_data in {chunk_size}-sized chunks "
                    f"[total locations: {total_tasks}]")
        for i in tqdm(
            range(0, len(tasks), max(1, chunk_size)),
            desc=desc,
            colour="#c9cfd8",
        ):
            chunk = tasks[i : i + chunk_size]
            chunk_results = await tqdm_asyncio.gather(
                *chunk,
                desc=f"Getting chunk: [{i+1}-{i+len(chunk)}]",
                timeout=timeout,
                colour="#e4e8ee",
            )
            results.extend(chunk_results)
    return results


def fetch_data_sync(
    url,
    site: str,
    location: str,
    start_timestamp: Union[datetime.datetime, str],
    end_timestamp: Union[datetime.datetime, str],
    headers: Optional[Dict[str, str]],
    group: pd.DataFrame,
    auth: Optional[httpx.BasicAuth],
    timeout: int,
    target: str = "metric",
) -> Any:
    """Syncronously fetch metrics data for the datasignals API app."""
    # fmt: off
    s_ = "• " + ",".join(group[target].tolist()).replace(",", "\n            • ")  # noqa: E501  # pylint: disable=C0301
    logging.info(f"\033[32;1m⏳ Getting data for {site} - "
                    f"{location}...\n📊 \033[35;1m{target.capitalize()}s: "
                    f"\033[0;34m{s_}\n\033[0m")
    # fmt: on
    r_ = handle_request(
        url,
        {
            "start_timestamp": start_timestamp,
            "end_timestamp": end_timestamp,
            "project": [site],
            "location": [location],
            f"{target}s": ",".join(group[target].tolist()),
        },
        auth,
        headers,
        timeout=timeout,
    )
    # Warn if empty
    if r_.json() == []:
        logging.warning(
            f"\033[33;1m⚠️ No data found for {site} - " f"{location}.\033[0m"
        )
    return r_.json()


def fetch_availability_sync(
    url,
    site: str,
    location: str,
    start_timestamp: Union[datetime.datetime, str],
    end_timestamp: Union[datetime.datetime, str],
    granularity: Union[str, int],
    sampling_interval_seconds: int,
    headers: Optional[Dict[str, str]],
    group: pd.DataFrame,
    auth: Optional[httpx.BasicAuth],
    timeout: int,
) -> Any:
    """Syncronously fetch metrics data for the datasignals API app."""
    # fmt: off
    s_ = "• " + ",".join(group["metric"].tolist()).replace(",", "\n            • ")  # noqa: E501  # pylint: disable=C0301
    logging.info(f"\033[32;1m⏳ Getting availabilities for {site} - "
                    f"{location}...\n📊 \033[35;1mMetrics: "
                    f"\033[0;34m{s_}\n\033[0m")
    params: Dict[str, Union[List[str], datetime.datetime, str, int]] = {
        "start_timestamp": start_timestamp,
        "end_timestamp": end_timestamp,
        "project": [site],
        "location": [location],
        "metrics": ",".join(group["metric"].tolist()),
    }
    # fmt: on
    if isinstance(granularity, str):
        params["granularity"] = granularity
    if isinstance(granularity, int):
        params["bucket_seconds"] = granularity
    params["sampling_interval_seconds"] = sampling_interval_seconds

    r_ = handle_request(url, params, auth, headers, timeout=timeout)
    # Warn if empty
    if r_.json() == []:
        logging.warning(
            f"\033[33;1m⚠️ No data found for {site} - " f"{location}.\033[0m"
        )
    return r_.json()


async def fetch_availability_async(
    url: str,
    site: str,
    location: str,
    start_timestamp: Union[datetime.datetime, str],
    end_timestamp: Union[datetime.datetime, str],
    granularity: Union[str, int],
    sampling_interval_seconds: int,
    headers: Optional[Dict[str, str]],
    group: pd.DataFrame,
    auth: Optional[httpx.BasicAuth],
    timeout: int,
    max_retries: int,
) -> Any:
    """Asynchronously fetch availability data for a site/location."""
    s_ = "• " + ",".join(group["metric"].tolist()).replace(
        ",", "\n            • "
    )
    logging.info(
        f"\033[32;1m⏳ Getting availabilities for {site} - {location}..."
        f"\n📊 \033[35;1mMetrics: \033[0;34m{s_}\n\033[0m"
    )
    params: Dict[str, Union[List[str], datetime.datetime, str, int]] = {
        "start_timestamp": start_timestamp,
        "end_timestamp": end_timestamp,
        "project": [site],
        "location": [location],
        "metrics": ",".join(group["metric"].tolist()),
    }
    if isinstance(granularity, str):
        params["granularity"] = granularity
    else:
        params["bucket_seconds"] = granularity
    params["sampling_interval_seconds"] = sampling_interval_seconds
    r_ = await handle_request_async(
        url, params, auth, headers, max_retries=max_retries, timeout=timeout
    )
    result_json = r_.json()
    if result_json == []:
        logging.warning(
            f"\033[33;1m⚠️ No data found for {site} - {location}.\033[0m"
        )
    return result_json


async def fetch_data_async(
    url,
    site: str,
    location: str,
    start_timestamp: Union[datetime.datetime, str],
    end_timestamp: Union[datetime.datetime, str],
    headers: Optional[Dict[str, str]],
    group: pd.DataFrame,
    auth: Optional[httpx.BasicAuth],
    timeout: int,
    max_retries: int,
    as_dict: bool = False,
    target: str = "metric",
) -> Union[pd.DataFrame, Dict[str, Any]]:
    """Asyncronously fetch metrics data for the datasignals API app."""
    s_ = "• " + ",".join(group[target].tolist()).replace(
        ",", "\n            • "
    )
    logging.info(
        f"\033[32;1m⏳ Getting data for {site} - {location}..."
        f"\n📊 \033[35;1m{target.capitalize()}s: \033[0;34m{s_}\n\033[0m"
    )
    r_ = await handle_request_async(
        url,
        {
            "start_timestamp": start_timestamp,
            "end_timestamp": end_timestamp,
            "project": [site],
            "location": [location],
            f"{target}s": ",".join(group[target].tolist()),
        },
        auth,
        headers,
        max_retries=max_retries,
        timeout=timeout,
    )
    result_json = r_.json()
    if result_json == []:
        logging.warning(
            f"\033[33;1m⚠️ No data found for {site} - {location}.\033[0m"
        )
    if as_dict:
        return result_json
    return pd.DataFrame(result_json)


async def fetch_oldest_timestamp_async(
    url,
    site: str,
    locations: Optional[str],
    headers: Dict[str, str],
    auth: Optional[httpx.BasicAuth],
    timeout: int,
    max_retries: int,
    as_dict: bool = False,
) -> Union[pd.DataFrame, Dict[str, Any]]:
    # Format locations with bullets and newlines
    if locations:
        formatted_locations = "   • " + "\n   • ".join(locations.split(","))
        logging.info(
            f"\033[32;1m⏳ Getting oldest timestamps for {site} at the "
            f"following locations:\n{formatted_locations}\n\033[0m"
        )
    else:
        logging.info(
            f"\033[32;1m⏳ Getting oldest timestamps for {site}\n\033[0m"
        )
    r_ = await handle_request_async(
        url,
        (
            {"project": site, "locations": locations}
            if locations
            else {"project": site}
        ),
        auth,
        headers,
        max_retries=max_retries,
        timeout=timeout,
    )
    result_json = r_.json()
    if result_json == []:
        logging.warning(f"\033[33;1m⚠️ No data found for {site}.\033[0m")
    if as_dict:
        return result_json
    return pd.DataFrame(result_json)


def set_threads_nr(threads: Optional[int], thread_limit: int = 30) -> int:
    """
    Set the number of threads to use for processing.

    Parameters
    ----------
    threads : Optional[int]
        The number of threads to use. If None, the number of available CPU cores
        will be used.

    Returns
    -------
    int
        The number of threads to use.
    """
    if threads is None:
        return multiprocessing.cpu_count()
    if threads < 1:
        return 1
    return int(threads) if threads < thread_limit else thread_limit


def parse_stats_list(stats_list: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Parse a list of statistics dictionaries into a DataFrame.

    Parameters
    ----------
    stats_list : List[Dict[str, Any]]
        List of dictionaries containing statistics data.

    Returns
    -------
    pd.DataFrame
        DataFrame containing the parsed statistics.
    """
    if not stats_list:
        return pd.DataFrame()

    rows = []
    for d in stats_list:
        for k, v in d.items():
            if "_" in k:
                prefix, metric = k.split("_", 1)
                rows.append({"metric": metric, "stat_type": prefix, "value": v})

    if not rows:
        return pd.DataFrame()

    # Create DataFrame and pivot in one operation
    df = pd.DataFrame(rows)
    stats_df = df.pivot_table(
        index="metric", columns="stat_type", values="value", aggfunc="first"
    ).reset_index()

    # Reorder and clean
    raw_prefixes = sorted(c_ for c_ in stats_df.columns if c_ != "metric")
    cols_order = ["metric"] + sorted(raw_prefixes)
    for c in cols_order:
        if c not in stats_df.columns:
            stats_df[c] = None
    stats_df = stats_df[cols_order]

    return stats_df.reset_index(drop=True)


def get_stats_overview_info(
    stats_df: pd.DataFrame,
    metrics_overview: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """
    Get the overview information for statistics DataFrame.

    Parameters
    ----------
    stats_df : pd.DataFrame
        DataFrame containing statistics data.
    metrics_overview : pd.DataFrame
        DataFrame containing metrics overview information.

    Returns
    -------
    pd.DataFrame
        DataFrame with overview information merged with stats_df.
    """
    if metrics_overview is None:
        return stats_df
    if stats_df.empty or metrics_overview.empty:
        return stats_df

    stats_df_temp = stats_df.copy()
    overview_temp = metrics_overview.copy()
    stats_df_temp["metric_lower"] = stats_df_temp["metric"].str.lower()
    overview_temp["metric_lower"] = overview_temp["metric"].str.lower()
    merged = stats_df_temp.merge(
        overview_temp[
            [
                "metric",
                "metric_lower",
                "site",
                "location",
                "data_group",
                "statistic",
                "short_hand",
                "print_str",
            ]
        ],
        on="metric_lower",
        how="left",
        suffixes=("", "_overview"),
    )
    merged["metric"] = merged["metric_overview"].fillna(merged["metric"])
    return merged.drop(["metric_lower", "metric_overview"], axis=1)


def get_stats_as_dict(
    stats_df: pd.DataFrame,
) -> Dict[str, Dict[str, pd.DataFrame]]:
    """
    Convert the statistics DataFrame to a dictionary format.

    Parameters
    ----------
    stats_df : pd.DataFrame
        DataFrame containing statistics data.

    Returns
    -------
    Dict[str, Dict[str, pd.DataFrame]]
        Dictionary with site and location as keys and statistics as values.
    """
    result_dict: DefaultDict[str, DefaultDict[str, pd.DataFrame]] = defaultdict(
        lambda: defaultdict(pd.DataFrame)
    )
    # fmt: off
    for (s_, l_), group in stats_df.groupby(['site', 'location']):
        s_ = s_.lower()
        l_ = l_.upper()
        result_dict[s_][l_] = group.drop(['site', 'location'],
                                            axis=1).reset_index(drop=True)
    # fmt: on
    return default_to_regular_dict(result_dict)


def get_metrics_data_df_as_dict(
    metrics_data_df: pd.DataFrame, selected_metrics: pd.DataFrame
) -> Dict[str, Dict[str, pd.DataFrame]]:
    """
    Convert the metrics DataFrame to a dictionary format.

    Parameters
    ----------
    metrics_data_df : pd.DataFrame
        DataFrame containing metrics data.

    Returns
    -------
    Dict[str, Dict[str, pd.DataFrame]]
        Dictionary with site and location as keys and metrics data as values.
    """
    # We need to reset the dataframe index to get the timestamp column
    # as a column and not as the index.
    metrics_data_df = parse_timestamp(metrics_data_df, keep_index_only=False)
    # fmt: off
    __melted = pd.melt(metrics_data_df, id_vars=["timestamp"],
                        var_name="metric", value_name="value")
    # Case-insensitive merge on metric (keep original 'metric' columns, only drop 'metric_lower')
    __melted["metric_lower"] = __melted["metric"].str.lower()
    _selected_metrics_ci = selected_metrics.copy()
    _selected_metrics_ci["metric_lower"] = _selected_metrics_ci["metric"].str.lower()
    __merged = pd.merge(__melted, _selected_metrics_ci, on="metric_lower", how="left")

    # Resolve possible duplicate metric columns (metric_x from melted, metric_y from selected)
    if "metric_x" in __merged.columns and "metric_y" in __merged.columns:
        # Prefer the casing from the selected metrics dataframe when available
        __merged["metric"] = __merged["metric_y"].fillna(__merged["metric_x"])
        __merged.drop(columns=[c for c in ["metric_x", "metric_y",
                                           "metric_lower"]
                               if c in __merged.columns], inplace=True)
    else:
        # Just drop helper column
        if "metric_lower" in __merged.columns:
            __merged.drop(columns=["metric_lower"], inplace=True)
    __srt = (__merged[["timestamp", "site", "location", "metric", "value"]]
             .sort_values(by=["timestamp", "location"]).reset_index(drop=True))
    __df = (__srt.pivot_table(index=["site", "location", "timestamp"],
                              columns="metric", values="value",
                              aggfunc="first",).reset_index())
    # fmt: on
    if __df.empty:
        raise E.DataSignalsError(
            "\033[31mThe \033[1mas_dict \033[22mmethod can only be called "
            "when the DataFrame is not empty."
        )
    if not all(c_ in __df.columns for c_ in ["site", "location", "timestamp"]):
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
        _df: pd.DataFrame = group.drop(["site", "location"], axis=1).dropna(
            axis=1, how="all"
        )
        _df = parse_timestamp(_df)
        _df = _df.sort_index()  # sort by timestamp
        if l_ not in __dict[s_]:
            __dict[s_][l_] = _df

    return default_to_regular_dict(__dict)


def series_to_type(series: pd.Series, dtype: Union[str, type]) -> pd.Series:
    """
    Convert a pandas Series to a specified data type.

    Parameters
    ----------
    series : pd.Series
        The Series to convert.
    dtype : Union[str, type]
        The data type to convert the series to.

    Returns
    -------
    pd.Series
        The Series converted to the specified data type.

    Example
    -------
    >>> import pandas as pd
    >>> s = pd.Series([1, 2, 3])
    >>> column_to_type(s, float)
    0    1.0
    1    2.0
    2    3.0
    dtype: float64
    """
    if dtype == "datetime":
        return pd.to_datetime(series)
    if dtype in ("float", float, "int", int):
        return pd.to_numeric(series, errors="coerce").astype(dtype)
    if dtype in ("str", "string", str):
        return series.astype(str)
    return series


def column_to_type(
    data: pd.DataFrame, column: str, dtype: Union[str, type]
) -> pd.DataFrame:
    """
    Convert a column in a DataFrame to a specified data type.

    Parameters
    ----------
    data : pd.DataFrame
        The DataFrame containing the column to convert.
    column : str
        The column to convert.
    dtype : Union[str, type]
        The data type to convert the column to.

    Returns
    -------
    pd.DataFrame
        The DataFrame with the column converted to the specified data type.

    Example
    -------
    >>> import pandas as pd
    >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    >>> column_to_type(df, 'A', float)
       A  B
    0  1  4
    1  2  5
    2  3  6
    """
    data[column] = series_to_type(data[column], dtype)
    return data
