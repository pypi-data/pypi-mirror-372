from enum import Enum
from typing import TypeVar

import pandas as pd
import pyarrow as pa
import pyarrow.dataset as ds

READ_BDB_COMPATIBLE_DATA_TYPE = TypeVar("READ_BDB_COMPATIBLE_DATA_TYPE", pa.Table, pd.DataFrame)
WRITE_BDB_COMPATIBLE_DATA_TYPE = TypeVar("WRITE_BDB_COMPATIBLE_DATA_TYPE", pa.Table, pd.DataFrame, ds.Dataset)
DEFAULT_PARTITION_FIELD = "__PARTITION__"


class OnDuplicates(str, Enum):
    first = "first"
    last = "last"
    error = "error"
