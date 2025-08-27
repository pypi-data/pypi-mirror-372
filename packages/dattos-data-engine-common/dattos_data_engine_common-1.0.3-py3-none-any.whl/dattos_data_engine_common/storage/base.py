from abc import ABC, abstractmethod
from typing import Optional

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from fsspec import AbstractFileSystem

from dattos_data_engine_common.models import Column


class StorageStrategy(ABC):
    _fs: AbstractFileSystem
    _connection_string: str
    _data_type: dict[str, pa.DataType] = {
        "Text": pa.string(),
        "Float": pa.float64(),
        "Date": pa.date32(),
        "Integer": pa.int64(),
        "DateTime": pa.timestamp("ns"),
    }

    def __init__(self, connection_string: str):
        self._connection_string = connection_string
        self._fs = self.get_filesystem()

    def get_storage_options(self) -> dict:
        return self._fs.storage_options

    @abstractmethod
    def get_filesystem(self) -> AbstractFileSystem:
        raise NotImplementedError(
            "Este método deve ser implementado pela estratégia de armazenamento específica."
        )

    @abstractmethod
    def read_dataframe(self, path: str) -> pd.DataFrame:
        raise NotImplementedError(
            "Este método deve ser implementado pela estratégia de armazenamento específica."
        )

    @abstractmethod
    def write_dataframe(
        self, df: pd.DataFrame, path: str, columns: Optional[list[Column]] = None
    ):
        if columns:
            expected_schema = self._get_arrow_schema(columns)

            self._validate_schema(df, expected_schema)

            table = pa.Table.from_pandas(df, schema=expected_schema)
            pq.write_table(table, path, filesystem=self._fs)
        else:
            df.to_parquet(path, storage_options=self.get_storage_options(), index=False)

    @abstractmethod
    def exists_file(self, path: str) -> bool:
        raise NotImplementedError(
            "Este método deve ser implementado pela estratégia de armazenamento específica."
        )

    @abstractmethod
    def delete_file(self, path: str):
        raise NotImplementedError(
            "Este método deve ser implementado pela estratégia de armazenamento específica."
        )

    @abstractmethod
    def copy_file(self, source_path: str, target_path: str):
        raise NotImplementedError(
            "Este método deve ser implementado pela estratégia de armazenamento específica."
        )

    def _parse_connection_string(self) -> dict:
        return dict(
            item.split("=", 1)
            for item in self._connection_string.split(";")
            if "=" in item
        )

    def _get_arrow_schema(self, columns: list[Column]):
        return pa.schema(
            [(column.name, self._data_type[column.data_type]) for column in columns]
        )

    def _validate_schema(self, df: pd.DataFrame, expected_schema: pa.Schema):
        gen_schema = pa.Schema.from_pandas(df)
        for field in expected_schema:
            if field.name not in gen_schema.names:
                raise ValueError(f"Missing column: [{field.name}]")
            if gen_schema.field(field.name).type.to_pandas_dtype() != field.type.to_pandas_dtype():
                raise ValueError(
                    f"Type mismatch for [{field.name}]: "
                    f"got [{gen_schema.field(field.name).type.to_pandas_dtype()}], "
                    f"expected [{field.type.to_pandas_dtype()}]"
                )
