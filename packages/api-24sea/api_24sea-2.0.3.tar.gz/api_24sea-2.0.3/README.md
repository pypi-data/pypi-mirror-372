# API 24SEA

**api_24sea** is a Python project designed to provide aid for the
interaction with data from the [24SEA
API](https://api.24sea.eu/docs/v1).

## Installation

The package supports Python 3.8 and above. To install it, run the
following command in your terminal:

``` shell
pip install api_24sea
```

## DataSignals Usage

The following example shows the classical usage of the datasignals
module.

-   The first step is to import the package and the necessary libraries.
-   Then, the environment variables are loaded from a `.env`
    file. This step is optional, since if any of the following names for
    user and password in the system, the package will authenticate
    automatically.
    * `"API_24SEA_USERNAME"`, `"24SEA_API_USERNAME"`, `"TWOFOURSEA_API_USERNAME"`,
      `"API_TWOFOURSEA_USERNAME"` for the username.
    * `"API_24SEA_PASSWORD"`, `"24SEA_API_PASSWORD"`, `"TWOFOURSEA_API_PASSWORD"`,
        `"API_TWOFOURSEA_PASSWORD"` for the password.
-   After that, API dataframe is initialized.
-   Finally, the user can get data from the API. The dataframe will
    authenticate lazily if the environment variables are loaded, or the
    user can authenticate manually before performing the data retrieval.

### Importing the package

``` python
# %%
# **Package Imports**
# - From the Python Standard Library
import logging
import os
import sys

# - From third party libraries
import pandas as pd
import dotenv  # <-- Not necessary to api_24sea per se, but useful for
               #     loading environment variables. Install it with
               #     `pip install python-dotenv`

# - Local imports
from api_24sea.version import __version__, parse_version
import api_24sea
```

``` python
# %%
# **Package Versions**
print("Working Folder: ", os.getcwd())
print(f"Python Version: {sys.version}")
print(f"Pandas Version: {pd.__version__}")
print(f"Package {parse_version(__version__)}")
# **Notebook Configuration**
logging.basicConfig(level=logging.INFO)
```

### Setting up the environment variables (optional)

This step assumes that you have a file structure similar to the
following one:

``` shell
.
├── env
│   └── .env
├── notebooks
│   └── example.ipynb
└── requirements.txt
```

The [.env]{.title-ref} file should look like this:

``` shell
API_24SEA_USERNAME=your_username
API_24SEA_PASSWORD=your_password
```

With this in mind, the following code snippet shows how to load the
environment variables from the [.env]{.title-ref} file:

``` python
# %%
# **Load Environment Variables from .env File**
_ = dotenv.load_dotenv("../env/.env")
if _:
    print("Environment Variables Loaded Successfully")
    print(os.getenv("API_24SEA_USERNAME"))
    # print(os.getenv("API_24SEA_PASSWORD"))
else:
    raise Exception("Environment Variables Not Loaded")
```

### Initializing an empty dataframe

Initializing an empty dataframe is necessary to use the API, as here is
where the data will be stored.

``` python
# %%
# **DataFrame initialization**
# The empty DataFrame is created beforehand because it needs to authenticate
# with the API to fetch the data.
df = pd.DataFrame()
```

#### Authentication (optional)

If any of the following names for user and password in the system, the package
will authenticate automatically.
* `"API_24SEA_USERNAME"`, `"24SEA_API_USERNAME"`, `"TWOFOURSEA_API_USERNAME"`,
    `"API_TWOFOURSEA_USERNAME"` for the username.
* `"API_24SEA_PASSWORD"`, `"24SEA_API_PASSWORD"`, `"TWOFOURSEA_API_PASSWORD"`,
    `"API_TWOFOURSEA_PASSWORD"` for the password.

The user can also authenticate manually by calling the `authenticate` method
from the DataFrame.

``` python
# %%
# **Authentication**
df.datasignals.authenticate("some_other_username", "some_other_password")
```

Alternatively, the user can authenticate with the API on DataFrame instantiation:

``` python
# %%
# **DataFrame initialization with authentication**
df = pd.DataFrame().datasignals.authenticate("some_other_username",
                                             "some_other_password")
```

#### Checking the available metrics

``` python
# %%
# **Metrics Overview**
# The metrics overview is a summary of the metrics available in the API and
# can be accessed from a hidden method in the DataSignals class.
df.datasignals._DataSignals__api.metrics_overview
# It will show all the available metrics with the corresponding units
# and the time window for which the user is allowed to get data
```

### Getting sample data from the API

After loading the environment variables and authenticating with the API,
the user can get data from [24SEA API
endpoints](https://api.24sea.eu/docs/v1/).

The data is retrieved and stored in the DataFrame. All the metrics are
stored in separate columns, and the timestamps are set as the index of
the DataFrame.

The data retrieval is done by specifying the sites or the locations or
both, the metrics, and timestamps.

-   Sites: Case insensitive, it can either match [site]{.title-ref} or
    [site_id]{.title-ref}. It is an optional parameter.
-   Locations: Case insensitive, it can either match
    [location]{.title-ref} or [location_id]{.title-ref}. It is an
    optional parameter.
-   Metrics: Case insensitive, it can be a partial match of the metric
    name. If the site and location are specified, and metrics equals
    `all`, all the \"allowed\" metrics for the specified site and
    location will be retrieved.
-   Timestamps: Timezone-aware datetime, strings in ISO 8601 format, or
    shorthand strings compatible with the [shorthand_datetime
    package](https://pypi.org/project/shorthand-datetime/).

``` python
# %%
# **Data Retrieval**
sites = ["wf"]

locations = ["a01", "a02"]

metrics = ["mean WinDSpEed", "mean pitch", "mean-Yaw", "mean Power"]
# Assigning metrics="all" will retrieve all the metrics available for the
# specified sites and locations.

start_timestamp = "2020-03-01T00:00:00Z"
end_timestamp = "2020-06-01T00:00:00Z"

df.datasignals.get_data(sites, locations, metrics,
                        start_timestamp, end_timestamp)
```

#### Checking the metrics selected and the data

``` python
# %%
df.datasignals.selected_metrics
df
```

### Split the data by site and location

The `as_dict` method is used to split the data by site and location and
return a dictionary of dictionaries of DataFrames.

``` python
# %%
# Data is a dictionary of dictionary of DataFrames in the shape of:
# {
#   "site1": {
#     "location1": DataFrame,
#     "location2": DataFrame,
#     ...
#   },
#   ...
# }
data = df.datasignals.as_dict()
# %%
# Retrieve the DataFrame for the windfarm WFA01 only
data["windfarm"]["WFA02"]
```

If `df` was defined using local data, rather than from API call, the
user can still use the `as_dict` method to split the data by site and
location by passing a `metrics_map` dataframe (i.e., the metrics
overview table) from the [datasignals
app](https://api.24sea.eu/datasignals/). For example:

``` python
import pandas as pd
import api_24sea
df = pd.DataFrame({
    "timestamp": ["2021-01-01", "2021-01-02"],
    "mean_WF_A01_windspeed": [10.0, 11.0],
    "mean_WF_A02_windspeed": [12.0, 13.0]
})
metrics_map = pd.DataFrame({
    "site": ["wf", "wf"],
    "location": ["a01", "a02"],
    "metric": ["mean_WF_A01_windspeed", "mean_WF_A02_windspeed"]
})
df.datasignals.as_dict(metrics_map)
# output
# {
#     "wf": {
#         "a01": pd.DataFrame({
#             "timestamp": ["2021-01-01", "2021-01-02"],
#             "mean_WF_A01_windspeed": [10.0, 11.0]
#         }),
#         "a02": pd.DataFrame({
#             "timestamp": ["2021-01-01", "2021-01-02"],
#             "mean_WF_A02_windspeed": [12.0, 13.0]
#         })
#     }
# }
```

<!--
## Core API Usage

The core API module is designed to provide a more direct interaction
with the [24SEA API](https://api.24sea.eu/docs/v1) and is the base for
the DataSignals module.

The following example shows the classical usage of the core API module,
which can be integrated within other standalone classes or functions.

-   The first step is to import the package and the necessary libraries.
-   Then, the environment variables are loaded from a [.env]{.title-ref}
    file.
-   After that, the package is initialized and the user is authenticated
    with the API.
-   Finally, the user can get data from the API.

The first two steps are the same as in the DataSignals module and will
not be repeated here.

### Authenticating with the API (optional)

The authentication step is performed automatically if the environment
variables `API_24SEA_USERNAME` and `API_24SEA_PASSWORD` are loaded. The
user can also authenticate manually by calling the `authenticate` method
from the API.

This step is optional, since the API is able to authenticate lazily if
the environment variables are loaded, or the user can authenticate
manually.

``` python
# %%
# Package Imports
from api_24sea.datasignals.core import API
# %%
# **Authentication**
api = API()
api.authenticate("some_other_username", "some_other_password")
```

#### Checking the available metrics

``` python
# %%
# **Metrics Overview**
# The metrics overview is a summary of the metrics available in the API and
# can be accessed from a hidden method in the DataSignals class.
api.metrics_overview
# It will show all the available metrics with the corresponding units
# and the time window for which the user is allowed to get Data
```

### Getting sample data from the API

After loading the environment variables and authenticating with the API,
the user can get data from [24SEA API
endpoints](https://api.24sea.eu/docs/v1/).

The retrieved data can be retrieved in multiple formats, depending on
the combination of the following three options:

-   `as_dict`: If True, any dataframe output is returned as a dictionary
    according to the following formula:
    `dataframe.reset_index().to_dict('records')`.
-   `as_star_schema`: If True, the data is returned in a star schema
    format, i.e. a dictionary with the following keys: `DimCalendar`,
    `DimWindFarm`, `DimDataGroup`, `DimMetric`, and `FactData`.
-   `outer_join_on_timestamp`: if True, the response from each metric is
    joined on the timestamp which is then set as the index of DataFrame.
    This option will necessarily drop the `location` and `site` columns
    from the DataFrame, but they can still be retrieved from the metrics
    overview. If False, the response from each metric is stored in a
    separate DataFrame and the `site` and `location` columns are kept.
    This means that the DataFrame will be \"diagonal\" with repeated
    timestamps (as many times as the number of queried (locations,
    sites) pairs).

Therefore, the following combinations are possible:

-   Single `pandas.DataFrame`: `outer_join_on_timestamp=True`,
    `as_star_schema=False`, and `as_dict=False`. This is the default
    behavior.
-   `dict[str, Union[float, dict[str, Any]]]`:
    `outer_join_on_timestamp=False`, `as_star_schema=False`, and
    `as_dict=True`.
-   Star schema as `dict[str, pandas.Dataframe]`:
    `outer_join_on_timestamp` is irrelevant `as_star_schema=True`, and
    `as_dict=False`.
-   Star schema as `dict[str, dict[str, Any]]`:
    `outer_join_on_timestamp` is irrelevant `as_star_schema=True`, and
    `as_dict=True`.

``` python
# %%
# **Data Retrieval**
sites = ["wf"]

locations = ["a01", "a02"]

metrics = ["mean WinDSpEed", "mean pitch", "mean-Yaw", "mean Power"]

start_timestamp = "2020-03-01T00:00:00Z"
end_timestamp = "2020-06-01T00:00:00Z"

data = api.get_data(sites, locations, metrics,
                    start_timestamp, end_timestamp)
```

### Data as Star Schema

#### Overview

The data as star schema feature is designed to provide a more
user-friendly experience when getting data for BI purposes. It is
implemented only for the core API module.

``` python
from api_24sea.datasignals.core import API

# %%
# **Star schema**

# %%
# **Data Retrieval**
sites = ["wf"]

locations = ["a01", "a02"]

metrics = ["mean WinDSpEed", "mean pitch", "mean-Yaw", "mean Power"]

start_timestamp = "2020-03-01T00:00:00Z"
end_timestamp = "2020-06-01T00:00:00Z"

star_schema = api.get_data(sites, locations, metrics,
                           start_timestamp, end_timestamp, as_star_schema=True)
```

This command is equivalent to the following:

``` python
from api_24sea.datasignals.core import to_star_schema, API

# %%
# **Data Retrieval**
api = API()

sites = ["wf"]

locations = ["a01", "a02"]

metrics = ["mean WinDSpEed", "mean pitch", "mean-Yaw", "mean Power"]

start_timestamp = "2020-03-01T00:00:00Z"
end_timestamp = "2020-06-01T00:00:00Z"

data = api.get_data(sites, locations, metrics,
                    start_timestamp, end_timestamp)

star_schema = to_star_schema(data, api.selected_metrics(data).reset_index())
```

The `star_schema` variable will contain a dictionary with the following
keys:

-   `DimCalendar`: A DataFrame with the timestamps and their
    corresponding calendar information.
-   `DimWindFarm`: A DataFrame with the wind farm information (site an
    locations)
-   `DimDataGroup`: A DataFrame with the metric group information (e.g.
    TP, SCADA)
-   `DimMetric`: A DataFrame with the metric information (e.g. mean
    pitch, mean power)
-   `FactData`: A DataFrame with the data itself.
-   `FactPivotData`: A DataFrame with the data pivoted by metric.

## Data as Category-Value

The data as category-value feature is designed to reshape the data so
that all the information for a metric is stored in a single row. It is
implemented only for the core API module.

``` python
# %%
# **Data Retrieval**
from api_24sea.datasignals.core import to_category_value
sites = ["wf"]

locations = ["a01", "a02"]

metrics = ["mean WinDSpEed", "mean pitch", "mean-Yaw", "mean Power"]

start_timestamp = "2020-03-01T00:00:00Z"
end_timestamp = "2020-06-01T00:00:00Z"

data = api.get_data(sites, locations, metrics,
                    start_timestamp, end_timestamp)

category_value = to_category_value(data, api.selected_metrics(data).reset_index())
```

## Fatigue Extra

The fatigue extra is a new feature that allows the user to analyze
cycle-count metrics.

### Installation

The fatigue extra is compatible with Python versions from 3.8 to 3.10, and
installs the [py-fatigue](https://owi-lab.github.io/py_fatigue/) and
[swifter](https://github.com/jmcarpenter2/swifter) packages.

To install this extra, run the following command in your terminal:

``` shell
pip install api_24sea[fatigue]
```

### Usage

Suppose you have already defined a `pandas.DataFrame`{.interpreted-text
role="class"} and authenticated with the API. For instructions on how to
do this, refer to the
`previous section <quick-start-01>`{.interpreted-text role="ref"}.

#### Importing the fatigue extra

``` python
# %%
# - Local imports
from api_24sea.datasignals import fatigue
```

##### Checking the available metrics after authentication

If your *Metrics Overview* table shows metrics whose name starts with
`CC_`, then the fatigue extra will be available for use.

#### Getting data

Similar to the data retrieval process described in the **DataSignals Usage** section,
the data retrieval process for the fatigue extra follows the same steps. The
only difference is that the selected metrics must include cycle-counts
(CC).

``` python
# %%
# **Data Retrieval**
# Besides SCADA data, we will query cycle-count metrics, which are available
# by looking for "CC" (cycle-count) and ["Mtn", "Mtl"] (i.e. Normal and
# Lateral Bending moment).

sites = ["wf"]
locations = ["a01", "a02"]
metrics = ["mean WinDSpEed", "mean pitch", "mean-Yaw", "mean power",
           "cc mtn", "cc mtl"]

start_timestamp = "2020-03-01T00:00:00Z"
end_timestamp = "2020-06-01T00:00:00Z"

df.datasignals.get_data(sites, locations, metrics,
                        start_timestamp, end_timestamp, as_dict=False)
```

#### Analyzing cycle-count metrics

Converting the cycle-count JSON objects to
[`py_fatigue.CycleCount`](https://owi-lab.github.io/py_fatigue/api/cycle_count/cycle_count_.html#py_fatigue.cycle_count.cycle_count.CycleCount) objects is the
first step in the fatigue analysis. This is done by calling the
[`api_24sea.datasignals.fatigue.Fatigue.cycle_counts_to_objects`](https://owi-lab.github.io/py_fatigue/api/cycle_count/cycle_count_.html#py_fatigue.cycle_count.cycle_count.CycleCount) method.

``` python
# %%
# **Fatigue Analysis**
# The fatigue analysis is done by calling the cycle_counts_to_objects() method
# from the fatigue accessor.
try:
    df.fatigue.cycle_counts_to_objects()
except ImportError as ie:
    print(f"\033[31;1mImportError\033[22m: {ie}")
```

At this point, you can treat your
[`py_fatigue.CycleCount`](https://owi-lab.github.io/py_fatigue/api/cycle_count/cycle_count_.html#py_fatigue.cycle_count.cycle_count.CycleCount) objects as you
would normally do with [py-fatigue](https://owi-lab.github.io/py_fatigue/).

For more information, check py-fatigue\'s [beginner\'s
guide](https://owi-lab.github.io/py_fatigue/user/01-absolute-noob.html). -->

## Project Structure

```shell
.
├── .azure/
├── api_24sea/
│   ├── __init__.py
│   ├── datasignals/
│   │   ├── __init__.py
│   │   ├── fatigue.py
│   │   └── schemas.py
│   ├── core.py
│   ├── exceptions.py
│   ├── singleton.py
│   ├── utils.py
│   └── version.py
├── tests/
├── docs/
├── notebooks/
├── pyproject.toml
├── LICENSE
├── VERSION
└── README.md
```

## License

The package is licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html).
