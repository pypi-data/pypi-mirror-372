import json
import pyarrow as pa
import pandas as pd
import pyarrow.flight as flight
from typing import Any, Dict, List, Optional, Set, Tuple, Type, Union
from ._constant import (
    READ_BDB_COMPATIBLE_DATA_TYPE,
    WRITE_BDB_COMPATIBLE_DATA_TYPE,
    OnDuplicates,
)
from .user_storage import user_storage



class DaiSdkClient:
    """数据sdk客户端"""

    @classmethod
    def instance(cls):
        """单例入口"""
        if not hasattr(cls, "_INSTANCE"):
            cls._INSTANCE = cls()
        return cls._INSTANCE

    def __init__(self) -> None:
        self._token_pair = ""
        self._user_storage = user_storage
        self.host = "bigquant.com"
        self.port = 17010
        self._client = flight.FlightClient(f"grpc+tcp://{self.host}:{self.port}")

    def _check_login(self):
        user_info = self._user_storage.get_user_id()
        if not user_info and not self._token_pair:
            raise ValueError("未找到有效的用户登录信息，请先登录")
        if user_info:
            self._login_way()
    def login(self, access_key, secret_key, *, host, port):
        self._client = flight.FlightClient(f"grpc+tcp://{host}:{port}")
        self._token_pair = self._client.authenticate_basic_token(access_key, secret_key)

    def _login_way(self):
        auth_type = self._user_storage.get_auth_type()
        if auth_type == "aksk":
            access_key = self._user_storage.get_access_key()
            secret_key = self._user_storage.get_secret_key()
            if not access_key or not secret_key:
                raise ValueError("未找到有效的Access Key或Secret Key，请重新登录")
            self._token_pair = self._client.authenticate_basic_token(access_key, secret_key)
        else:
            token = self._user_storage.get_token()
            if not token:
                raise ValueError("未找到有效的Token，请重新登录")
            self._token_pair = (b'authorization', f'Bearer {token}'.encode('utf-8'))

    def query(
        self,
        sql: str,
        full_db_scan: bool = False,
        filters: Optional[Dict[str, List[Any]]] = {},
        params: Optional[Dict[str, Any]] = None,
    ):
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
        self._check_login()
        options = flight.FlightCallOptions(headers=[self._token_pair])
        flight_params = {
            "sql": sql,
            "full_db_scan": full_db_scan,
            "filters": filters,
            "params": params,
        }
        reader = self._client.do_get(flight.Ticket(json.dumps(flight_params)), options=options)
        batches = [chunk.data for chunk in reader]
        if batches:
            bdb_table = pa.Table.from_batches(batches)
        else:
            bdb_table = reader.read_all()

        return bdb_table

    def read_bdb(
        self,
        id,
        as_type: Type[READ_BDB_COMPATIBLE_DATA_TYPE] = pa.Table,
        *,
        partition_filter: Optional[Dict[str, Union[tuple, set]]] = None,
        columns=None,
        **kwargs,
    ):
        self._check_login()
        options = flight.FlightCallOptions(headers=[self._token_pair])
        type_dict = {}
        if partition_filter is None:
            partition_filter = {}
        for key, value in partition_filter.items():
            if isinstance(value, set):
                partition_filter[key] = list(value)
                type_dict[key] = "set"
            elif not isinstance(value, tuple):
                raise ValueError("partition_filter 字典的值类型只能为 tuple 或者 set")
        params = {
            "id": id,
            "partition_filter": partition_filter,
            "columns": columns,
            "type_dict": type_dict,
            **kwargs,
        }
        reader = self._client.do_get(flight.Ticket(json.dumps(params)), options=options)
        batches = [chunk.data for chunk in reader]
        if batches:
            bdb_table = pa.Table.from_batches(batches)
        else:
            bdb_table = reader.read_all()

        # 检查字段是否存在
        fields_to_sort = []
        if "date" in bdb_table.schema.names:
            fields_to_sort.append(("date", "ascending"))
        if "instrument" in bdb_table.schema.names:
            fields_to_sort.append(("instrument", "ascending"))

        # 如果两个字段都不存在，则不排序
        if fields_to_sort:
            # 使用 pyarrow 的 sort_to_indices 来获取排序索引
            sorted_indices = pa.compute.sort_indices(bdb_table, sort_keys=fields_to_sort)
            # 使用索引来重排 Table
            bdb_table = bdb_table.take(sorted_indices)

        if as_type == pa.Table:
            return bdb_table
        elif as_type == pd.DataFrame:
            return bdb_table.to_pandas()
        else:
            raise ValueError(f"不支持的 as_type 参数: {as_type}")

    def write_bdb(
        self,
        data: WRITE_BDB_COMPATIBLE_DATA_TYPE,
        *,
        id: Optional[str] = None,
        partitioning: Optional[List[str]] = None,
        indexes: Optional[List[str]] = None,
        excludes: Optional[Set[str]] = None,
        unique_together: Optional[List[str]] = None,
        on_duplicates: OnDuplicates = OnDuplicates.last,
        sort_by: Optional[List[Tuple[str, str]]] = None,
        docs: Optional[Dict[str, Any]] = None,
        timeout: int = 300,
        **kwargs,
    ):
        self._check_login()
        options = flight.FlightCallOptions(headers=[self._token_pair])
        params = {
            "id": id,
            "partitioning": partitioning,
            "indexes": indexes,
            "excludes": excludes,
            "unique_together": unique_together,
            "on_duplicates": on_duplicates,
            "sort_by": sort_by,
            "docs": docs,
            "timeout": timeout,
            **kwargs,
        }
        descriptor = flight.FlightDescriptor.for_command(json.dumps(params))
        writer, reader = self._client.do_put(descriptor, data.schema, options=options)
        with writer:
            writer.write_table(data, 10 * 1024 * 1024)
            writer.done_writing()
            response = reader.read()
            return response.to_pybytes().decode("UTF-8")

    def do_action(self, action_type: str, action_body: bytes = b"") -> List[bytes]:
        self._check_login()
        options = flight.FlightCallOptions(headers=[self._token_pair])
        return self._client.do_action(
            flight.Action(action_type, action_body), options=options
        )


client_instance = DaiSdkClient.instance()
