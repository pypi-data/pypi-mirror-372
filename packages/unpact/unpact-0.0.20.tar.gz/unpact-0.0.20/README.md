# unpact

A lightweight library for tabulating dictionaries.

![Coverage](https://unpact.s3.amazonaws.com/coverage.svg)

## Usage

A basic example:

```python
from unpact import unwind, ColumnDef

columns: List[ColumnDef] = [
    'calendar.year',
    'calendar.date',
    'locations.location',
    'locations.x',
    'locations.y'
]

 # columns of the same child and the same length are considered 'adjacent'
 # adjacent columns are zipped together.
 # here, 'x' and 'y' are considered 'adjacent'
data = {
    'calendar': {'year': 2022, 'date': 'Aug 14'},
    'locations': [
        {'location': 'Loc1', 'x': [1,2,3,4], 'y': [1,2,3,4]},
        {'location': 'Loc2', 'x': [11,22,33,44], 'y': [11,22,33,44]},
        {'location': 'Loc3', 'x': [11], 'y': [11]},
    ],
    'ignored': "This isn't in the ColumDefs so won't be included"
}

table = unwind(data, columns)
print(pl.from_dicts(table))

--
shape: (9, 5)
┌──────┬────────┬──────────┬─────┬─────┐
│ year ┆ date   ┆ location ┆ x   ┆ y   │
│ ---  ┆ ---    ┆ ---      ┆ --- ┆ --- │
│ i64  ┆ str    ┆ str      ┆ i64 ┆ i64 │
╞══════╪═���══════╪══════════╪═════╪═════╡
│ 2022 ┆ Aug 14 ┆ Loc1     ┆ 1   ┆ 1   │
│ 2022 ┆ Aug 14 ┆ Loc1     ┆ 2   ┆ 2   │
│ 2022 ┆ Aug 14 ┆ Loc1     ┆ 3   ┆ 3   │
│ 2022 ┆ Aug 14 ┆ Loc1     ┆ 4   ┆ 4   │
│ 2022 ┆ Aug 14 ┆ Loc2     ┆ 11  ┆ 11  │
│ 2022 ┆ Aug 14 ┆ Loc2     ┆ 22  ┆ 22  │
│ 2022 ┆ Aug 14 ┆ Loc2     ┆ 33  ┆ 33  │
│ 2022 ┆ Aug 14 ┆ Loc2     ┆ 44  ┆ 44  │
│ 2022 ┆ Aug 14 ┆ Loc2     ┆ 11  ┆ 11  │
└──────┴────────┴──────────┴─────┴─────┘
```

A more complex example using ColumnSpecs:

```python
from typing import List

import polars as pl

from unpact import ColumnDef, ColumnSpec, unwind


def format_coordinate_pair(
    coords: list[int], index: int | None
) -> dict:  # Formatter functions must return a dictionary
    # Terminal value is passed to the "formatter" function
    # "index" is optionally injected if the value is a member of a list

    return {"x": coords[0], "y": coords[1], "frame": index} if coords else {"x": None, "y": None, "frame": index}


# You can pass in a pass in a 'ColumnSpec' to change the behavior of a column
# current values are 'formatter' which accepts a callable and 'name', a string which will rename the column
columns: List[ColumnDef] = [
    ColumnSpec(path="calendar.year", name="Year"),  # You can rename the column using the optional `name` kwarg
    ColumnSpec(path="calendar.date"),  # Otherwise the column will be named after the last part of the path
    ColumnSpec(path="locations.location", name="location name"),
    ColumnSpec(path="locations.coords", formatter=lambda coords: {"x": coords[0], "y": coords[1]}),
    ColumnSpec(path="locations.coords", formatter=format_coordinate_pair),
]

data = {
    "calendar": {"year": 2022, "date": "Aug 14"},
    "locations": [
        {"location": "Loc1", "coords": [[1, 1], [2, 2], [3, 3]]},
        {"location": "Loc2", "coords": [[1, 1], [2, 2], [3, 3]]},
        {"location": "Loc3", "coords": [[1, 1], [2, 2], [3, 3]]},
    ],
    "ignored": "This isn't in the ColumDefs so won't be included",
}

table = unwind(data, columns)
print(pl.from_dicts(table))


---
shape: (9, 6)
┌──────┬────────┬───────────────┬─────┬─────┬───────┐
│ Year ┆ date   ┆ location name ┆ x   ┆ y   ┆ frame │
│ ---  ┆ ---    ┆ ---           ┆ --- ┆ --- ┆ ---   │
│ i64  ┆ str    ┆ str           ┆ i64 ┆ i64 ┆ i64   │
╞══════╪════════╪═══════════════╪═════╪═════╪═══════╡
│ 2022 ┆ Aug 14 ┆ Loc1          ┆ 1   ┆ 1   ┆ 0     │
│ 2022 ┆ Aug 14 ┆ Loc1          ┆ 2   ┆ 2   ┆ 1     │
│ 2022 ┆ Aug 14 ┆ Loc1          ┆ 3   ┆ 3   ┆ 2     │
│ 2022 ┆ Aug 14 ┆ Loc2          ┆ 1   ┆ 1   ┆ 0     │
│ 2022 ┆ Aug 14 ┆ Loc2          ┆ 2   ┆ 2   ┆ 1     │
│ 2022 ┆ Aug 14 ┆ Loc2          ┆ 3   ┆ 3   ┆ 2     │
│ 2022 ┆ Aug 14 ┆ Loc3          ┆ 1   ┆ 1   ┆ 0     │
│ 2022 ┆ Aug 14 ┆ Loc3          ┆ 2   ┆ 2   ┆ 1     │
│ 2022 ┆ Aug 14 ┆ Loc3          ┆ 3   ┆ 3   ┆ 2     │
└──────┴────────┴───────────────┴─────┴─────┴───────┘

```

## API Documentation

### ColumnSpec

`ColumnSpec` is a dataclass used to define the specifications for a column in the output dataframe. It includes the following attributes:

- `path` (str): Dot-delimited path to the column in the input data.
- `name` (Optional[str]): Name of the column in the output dataframe. If not provided, the terminal path is used.
- `formatter` (Optional[ColumnFormatter]): Formatter to apply to the column data.
- `default` (Optional[Any]): Value to use if the column is missing from the input data. If not provided, `None` is used.

#### Methods

- `from_tuple(column_def: Tuple[str, ColumnSpecDict]) -> ColumnSpec`: Creates a `ColumnSpec` instance from a tuple.
- `from_str(path: str) -> ColumnSpec`: Creates a `ColumnSpec` instance from a string path.
- `from_def(column_def: ColumnDef) -> ColumnSpec`: Creates a `ColumnSpec` instance from a `ColumnDef` which can be a string, tuple, or `ColumnSpec` instance.
