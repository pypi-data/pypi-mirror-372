"""
This module creates the external funcions used in the MATER class.
"""

import datetime
import glob
import json
import logging
import os
from functools import wraps
from typing import Dict, List, Literal

import numpy as np
import pandas as pd
import requests
from data_completion_tool import dct
from pandas.core.frame import DataFrame

# Functions definition


def _log_normal(
    life_time: DataFrame, standard_deviation: DataFrame, k: datetime.datetime, offset: datetime.datetime
) -> DataFrame:
    r"""
    Compute the log-normal probability density function.

    This function calculates the log-normal distribution given the lifetime mean value, standard deviation, and a set of time points. It is typically used to model time until failure or time until an event occurs, where the event times are assumed to follow a log-normal distribution.

    :param time: :math:`t` a DataFrame containing time points at which the log-normal distribution is evaluated.
    :param life_time: :math:`\mu_{l,o,t}` a DataFrame containing the lifetime mean values.
    :param standard_deviation: :math:`\sigma_{l,o,t}` a DataFrame containing the standard deviations of the lifetime values.
    :param k: A `time` integer.
    :type time: pd.DataFrame
    :type life_time: pd.DataFrame
    :type standard_deviation: pd.DataFrame
    :type k: int
    :return: :math:`d^{log}_{l,o,t}` a DataFrame containing the computed log-normal probability densities at each time point.
    :rtype: pd.DataFrame

    Calculation
    -----------
    The probability density function for a log-normal distribution is calculated as follows:

    .. math::
        d^{log}_{l,o,t}[t,\mu_{l,o,t},\sigma_{l,o,t},k] = \frac{1}{(t - k) \sigma_{l,o,t} \sqrt{2\pi}} \exp\left(-\frac{(\log(t - k) - \mu_{l,o,t})^2}{2\sigma_{l,o,t}^2}\right)
        :label: probability_density_function

    Notes
    -----
    Indices are the :ref:`variables dimensions <dimensions>`.
    """
    time = _time_df(life_time, k, offset)
    log_normal = np.exp(
        -1 / 2 * ((np.log(time).subtract(life_time[k], axis=0)).div(standard_deviation[k], axis=0)) ** 2
    ) / (time.mul(standard_deviation[k], axis=0) * np.sqrt(2 * np.pi))
    return log_normal


def _exponential_decay(life_time: DataFrame, k: datetime.datetime, offset: datetime.datetime):
    r"""
    Calculate the exponential decay for given time points and decay lifetimes.

    :param time: :math:`t` is a `Time` DataFrame fot `time` :math:`t \ge k+1`.
    :type time: pd.DataFrame
    :param life_time: :math:`L^m_{l,o}(k)` is a `lifetime_mean_value` DataFrame at `time` :math:`k`.
    :type life_time: pd.DataFrame
    :param k: a `time` integer.
    :type k: int

    :return: :math:`d^e_{l,o,t}` a DataFrame resulting of the exponential decay function.
    :rtype: pd.DataFrame

    calculation
    -----------
    .. math::
        d^e_{l,o,t}[t,L^m_{l,o,t},k] = \frac{{e^{-\frac{{(t - k)}}{{L^m_{l,o}(k)}}}}}{{L^m_{l,o}(k)}}
        :label: exponential_decay

    Notes
    -----
    Indices are the :ref:`variables dimensions <dimensions>`.
    """
    ### WARNING: the lifetime value in life_time must me the same unit as the time_frequency
    ### ToDo : Handle automatic conversion depending on the unit of life_time and the given time_frequency
    time = _time_df(life_time, k, offset)
    exponential_decay = np.exp(-time.div(life_time[k], axis=0)).div(life_time[k], axis=0).dropna(axis=0, how="all")
    return exponential_decay


def _time_df(life_time: DataFrame, k: datetime.datetime, offset: datetime.datetime):
    col = life_time.loc[:, k + offset :].columns
    length = len(col)
    t = np.arange(1, length + 1, 1)
    time = pd.DataFrame(data=[t] * len(life_time.index), index=life_time.index, columns=col)
    time.columns.name = "time"
    return time


def profile(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        self.profiler.enable()
        retval = func(self, *args, **kwargs)
        self.profiler.disable()
        return retval

    return wrapper


def _compute_pseudoinverse(matrix):
    """Compute the Moore-Penrose pseudoinverse of a given matrix.

    This function calculates the pseudoinverse of a matrix using the NumPy linear algebra library. The Moore-Penrose pseudoinverse is a generalization of the matrix inverse for square matrices and is applicable to non-square matrices as well.

    :param matrix: A pandas DataFrame representing the matrix for which the pseudoinverse is to be computed.
    :type matrix: pd.DataFrame
    :return: The pseudoinverse of the matrix as a NumPy array. This array has the same dimensions as the input matrix transposed, and it satisfies the four Moore-Penrose conditions.
    :rtype: np.ndarray

    The computation is performed using the NumPy library's `linalg.pinv` method, which is based on Singular Value Decomposition (SVD).

    Examples
    --------
    >>> import pandas as pd
    >>> import numpy as np
    >>> df = pd.DataFrame([[1, 2], [3, 4]])
    >>> compute_pseudoinverse(df)
    array([[-2. ,  1. ],
           [ 1.5, -0.5]])

    See Also
    --------
    `np.linalg.pinv <https://numpy.org/doc/stable/reference/generated/numpy.linalg.pinv.html>`_ : NumPy's method to compute the pseudoinverse of a matrix.

    References
    ----------
    - Penrose, R. (1955). A generalized inverse for matrices. Proceedings of the Cambridge Philosophical Society, 51, 406-413.
    - Ben-Israel, A., & Greville, T. N. E. (2003). Generalized inverses: Theory and applications. Springer Science & Business Media.

    """
    return np.linalg.pinv(matrix.values)


def _groupby_sum_empty(df: pd.DataFrame | pd.Series, group_index: list):
    if df.empty:
        # Create an empty MultiIndex with the desired names
        multi_index = pd.MultiIndex.from_tuples([], names=group_index)
        if isinstance(df, pd.DataFrame):
            # Return an empty DataFrame with expected index structure
            return pd.DataFrame([], index=multi_index, dtype=float)
        elif isinstance(df, pd.Series):
            # Return an empty Series with expected index structure
            return pd.Series([], index=multi_index, dtype=float)
        else:
            raise TypeError
    else:
        # Perform the groupby operation if the Series is not empty
        return df.groupby(level=group_index).sum()  # may be parameterized if we need something else than sum()


def _loc_dynamic(df: pd.DataFrame | pd.Series, level_slice: Dict[str, List[str]]):
    """
    Efficiently filter a MultiIndex DataFrame or Series based on specific level slices.
    Still it is slower than direct DataFrame.loc so use it only if needed

    Parameters:
    - df: A pandas DataFrame or Series with a MultiIndex.
    - level_slice: A dictionary where keys are MultiIndex level names and values are lists of desired elements.

    Returns:
    - A filtered DataFrame or Series.
    """
    # Prepare the index slices
    idx = pd.IndexSlice
    slice_obj = [slice(None)] * len(df.index.levels)  # Slice all levels initially

    # Optimize filtering for each level
    for key, filter_values in level_slice.items():
        # Find the position of the level
        level_id = df.index.names.index(key)

        # Use Index's native intersection (faster than converting to list and set)
        filtered_slice = df.index.get_level_values(key).intersection(filter_values)

        # Update the slice object with the filtered values
        slice_obj[level_id] = filtered_slice

    # Apply slicing dynamically based on DataFrame or Series type
    filtered_df = df.loc[idx[tuple(slice_obj)], :] if isinstance(df, pd.DataFrame) else df.loc[idx[tuple(slice_obj)]]

    return filtered_df


def _loc_dynamic_direct(df: pd.DataFrame | pd.Series, level_slice: Dict[str, List[str]]):
    """
    Filter a MultiIndex DataFrame or Series by constructing the loc[] argument directly.

    Parameters:
    - df: A pandas DataFrame or Series with a MultiIndex.
    - level_slice: A dictionary where keys are MultiIndex level names and values are lists of desired elements.

    Returns:
    - A filtered DataFrame or Series.
    """
    # Known level order (use the order of MultiIndex levels)
    level_names = df.index.names

    # Build the tuple directly for loc[] using comprehension
    loc_args = tuple(
        df.index.get_level_values(level).intersection(level_slice[level]) if level in level_slice else slice(None)
        for level in level_names
    )

    # Apply loc[] directly
    return df.loc[loc_args]


def convert_to_datetime(column: pd.Series) -> pd.Series:
    """
    Converts a column of mixed date formats (float, string, or int) to pandas datetime.
    Handles formats like YYYYMMDD and epoch time systematically.

    :param column: pandas Series containing date values.
    :return: pandas Series with converted datetime values.
    """

    def parse_date(value):
        try:
            # Handle float and integer
            if isinstance(value, (float, int)):
                return pd.to_datetime(str(int(value)), errors="coerce", utc=True)

            # Handle strings
            elif isinstance(value, str):
                return pd.to_datetime(value, errors="coerce", utc=True)

        except Exception:
            return pd.NaT

    # Apply the parsing function to each value in the column
    return column.apply(parse_date)


def read_json(
    folder: Literal["input_data", "dimension", "variable_dimension"],
) -> pd.DataFrame:
    folder_path = os.path.join("data", folder)
    pattern = os.path.join(folder_path, "*.json")
    json_files = glob.glob(pattern)
    if folder == "input_data":
        dfs = []
        for f in json_files:
            with open(f, "r") as file:
                data = json.load(file)
                df = pd.DataFrame(data["input_data"])
                dfs.append(df)
    else:
        dfs = [pd.read_json(f, orient="records") for f in json_files]
    df = pd.concat(dfs, ignore_index=True)
    return df


def dimension_to_columns(df: pd.DataFrame):
    # expand the dict into its own columns
    expanded = df["dimensions_values"].apply(pd.Series)
    # drop the JSON-like column and join the expanded columns back
    df_expanded = df.drop(columns=["dimensions_values"]).join(expanded)
    return df_expanded


def extract_variables(df: pd.DataFrame, scenario: str | None = None) -> Dict[str, pd.DataFrame]:
    variable_names = df["variable"].unique()
    df = df[df["scenario"].isin(["historical", scenario])]
    dict_dfs = {
        var: dimension_to_columns(df[df["variable"] == var].drop(["variable", "scenario"], axis=1))
        for var in variable_names
    }
    return dict_dfs


def input_completion(
    input_name: str,
    input: pd.DataFrame,
    ds: dct.DataSet,
    variable_dimension: pd.DataFrame,
):
    input.rename({"date": "time"}, axis=1, inplace=True)  # For now it is "time" everywhere
    input["time"] = convert_to_datetime(input["time"])
    #### WARNING if the conversion is not possible it returns NaT.
    input = input.dropna()
    #### Issue with djando datetime before 1911.
    variable_aspects = variable_dimension[variable_dimension["variable"] == input_name]
    aspect_property = variable_aspects[["dimension", "property"]].set_index("dimension").T.to_dict("list")
    completed_input = ds.completion(input, aspect_property)

    return completed_input


def api_session_auth(api_url: str, username: str, password: str) -> requests.Session | None:
    # Create a session object to maintain cookies
    session = requests.Session()

    # Step 2: Log in to the Django site
    login_url = f"{api_url}/api-auth/login/?next=/"
    # Step 1: Get the CSRF token (required for Django session authentication)
    try:
        response = session.get(login_url)
        response.raise_for_status()  # Raise exception for HTTP errors

        # Get CSRF token from cookies
        if "csrftoken" in session.cookies:
            csrf_token = session.cookies["csrftoken"]
        else:
            # Some Django configurations use other names
            csrf_token = session.cookies.get("csrf", session.cookies.get("_csrf"))

        if not csrf_token:
            logging.error("Could not retrieve CSRF token")
            return None

        # Step 2: Login with credentials
        login_data = {
            "username": username,
            "password": password,
            "csrfmiddlewaretoken": csrf_token,
        }

        # Add Referer header to satisfy Django's CSRF protection
        headers = {"Referer": login_url, "X-CSRFToken": csrf_token}

        # Submit login request
        response = session.post(login_url, data=login_data, headers=headers, allow_redirects=True)

        # Check if login was successful
        if response.status_code == 200:
            # Check if we're still on the login page (failed login)
            if "login" in response.url.lower() and "password" in response.text.lower():
                logging.error("Login failed: Invalid credentials")
                return None
            else:
                logging.info("Login successful")
                return session
        else:
            logging.error(f"Login failed with status code: {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        logging.error(f"Error during authentication: {e}")
        return None


def get_data_from_api(session: requests.Session, api_url: str, endpoint: str):
    # Use the authenticated session to get data
    url = f"{api_url}/{endpoint}/?format=json"
    response = session.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        logging.warning(f"Failed to get data: {response.status_code}")
        logging.warning(response.text)
        return None
