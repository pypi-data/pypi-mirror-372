import json
from typing import Dict, List, Optional, Set, Tuple, Type, Union, Any
import pandas as pd
import pyarrow as pa
import pyarrow.dataset as ds

from ._client import client_instance
from ._constant import (
    READ_BDB_COMPATIBLE_DATA_TYPE,
    WRITE_BDB_COMPATIBLE_DATA_TYPE,
    OnDuplicates,
    DEFAULT_PARTITION_FIELD,  # noqa: F401
)


def login(
    access_key: str, secret_key: str, host: str = "bigquant.com", port: int = 17010
):
    """Authenticate with access_key and secret_key."""
    client_instance.login(access_key, secret_key, host=host, port=port)


def quota():
    """Get the quota information."""
    responses = client_instance.do_action("quota")
    results = [
        response.body.to_pybytes().decode("utf-8")
        for response in responses
        if response.body
    ]
    if results:
        return json.loads(results[0])


class QueryResult:
    """
    QueryResult is a class to represent the result of a query."""

    def __init__(
        self: "QueryResult",
        result: pa.Table,
    ):
        """
        Create a QueryResult object

        Args:
            result: the result of the query
        """
        self.result = result

    def arrow(self: "QueryResult") -> pa.Table:
        """
        Get the result as an Arrow table

        Returns:
            pa.Table: the result of the query as an Arrow table
        """
        return self.result

    def df(self: "QueryResult") -> pd.DataFrame:
        """
        Get the result as a pandas DataFrame"""
        return self.result.to_pandas()


def query(
    sql: str,
    full_db_scan: bool = False,
    filters: Optional[Dict[str, List[Any]]] = {},
    params: Optional[Dict[str, Any]] = None,
) -> QueryResult:
    """
    Execute a SQL query

    Args:
        sql: the SQL query to run, required
        full_db_scan: whether to enable full_db_scan, default to False
        filters: a dictionary of filters, where the key is the column name and the value is a list of values
        params: a dictionary of named params in sql, like if $a in sql, then params should be {"a": "value"}, default to None

    Returns:
        QueryResult: the result of the query
    """
    result = client_instance.query(sql, full_db_scan, filters, params)
    return QueryResult(result)


class DataSource:
    id: str

    def __init__(self: "DataSource", id: str) -> None:
        self.id = id

    def __repr__(self):
        return f'dai.DataSource("{self.id}")'

    @property
    def metadata(self) -> Dict[str, Any]:
        """
        获取数据源元数据

        Returns:
            Dict[str, Any]: 数据源元数据"""

        responses = client_instance.do_action("metadata", self.id.encode("utf-8"))
        results = [
            response.body.to_pybytes().decode("utf-8")
            for response in responses
            if response.body
        ]
        if results:
            return json.loads(results[0])

    def read_bdb(
        self,
        as_type: Type[READ_BDB_COMPATIBLE_DATA_TYPE] = pa.Table,
        partition_filter: Optional[Dict[str, Union[tuple, set]]] = None,
        columns: Optional[List[str]] = None,
        **kwargs,
    ) -> READ_BDB_COMPATIBLE_DATA_TYPE:
        assert self.id

        return client_instance.read_bdb(
            self.id,
            as_type,
            partition_filter=partition_filter,
            columns=columns,
            **kwargs,
        )

    @classmethod
    def write_bdb(
        cls,
        data: WRITE_BDB_COMPATIBLE_DATA_TYPE,
        *,
        id: Optional[str] = None,
        partitioning: Optional[List[str]] = None,
        indexes: Optional[List[str]] = None,
        excludes: Optional[Set[str]] = None,
        unique_together: Optional[List[str]] = None,
        on_duplicates: OnDuplicates = OnDuplicates.last,
        sort_by: Optional[List[Tuple[str, str]]] = None,
        preserve_pandas_index=False,
        docs: Optional[Dict[str, Any]] = None,
        timeout: int = 300,
        extra: str = "",
        **kwargs,
    ) -> "DataSource":
        assert data is not None

        if isinstance(data, pd.DataFrame):
            data = pa.Table.from_pandas(data, preserve_index=preserve_pandas_index)
        elif isinstance(data, ds.Dataset):
            data = data.to_table()

        return cls(
            id=client_instance.write_bdb(
                data=data,
                id=id,
                partitioning=partitioning,
                indexes=indexes,
                excludes=excludes,
                unique_together=unique_together,
                on_duplicates=on_duplicates,
                sort_by=sort_by,
                docs=docs,
                timeout=timeout,
                extra=extra,
                **kwargs,
            )
        )

    def delete(self):
        assert self.id
        responses = client_instance.do_action("delete", self.id.encode("utf-8"))
        error_message = [
            response.body.to_pybytes().decode("utf-8")
            for response in responses
            if response.body
        ]
        if error_message:
            raise Exception(",".join(error_message))
