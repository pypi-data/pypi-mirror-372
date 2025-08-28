from __future__ import annotations

from typing import Any, Tuple, Dict

import dask.dataframe as dd
import pandas as pd

from sibi_dst.utils import ManagedResource
from sibi_dst.df_helper.core import ParamsConfig, QueryConfig
from ._db_connection import SqlAlchemyConnectionConfig
from ._io_dask import SQLAlchemyDask


class SqlAlchemyLoadFromDb(ManagedResource):
    """
    Orchestrates loading data from a database using SQLAlchemy into a Dask DataFrame.
    """
    logger_extra: Dict[str, Any] = {"sibi_dst_component": __name__}

    def __init__(
        self,
        plugin_sqlalchemy: SqlAlchemyConnectionConfig,
        plugin_query: QueryConfig = None,
        plugin_params: ParamsConfig = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.db_connection = plugin_sqlalchemy
        self.model = self.db_connection.model
        self.engine = self.db_connection.engine
        self.query_config = plugin_query
        self.params_config = plugin_params
        self.chunk_size = kwargs.get("chunk_size", self.params_config.df_params.get("chunk_size", 1000) if self.params_config else 1000)
        self.total_records = -1

    def build_and_load(self) -> Tuple[int, dd.DataFrame]:
        try:
            with SQLAlchemyDask(
                model=self.model,
                filters=self.params_config.filters if self.params_config else {},
                engine=self.engine,
                chunk_size=self.chunk_size,
                logger=self.logger,
                verbose=self.verbose,
                debug=self.debug,
            ) as loader:
                self.logger.debug(f"SQLAlchemyDask loader initialized for model: {self.model.__name__}", extra=self.logger_extra)
                self.total_records, dask_df = loader.read_frame()
                return self.total_records, dask_df
        except Exception as e:
            self.total_records = -1
            self.logger.error(f"{self.model.__name__} Failed to build and load data: {e}", exc_info=True, extra=self.logger_extra)
            # empty df with correct columns
            columns = [c.name for c in self.model.__table__.columns]
            return self.total_records, dd.from_pandas(pd.DataFrame(columns=columns), npartitions=1)

