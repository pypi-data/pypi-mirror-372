from __future__ import annotations
from datetime import datetime
from dateutil.parser import parse
from typing import Union, List, TYPE_CHECKING
import re

try:
    import numpy as np
except ImportError:
    np = None
try:
    import pandas as pd
except ImportError:
    pd = None

if TYPE_CHECKING:
    from pandas import DataFrame


def convert_to_list(arg):
    """Converts various data types to a Python list format.

    Args:
        arg: The input object to be converted to a list.

    Returns:
        A Python list containing the converted values from the input.
    """
    try:
        if arg is None:
            return None
        elif isinstance(arg, list):
            return arg
        elif isinstance(arg, (int, float, str)):
            return [arg]
        elif isinstance(arg, (tuple, set)):
            return list(arg)
        elif isinstance(arg, dict):
            return list(arg.values())
        elif np and isinstance(arg, np.ndarray):
            return arg.tolist()
        elif pd and isinstance(arg, (pd.Series, pd.Index)):
            return arg.tolist()
        return list(arg)
    except TypeError:
        raise TypeError(f'Data type {type(arg)} is not supported.')


def convert_to_dict(arg):
    """Converts various data types to a Python dictionary format.

    Args:
        arg: The input object to be converted to a dictionary.

    Returns:
        A Python dictionary containing the converted values from the input.
    """
    try:
        if arg is None:
            return None
        elif isinstance(arg, list):
            for i in range(len(arg)):
                arg[i] = convert_to_dict(arg[i])
            return arg
        elif isinstance(arg, dict):
            return arg
        elif pd and isinstance(arg, pd.DataFrame):
            return arg.to_dict(orient='records')
        elif pd and isinstance(arg, pd.Series):
            return arg.to_dict()
        return dict(arg)
    except TypeError:
        raise TypeError(f'Data type {type(arg)} is not supported.')


def convert_to_matrix(arg):
    """Converts various multidimensional data types to a Python matrix represented as
    a list of lists containing native Python numbers (int or float).

    Args:
        arg: The input object to be converted to a matrix.

    Returns:
        A Python list of lists representing the converted matrix.
    """
    try:
        if arg is None:
            return None
        elif isinstance(arg, list) and all(isinstance(row, list) for row in arg):
            return arg
        elif np and isinstance(arg, np.ndarray):
            return arg.tolist()
        elif pd and isinstance(arg, pd.DataFrame):
            return arg.values.tolist()
        elif isinstance(arg, tuple) and all(isinstance(row, (tuple, list)) for row in arg):
            return [list(row) for row in arg]
        elif hasattr(arg, '__iter__'):
            return [convert_to_matrix(item) for item in arg]
        return [arg]
    except TypeError:
        raise TypeError(f'Data type {type(arg)} is not supported.')


def date_to_iso(data: Union[datetime, str, float, int, List, dict]):
    """
    Converts a datetime, string, or numeric object to ISO format. Handles lists of such objects recursively.
    For dictionaries, it converts the 'dateTime' field to ISO format if present.

    Args:
        data (Union[datetime, str, float, int, List, dict]): The input data to convert to ISO format.

    Returns:
        Union[str, List, dict]: ISO 8601 formatted string(s) or processed dictionaries.
    """

    if isinstance(data, list):
        return [item for item in (date_to_iso(item) for item in data) if item is not None]

    if isinstance(data, dict):
        if 'dateTime' in data:
            date_time = data['dateTime']
            data['dateTime'] = date_to_iso(date_time)
        return data

    if isinstance(data, datetime):
        return data.isoformat()

    if isinstance(data, str):
        try:
            return parse(data).isoformat()
        except (ValueError, OverflowError):
            return None

    if isinstance(data, (float, int)):
        try:
            return datetime.fromtimestamp(data).isoformat()
        except (OverflowError, ValueError):
            return None

    return None


def normalize_data(data: Union[dict, list, 'DataFrame']) -> list:
    """
    Normalizes input data into a list of dictionaries with standardized keys.

    Args:
        data: Input data in various formats such as dict, list, or Pandas DataFrame.

    Returns:
        list: A list of dictionaries containing normalized data.
    """
    normalized_data = []

    regex_patterns = {
        'dateTime': re.compile(r'^(date[_\- ]*time|date|Date|DATE)$', re.IGNORECASE),
        'open': re.compile(r'^(open|Open|OPEN)$', re.IGNORECASE),
        'high': re.compile(r'^(high|High|HIGH)$', re.IGNORECASE),
        'low': re.compile(r'^(low|Low|LOW)$', re.IGNORECASE),
        'close': re.compile(r'^(close|Close|CLOSE)$', re.IGNORECASE),
        'volume': re.compile(r'^(volume|Volume|VOLUME)$', re.IGNORECASE),
        'openInterest': re.compile(r'^(open[_\- ]*interest|OpenInterest|OPENINTEREST)$', re.IGNORECASE),
    }

    def standardize_keys(item):
        standardized = {}
        for k, v in item.items():
            for target_key, pattern in regex_patterns.items():
                if pattern.match(k):
                    standardized[target_key] = v
                    break
            else:
                standardized[k] = v
        return {
            'open': standardized.get('open'),
            'high': standardized.get('high'),
            'low': standardized.get('low'),
            'close': standardized.get('close'),
            'dateTime': standardized.get('dateTime'),
            'volume': standardized.get('volume'),
            'openInterest': standardized.get('openInterest'),
        }

    if pd and isinstance(data, pd.DataFrame):
        data = data.rename(
            columns=lambda x: next(
                (target_key for target_key, pattern in regex_patterns.items() if pattern.match(x)),
                x,
            )
        )

        if 'dateTime' in data:
            data['dateTime'] = data['dateTime'].apply(lambda x: date_to_iso(x))
        normalized_data = data.to_dict(orient='records')

    elif isinstance(data, dict):
        normalized_data = [standardize_keys(data)]

    elif pd is None and 'DataFrame' in str(type(data)):
        raise ImportError('Pandas is not installed. Please install pandas to use DataFrame as input.')

    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                normalized_data.append(standardize_keys(item))
            elif isinstance(item, list):
                try:
                    keys = [
                        'open',
                        'high',
                        'low',
                        'close',
                        'dateTime',
                        'volume',
                        'openInterest',
                    ]
                    item_dict = dict(zip(keys, item))
                    normalized_data.append(standardize_keys(item_dict))
                except ValueError:
                    raise ValueError(f"Invalid list format: {item}. Expected at least 5 values for 'open', 'high', 'low', 'close', and 'dateTime'.")

    for i in normalized_data:
        if 'dateTime' in i and isinstance(i['dateTime'], (datetime, str, float, int)):
            i['dateTime'] = date_to_iso(i['dateTime'])

    return normalized_data


def preprocess_data_point(strict=True, *args, **kwargs):
    """
    Preprocesses a data point to ensure it is in the correct format (dictionary with required keys).

    Args:
        data_point (Union[dict, list, tuple, None]): The input data point in list, tuple, or dict format.
        date_time (Union[datetime, str, None]): The datetime for the data point.
        strict (bool): Whether to enforce strict validation (used for update_last_data_point).
        is_update (bool): Whether this is for an update (dateTime is not mandatory in this case).
        **kwargs: Additional keyword arguments for data point fields (e.g., open, high, low, close, etc.).

    Returns:
        dict: The processed data point as a dictionary.

    Raises:
        ValueError: If strict=True and the data point doesn't have required fields.
    """
    keys = [
        'open',
        'high',
        'low',
        'close',
        'dateTime',
        'volume',
        'openInterest',
    ]
    if args:
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            data_point = dict(zip(keys, list(args[0]) + [None] * (len(keys) - len(args[0]))))
        else:
            data_point = dict(zip(keys, list(args) + [None] * (len(keys) - len(args))))
    elif kwargs:
        data_point = kwargs.pop('data_point', None) or kwargs
    else:
        raise ValueError('No valid data provided to update_last_data_point.')

    regex_patterns = {
        'open': re.compile(r'^(open|Open|OPEN)$', re.IGNORECASE),
        'high': re.compile(r'^(high|High|HIGH)$', re.IGNORECASE),
        'low': re.compile(r'^(low|Low|LOW)$', re.IGNORECASE),
        'close': re.compile(r'^(close|Close|CLOSE)$', re.IGNORECASE),
        'dateTime': re.compile(r'^(date[_\- ]*time|time|date|Date|DATE)$', re.IGNORECASE),
        'volume': re.compile(r'^(volume|Volume|VOLUME)$', re.IGNORECASE),
        'openInterest': re.compile(r'^(open[_\- ]*interest|OpenInterest|OPENINTEREST)$', re.IGNORECASE),
    }

    def normalize_keys(item):
        """Normalize dictionary keys based on regex patterns."""
        normalized = {}
        for k, v in item.items():
            for target_key, pattern in regex_patterns.items():
                if pattern.match(k):
                    normalized[target_key] = v
                    break
            else:
                normalized[k] = v
        return normalized

    if isinstance(data_point, (list, tuple)):
        keys = ['open', 'high', 'low', 'close', 'dateTime', 'volume', 'openInterest']
        if len(data_point) < 5:
            raise ValueError('Data point tuple/list must include at least 5 values: open, high, low, close, and dateTime.')
        data_point = dict(zip(keys, list(data_point) + [None] * (len(keys) - len(data_point))))

    if isinstance(data_point, dict):
        data_point = normalize_keys(data_point)
        if isinstance(data_point.get('open'), dict):
            data_point = normalize_keys(data_point['open'])
        kwargs.update(data_point)

    if 'dateTime' in data_point:
        data_point['dateTime'] = date_to_iso(data_point['dateTime'])
    else:
        data_point['dateTime'] = datetime.now().isoformat()

    mandatory_fields = ['open', 'high', 'low', 'close']
    if strict:
        missing_fields = [key for key in mandatory_fields if data_point[key] is None]
        if missing_fields:
            raise ValueError(f'Data point must include {", ".join(mandatory_fields)}. Missing: {", ".join(missing_fields)}')

    return data_point


def is_data_sorted_chronologically(data: list) -> bool:
    """
    Check if the data is already sorted chronologically by dateTime.

    Args:
        data: List of dictionaries with dateTime field.

    Returns:
        bool: True if data is sorted chronologically, False otherwise.
    """
    if len(data) <= 1:
        return True

    for i in range(1, len(data)):
        if data[i - 1]['dateTime'] > data[i]['dateTime']:
            return False
    return True
