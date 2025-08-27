# py-xsv
py-xsv is a Python utility for reading -SV files (CSV, TSV, etc.) and converting them into dataframes.

---

## Features

- Auto-detect delimiters in CSV, TSV, or other -SV files.
- Read files into:
  - List of dictionaries (`content_dict`)
  - List of lists (`content_list`)
- Extract column data easily (`column`).
- Quickly access top/bottom rows (`head`, `tail`).
- Get dimensions (`length_width`) and headers (`headers`).
- Save -SV file to pandas DataFrames (`save_df`).

---

## Installation
```bash
pip install py-xsv
```
This needs Python 3.9 or more.

---

## Docs

### Read a CSV/TSV file as a list of dictionaries
```python
import py_xsv
data = content_dict("data.csv")
print(data[:5])
```

### Read as a list of lists
```python
import py_xsv

data = content_list("data.csv")
print(data[:5])
```

### Detect dilimiter manualy
```python
import py_xsv

with open("data.csv", "r") as f:
    lines = f.readlines()

delimiter = detect_delimiter(lines)
print(f"Detected delimiter: {delimiter}")
```

### Work with columns and headers
```python
import py_xsv

data = content_dict("data.csv")
print("Headers:", headers(data))
print("First column:", column(data, "ColumnName"))
```

### Quick access to top and bottom rows
```python
import py_xsv

data = content_list("data.csv")
print("Top 5 rows:", head(data, 5))
print("Bottom 5 rows:", tail(data, 5))
```

### Save data to a pandas DataFrame
```python
import pandas
import py_xsv

data = content_dict("data.csv")
df = save_df(data)
```
> You need to have `import pandas` before doing this

### Exceptions
- `NotSVFileError` - Used when a non -sv file is given
- `PandaError` - Errors while using pandas
- `Error` - Generic Error

---

## License
This is licensed under the WTFPL.

This means that you have permission for:
- Commercial use
- Modification
- Distribution
- Private use
- Everything basically

Under no conditions or limitations

---