from typing import Literal

import daft
from daft import DataFrame

from .....__types import DictData
from .....models import MetricSource, Shape
from ....__abc import BaseSource


class LocalJsonFile(BaseSource):
    type: Literal["local"]
    file_format: Literal["json"]
    path: str

    def load(
        self,
        engine: DictData,
        metric: MetricSource,
        **kwargs,
    ) -> tuple[DataFrame, Shape]:
        df: DataFrame = daft.read_json(
            path=self.path,
            file_path_column=None,
        )
        return df, Shape()

    def inlet(self) -> tuple[str, str]:
        return "local", self.path


class LocalCsvFile(BaseSource):
    type: Literal["local"]
    file_format: Literal["csv"]
    path: str
    delimiter: str | None = None
    header: bool = True

    def load(
        self,
        engine: DictData,
        metric: MetricSource,
        **kwargs,
    ) -> tuple[DataFrame, Shape]:
        df: DataFrame = daft.read_csv(
            path=self.path,
            file_path_column=None,
            delimiter=self.delimiter,
            has_headers=self.header,
        )
        return df, Shape()

    def inlet(self) -> tuple[str, str]:
        return "local", self.path
