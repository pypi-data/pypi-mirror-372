import logging
from typing import Literal

from daft import DataFrame
from pydantic import Field

from ... import Result
from ...__types import DictData
from ...models import Context, MetricEngine, MetricTransform
from ..__abc import BaseEngine
from .sink import Sink
from .source import Source

logger = logging.getLogger("jett")


class Daft(BaseEngine):
    """Daft Engine Model."""

    type: Literal["daft"]
    sink: list[Sink] = Field(description="A list of Sink model.")
    source: Source

    def execute(
        self,
        context: Context,
        engine: DictData,
        metric: MetricEngine,
    ) -> DataFrame:
        logger.info("Start execute with Arrow engine.")
        df: DataFrame = self.source.handle_load(context, engine=engine)
        df: DataFrame = self.handle_apply(df, context, engine=engine)
        for sk in self.sink:
            sk.handle_save(df, context, engine=engine)
        return df

    def set_engine_context(self, context: Context, **kwargs) -> DictData:
        return {"engine": self}

    def set_result(self, df: DataFrame, context: Context) -> Result:
        return Result()

    def apply(
        self,
        df: DataFrame,
        context: Context,
        engine: DictData,
        metric: MetricTransform,
        **kwargs,
    ) -> DataFrame:
        return df
