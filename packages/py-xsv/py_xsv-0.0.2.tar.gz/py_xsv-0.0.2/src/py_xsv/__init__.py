"""Tools for reading something serperated values files"""

import re
from collections import Counter
import csv
import sys
from io import StringIO
from typing import Annotated

class NotSVFileError(Exception):
    """Error to raise if auto-detection of delimitter fails because it was not an -SV file"""
    pass

class PandaError(Exception):
    """Errors with pandas"""
    pass

class Error(Exception):
    """Generic Error"""
    pass

# Global strict flag
strict: Annotated[bool, "Checks stricter while auto-detecting delimitter"] = True

# Global delimiter priority list
priority: Annotated[list, "Priority list for auto-detecting delimitter"] = [
    ",", "\t", "|", ";", " ", ":", "^", "~", "&", "\0",
    "¦", "§", "‖", "\x1e"  # exotic Unicode, record separator
]

def check_delim(delim, rows, header):
        """This is a helper function to the function detect_delimiter. Using detect_delimitter is probably a better choice."""
        split_rows = [row.split(delim) for row in rows]
        col_counts = [len(r) for r in split_rows]

        # Rule 1: delimiter must appear in >=95% rows
        rows_with_delim = sum(1 for r in split_rows if len(r) > 1)
        if rows_with_delim < 0.95 * len(rows):
            return False

        # Rule 2: column consistency relative to header
        H = col_counts[0]
        if H <= 1:
            return False
        consistent = sum(1 for c in col_counts if c <= H)
        exact = sum(1 for c in col_counts if c == H)
        if exact < 0.9 * len(rows):
            return False
        if consistent < 0.95 * len(rows):
            return False

        # Rule 3: header sanity check (optional)
        header_tokens = header.split(delim)
        words = sum(1 for t in header_tokens if re.search(r"[A-Za-z]", t))
        nums = sum(1 for t in header_tokens if re.fullmatch(r"[0-9.]+", t))
        if words <= nums and strict:
            return False

        # Rule 4: semantic column coherence check
        good_cols = 0
        for col_i in range(H):
            col_data = [r[col_i] for r in split_rows if len(r) > col_i]
            if not col_data:
                continue
            numeric = sum(1 for v in col_data if re.fullmatch(r"[+-]?[0-9]+(\.[0-9]+)?%?", v))
            alpha = sum(1 for v in col_data if re.search(r"[A-Za-z]", v))
            if numeric >= 0.7 * len(col_data) or alpha >= 0.7 * len(col_data):
                good_cols += 1
        if good_cols == 0:
            return False

        return True

def detect_delimiter(lines):
    """Detect the delimitter of a -sv file."""

    # Clean input
    rows = [line.strip() for line in lines if line.strip()]
    if not rows:
        if strict:
            raise NotSVFileError("Empty file")
        return None

    header = rows[0]

    # First try with priority list
    candidates = [d for d in priority if check_delim(d, rows, header)]
    if candidates:
        for p in priority:
            if p in candidates:
                return p

    # If strict, stop here
    if strict:
        raise NotSVFileError("No valid delimiter found")

    # --- Fallback autodetection ---
    sample_text = "\n".join(rows[:100])
    # Count non-alnum characters
    freq = Counter(ch for ch in sample_text if not ch.isalnum() and ch not in "'\".-")
    if not freq:
        return None

    # Sort candidates by frequency
    for delim, _ in freq.most_common():
        if check_delim(delim, rows, header):
            return delim

    return None

def content_dict(file, encode="utf-8", delim="auto"):
    """Get the content of a -sv file. Returns a list of dictionaries."""
    with open(file, "r", encoding=encode) as f:
        lines = f.readlines()
    if delim == "auto":
        delimiter = detect_delimiter(lines)
    else:
        delimiter = delim
    reader = csv.DictReader(lines, delimiter=delimiter)
    return list(reader)

def content_list(file, encode="utf-8", delim="auto"):
    """Get the content of a -sv file. Returns a list of lists."""
    with open(file, "r", encoding=encode) as f:
        lines = f.readlines()
    if delim == "auto":
        delimiter = detect_delimiter(lines)
    else:
        delimiter = delim
    reader = csv.reader(lines, delimiter=delimiter)
    return list(reader)

def length_width(data):
    """Get the length and width of the list made by content_dict or content_list."""
    rows = len(data)
    if not rows:
        return 0, 0
    first_row = data[0]
    if isinstance(first_row, dict):
        cols = len(first_row)
    else:  # list or tuple
        cols = len(first_row)
    return rows, cols

def headers(data):
    """Get the headers from a list made by content_dict or content_list as a list.
    """
    if not data:
        return []

    first_row = data[0]

    if isinstance(first_row, dict):
        return list(first_row.keys())
    elif isinstance(first_row, list) or isinstance(first_row, tuple):
        # Treat first row as header
        return list(first_row)
    else:
        raise TypeError("Unsupported data type for headers()")

def column(data, col):
    """Returns a list of the column's contents. Works for list-of-dicts or list-of-lists."""
    result = []
    if not data:
        return result
    if isinstance(data[0], dict):
        for row in data:
            result.append(row.get(col))
    else:  # list-of-lists
        for row in data:
            result.append(row[col])
    return result

def head(data, n=5):
    """Returns the top n values."""
    return data[:n]

def tail(data, n=5):
    """Returns the bottom n values."""
    return data[-n:]

def save_df(data):
    """
    Convert a list-of-lists or list-of-dicts into a pandas DataFrame.
    Requires pandas to be already imported.

    Parameters:
    - data: list of lists (with first row as header) or list of dicts

    Returns:
    - pandas DataFrame
    """
    pd = sys.modules.get("pandas")
    if pd is None:
        raise PandaError("Pandas is not imported. Please import pandas first to use to_dataframe().")

    if not data:
        return pd.DataFrame()  # empty DataFrame

    # List-of-dicts → simple conversion
    if isinstance(data[0], dict):
        df = pd.DataFrame(data)
    # List-of-lists → treat first row as header
    elif isinstance(data[0], list) or isinstance(data[0], tuple):
        header = data[0]
        rows = data[1:]  # remaining rows
        df = pd.DataFrame(rows, columns=header)
    else:
        raise PandaError("Unsupported data type for save_df()")

    return df

__all__ = [
    "NotSVFileError",
    "PandaError",
    "Error",
    "detect_delimiter",
    "content_dict",
    "content_list",
    "length_width",
    "headers",
    "column",
    "head",
    "tail",
    "save_df"
]
