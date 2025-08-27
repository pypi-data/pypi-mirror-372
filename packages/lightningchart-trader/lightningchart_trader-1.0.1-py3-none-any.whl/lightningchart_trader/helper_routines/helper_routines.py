import os
import pandas as pd
import csv
import io


def calculate_heikin_ashi_values(xohlc_data: list[list[int | float]]):
    """Calculates Heikin Ashi values based on the given dataset.

    Args:
        xohlc_data (list[list[int | float]]): XOHLC dataset to calculate from.

    Returns:
        List of Heikin Ashi values.
    """
    ha_values = []

    for i in range(len(xohlc_data)):
        if i == 0:
            ha_values.append(
                [
                    xohlc_data[i][0],
                    (xohlc_data[i][1] + xohlc_data[i][4]) / 2,
                    max(xohlc_data[i][1], xohlc_data[i][2], xohlc_data[i][4]),
                    min(xohlc_data[i][1], xohlc_data[i][3], xohlc_data[i][4]),
                    (xohlc_data[i][1] + xohlc_data[i][2] + xohlc_data[i][3] + xohlc_data[i][4]) / 4,
                ]
            )
        else:
            ha_values.append(
                [
                    xohlc_data[i][0],
                    (ha_values[i - 1][1] + ha_values[i - 1][4]) / 2,
                    max(xohlc_data[i][1], xohlc_data[i][2], xohlc_data[i][4]),
                    min(xohlc_data[i][1], xohlc_data[i][3], xohlc_data[i][4]),
                    (xohlc_data[i][1] + xohlc_data[i][2] + xohlc_data[i][3] + xohlc_data[i][4]) / 4,
                ]
            )

    return ha_values


def extract_close_values(xohlc_data: list[list[int | float]]):
    """Extracts all Close values from the current dataset.

    Args:
        xohlc_data (list[list[int | float]]): XOHLC data values to extract from.

    Returns:
        List of Close values, or empty list if unable to extract.
    """
    close_values = []

    if len(xohlc_data) > 0:
        for i in range(len(xohlc_data)):
            close_values.append(xohlc_data[i][4])

    return close_values


def extract_high_values(xohlc_data: list[list[int | float]]):
    """Extracts all High values from the current dataset.

    Args:
        xohlc_data (list[list[int | float]]): XOHLC data values to extract from.

    Returns:
        List of High values, or empty list if unable to extract.
    """
    high_values = []

    if len(xohlc_data) > 0:
        for i in range(len(xohlc_data)):
            high_values.append(xohlc_data[i][2])

    return high_values


def extract_low_values(xohlc_data: list[list[int | float]]):
    """Extracts all Low values from the current dataset.

    Args:
        xohlc_data (list[list[int | float]]): XOHLC data values to extract from.

    Returns:
        List of Low values, or empty list if unable to extract.
    """
    low_values = []

    if len(xohlc_data) > 0:
        for i in range(len(xohlc_data)):
            low_values.append(xohlc_data[i][3])

    return low_values


def extract_open_values(xohlc_data: list[list[int | float]]):
    """Extracts all Open values from the current dataset.

    Args:
        xohlc_data (list[list[int | float]]): XOHLC data values to extract from.

    Returns:
        List of Open values, or empty list if unable to extract.
    """
    open_values = []

    if len(xohlc_data) > 0:
        for i in range(len(xohlc_data)):
            open_values.append(xohlc_data[i][1])

    return open_values


def extract_position_values(xohlc_data: list[list[int | float]]):
    """Extracts all position values (X-values) from the current dataset.

    Args:
        xohlc_data (list[list[int | float]]): XOHLC data values to extract from.

    Returns:
        List of positions values, or empty list if unable to extract.
    """
    x_values = []

    if len(xohlc_data) > 0:
        for i in range(len(xohlc_data)):
            x_values.append(xohlc_data[i][0])

    return x_values


def convert_to_xohlc(data):
    """
    Converts various data formats (CSV, list of dicts, list of lists, DataFrame) into XOHLC format.
    The function is **case insensitive** for column names (e.g., "Open" == "open" == "OPEN").

    Args:
        data (str | list | dict | DataFrame):
            - Path to CSV file (str)
            - List of dictionaries (list[dict])
            - Single dictionary (dict)
            - List of lists (list[list])
            - Pandas DataFrame (DataFrame)

    Returns:
        list: Data in XOHLC format -> [[Index, Open, High, Low, Close], ...]

    Example Usage:
    --------------
    >>> convert_to_xohlc("your_csv_file.csv")
    >>> convert_to_xohlc(df)  # Pandas DataFrame
    >>> convert_to_xohlc([{"OPEN":1.1, "HIGH":1.2, "LOW":1.0, "CLOSE":1.15, "DATE":"Jan 1, 1970"}])  # List of Dicts
    >>> convert_to_xohlc([[1.1, 1.2, 1.0, 1.15, "Jan 1, 1970"]])  # List of Lists
    """

    xohlc_data = []

    if isinstance(data, str) and os.path.exists(data):
        with open(data, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            fieldnames = {col.lower(): col for col in reader.fieldnames}

            required_columns = {'open', 'high', 'low', 'close'}
            if not required_columns.issubset(fieldnames.keys()):
                raise ValueError(f'CSV file must contain columns: {required_columns}')

            for idx, row in enumerate(reader):
                xohlc_data.append(
                    [
                        idx,
                        float(row[fieldnames['open']]),
                        float(row[fieldnames['high']]),
                        float(row[fieldnames['low']]),
                        float(row[fieldnames['close']]),
                    ]
                )

    elif isinstance(data, pd.DataFrame):
        data.columns = data.columns.str.lower()

        if not all(col in data.columns for col in ['open', 'high', 'low', 'close']):
            raise ValueError("DataFrame must contain 'Open', 'High', 'Low', 'Close' columns.")

        xohlc_data = [[idx, row['open'], row['high'], row['low'], row['close']] for idx, (date, row) in enumerate(data.iterrows())]

    elif isinstance(data, list) and all(isinstance(item, dict) for item in data):
        for idx, row in enumerate(data):
            row = {k.lower(): v for k, v in row.items()}

            if all(key in row for key in ['open', 'high', 'low', 'close']):
                xohlc_data.append(
                    [
                        idx,
                        float(row['open']),
                        float(row['high']),
                        float(row['low']),
                        float(row['close']),
                    ]
                )

    elif isinstance(data, dict):
        data = {k.lower(): v for k, v in data.items()}

        if all(key in data for key in ['open', 'high', 'low', 'close']):
            xohlc_data.append(
                [
                    0,
                    float(data['open']),
                    float(data['high']),
                    float(data['low']),
                    float(data['close']),
                ]
            )

    elif isinstance(data, list) and all(isinstance(item, list) and len(item) >= 4 for item in data):
        for idx, row in enumerate(data):
            xohlc_data.append([idx, float(row[0]), float(row[1]), float(row[2]), float(row[3])])

    else:
        raise TypeError('Unsupported data format. Provide CSV, DataFrame, list of dicts, list of lists, or a single dictionary.')

    return xohlc_data


def read_csv_string(csv_input: str, start_date=None, end_date=None, delimiter=','):
    """
    Parses a CSV string or file into separate OHLCV arrays, similar to JS `readCsvString()`.

    Args:
        csv_input (str): Either a **file path** or a **raw CSV string**.
        start_date (str | None): Optional filter, exclude rows **before** this date (Format: "YYYY-MM-DD").
        end_date (str | None): Optional filter, exclude rows **after** this date (Format: "YYYY-MM-DD").
        delimiter (str): The delimiter used in the CSV (default: `,`).

    Returns:
        list: A list containing:
            - Array of date strings
            - Array of Open values
            - Array of High values
            - Array of Low values
            - Array of Close values
            - Array of Volumes (or empty if not in CSV)
            - Array of Open Interests (or empty if not in CSV)

    Example Usage:
    --------------
    >>> csv_data = '''Date,Open,High,Low,Close,Volume,OpenInterest
    ... 2024-01-01,100,105,99,104,5000,200
    ... 2024-01-02,104,106,102,105,5500,210
    ... 2024-01-03,105,107,103,106,6000,220'''
    >>> parsed_data = read_csv_string(csv_data, start_date="2024-01-02")
    >>> print(parsed_data)

    >>> parsed_file = read_csv_string("your_csv_file.csv")
    >>> print(parsed_file)
    """

    if os.path.exists(csv_input):
        with open(csv_input, 'r', encoding='utf-8') as file:
            csv_string = file.read()
    else:
        csv_string = csv_input  # Treat as raw CSV string

    # Initialize lists for output
    dates, opens, highs, lows, closes, volumes, open_interests = (
        [],
        [],
        [],
        [],
        [],
        [],
        [],
    )

    reader = csv.DictReader(io.StringIO(csv_string), delimiter=delimiter)

    # Normalize column names (case-insensitive)
    fieldnames = {col.lower(): col for col in reader.fieldnames}

    required_columns = {'date', 'open', 'high', 'low', 'close'}
    if not required_columns.issubset(fieldnames.keys()):
        raise ValueError(f'CSV must contain columns: {required_columns}')

    has_volume = 'volume' in fieldnames
    has_open_interest = 'openinterest' in fieldnames

    # Iterate through rows and apply date filtering
    for row in reader:
        row_date = row[fieldnames['date']]
        if start_date and row_date < start_date:
            continue  # Skip rows before start_date
        if end_date and row_date > end_date:
            continue  # Skip rows after end_date

        dates.append(row_date)
        opens.append(float(row[fieldnames['open']]))
        highs.append(float(row[fieldnames['high']]))
        lows.append(float(row[fieldnames['low']]))
        closes.append(float(row[fieldnames['close']]))

        if has_volume:
            volumes.append(float(row[fieldnames['volume']]))
        if has_open_interest:
            open_interests.append(float(row[fieldnames['openinterest']]))

    return [dates, opens, highs, lows, closes, volumes, open_interests]


def convert_hex_to_rgba(hex_color):
    """Convert a HEX color string to an RGBA tuple.

    Args:
        hex_code (str): A HEX color code in the format '#RRGGBB' or '#RRGGBBAA'.

    Returns:
        tuple: A tuple (R, G, B, A) where R, G, B, and A are integers between 0 and 255.
               If no alpha channel is provided in the HEX string, the alpha will be excluded from the result.
    """
    hex_color = hex_color.lstrip('#')
    length = len(hex_color)
    if length == 6:
        r, g, b = (
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16),
        )
        return r, g, b
    elif length == 8:
        r, g, b, a = (
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16),
            int(hex_color[6:8], 16),
        )
        return r, g, b, a
    else:
        raise ValueError('Invalid HEX color format')


def convert_rgba_to_hex(r, g, b, a=None):
    """Convert an RGB or RGBA color value to a HEX color string.

    Args:
        r (int): Red component, an integer between 0 and 255.
        g (int): Green component, an integer between 0 and 255.
        b (int): Blue component, an integer between 0 and 255.
        a (int, optional): Alpha component, an integer between 0 and 255.
                           If not provided, the alpha will be excluded from the result.

    Returns:
        str: A HEX string representing the color in the format '#RRGGBB' or '#RRGGBBAA'.
    """
    if a is None:
        return '#{:02x}{:02x}{:02x}'.format(r, g, b)
    else:
        return '#{:02x}{:02x}{:02x}{:02x}'.format(r, g, b, a)
