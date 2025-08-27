from __future__ import annotations
import base64
from datetime import datetime
import os
import re

import requests

from lightningchart.themes import CSS_COLOR_NAMES, Color

try:
    import numpy as np
except ImportError:
    np = None
try:
    import pandas as pd
except ImportError:
    pd = None


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


def convert_to_unix_time(arg, str_format: str = None):
    """Convert various datetime formats to Unix timestamp in milliseconds.

    Args:
        arg: The datetime value(s) to convert. Acceptable types include:
            int, float, datetime, pd.Timestamp, np.datetime64, str, or list
        str_format: The expected format of the string date if `arg` is a string and not in ISO format.
            This should follow the Python `datetime.strptime` format codes.

    Returns:
        A Unix timestamp in milliseconds as an integer if a single item was passed, or a list of
        Unix timestamps in milliseconds if a list was passed.
    """
    try:
        if isinstance(arg, list):
            for i in range(len(arg)):
                arg[i] = convert_to_unix_time(arg[i])
            return arg
        if isinstance(arg, (int, float)):
            return arg
        elif isinstance(arg, datetime):
            return int(arg.timestamp() * 1000)
        elif isinstance(arg, pd.Timestamp):
            return int(arg.timestamp() * 1000)
        elif isinstance(arg, np.datetime64):
            return int(arg.astype('datetime64[ms]').astype('int64'))
        elif isinstance(arg, str):
            if str_format:
                return int(datetime.strptime(arg, str_format).timestamp() * 1000)
            else:
                return int(datetime.fromisoformat(arg).timestamp() * 1000)
    except ValueError:
        raise ValueError('Input cannot be converted to a timestamp')


def convert_to_base64(source: str) -> str:
    """
    Converts an image or video file (local or remote) to a Base64 data URI.

    Args:
        source (str): File path or URL. If the source already starts with 'data:', it is returned unchanged.

    Returns:
        str: A data URI in the form 'data:<mime_type>;base64,<base64_data>'.

    Raises:
        FileNotFoundError: If a local file is not found.
        ValueError: If the file extension is unsupported.
    """
    if source.startswith('data:'):
        return source

    if source.startswith('http://') or source.startswith('https://'):
        response = requests.get(source)
        response.raise_for_status()
        data = response.content
        mime_type = response.headers.get('Content-Type')
        if not mime_type:
            lower = source.lower()
            if lower.endswith('.mp4'):
                mime_type = 'video/mp4'
            elif lower.endswith('.webm'):
                mime_type = 'video/webm'
            elif lower.endswith('.gif'):
                mime_type = 'image/gif'
            elif lower.endswith('.jpg') or lower.endswith('.jpeg'):
                mime_type = 'image/jpeg'
            elif lower.endswith('.png'):
                mime_type = 'image/png'
            else:
                raise ValueError('Unsupported file extension for URL: ' + source)
        return f'data:{mime_type};base64,{base64.b64encode(data).decode("utf-8")}'

    if not os.path.exists(source):
        raise FileNotFoundError(f'File not found: {source}')
    with open(source, 'rb') as f:
        data = f.read()
    lower = source.lower()
    if lower.endswith('.mp4'):
        mime_type = 'video/mp4'
    elif lower.endswith('.webm'):
        mime_type = 'video/webm'
    elif lower.endswith('.gif'):
        mime_type = 'image/gif'
    elif lower.endswith('.jpg') or lower.endswith('.jpeg'):
        mime_type = 'image/jpeg'
    elif lower.endswith('.png'):
        mime_type = 'image/png'
    else:
        raise ValueError('Unsupported file extension: ' + source)
    return f'data:{mime_type};base64,{base64.b64encode(data).decode("utf-8")}'


def convert_color_to_hex(color) -> str:
    """
    Convert various color representations to a hex string.
    Supports:
    - Hex strings (6 or 8 characters)
    - CSS color names
    - Integer (0 to 4,294,967,295)
    - RGB tuples/lists (3 or 4 integers in 0-255 range)
    - RGB dicts (keys: 'r', 'g', 'b' and optional 'a')
    - lightningchart.Color objects

    Args:
        color (object): Color representation to convert.

    Returns:
        str: Hex color string in the format '#RRGGBB' or '#RRGGBBAA'.
    """
    HEX_COLOR_RE = re.compile(r'^#?([0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$')

    # lightningchart.Color object
    if isinstance(color, Color):
        return color.get_hex()

    # String input (hex or CSS color name)
    if isinstance(color, str):
        lower = color.lower()
        match = HEX_COLOR_RE.match(lower)
        if match:
            hex_value = match.group(1)
            # Keep original length - don't expand 3 or 4 digit hex
            return f'#{hex_value}'
        if lower in CSS_COLOR_NAMES:
            return CSS_COLOR_NAMES[lower]
        raise ValueError('Invalid hex or CSS color string.')

    # Tuple or list input (RGB[A])
    if isinstance(color, (tuple, list)):
        if 3 <= len(color) <= 4 and all(isinstance(v, int) and 0 <= v <= 255 for v in color):
            r, g, b = color[:3]
            a = color[3] if len(color) == 4 else 255
            return f'#{r:02x}{g:02x}{b:02x}{a:02x}'
        raise ValueError('Tuple/list color must have 3 or 4 integers in 0-255 range.')

    # Dict input (r, g, b[, a])
    if isinstance(color, dict):
        r, g, b = color.get('r'), color.get('g'), color.get('b')
        a = color.get('a', 255)
        if all(isinstance(v, int) and 0 <= v <= 255 for v in (r, g, b, a)):
            return f'#{r:02x}{g:02x}{b:02x}{a:02x}'
        raise ValueError('Dict color must have integer r, g, b (and optional a) in 0-255 range.')

    # Integer input
    if isinstance(color, int):
        if 0 <= color <= 0xFFFFFFFF:
            return f'#{color:08x}'
        raise ValueError('Integer color must be in the range 0-4294967295 (0xFFFFFFFF).')

    # Object with r, g, b, (optional a) attributes
    if not isinstance(color, (str, int, list, tuple, dict)):
        if all(hasattr(color, attr) for attr in ('r', 'g', 'b')):
            r = getattr(color, 'r')
            g = getattr(color, 'g')
            b = getattr(color, 'b')
            a = getattr(color, 'a', 255)
            if all(isinstance(v, int) and 0 <= v <= 255 for v in (r, g, b, a)):
                return f'#{r:02x}{g:02x}{b:02x}{a:02x}'

    raise ValueError(
        'Invalid color input. Pass a hex string, CSS color name, 3-4 integers (RGB[A]), dict, or object with get_hex() or r/g/b attributes.'
    )
