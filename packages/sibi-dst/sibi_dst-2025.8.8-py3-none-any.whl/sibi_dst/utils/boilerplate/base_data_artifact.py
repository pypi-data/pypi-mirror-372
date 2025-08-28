from __future__ import annotations

import asyncio
from typing import Any, Dict, Mapping, Optional, Type, Union
from datetime import date, datetime

import pandas as pd
import dask.dataframe as dd
from sibi_dst.df_helper import ParquetArtifact


DateLike = Union[str, date, datetime, None]


def _validate_and_format_date(name: str, value: DateLike) -> Optional[str]:
    """
    Normalize date-like input into a canonical string '%Y-%m-%d'.

    - None -> None
    - str/date/datetime -> parse with pandas.to_datetime, take .date(), return '%Y-%m-%d'
    - else -> TypeError
    """
    if value is None:
        return None
    if isinstance(value, (str, date, datetime)):
        try:
            return pd.to_datetime(value).date().strftime("%Y-%m-%d")
        except Exception as e:
            raise ValueError(f"{name} must be a valid date, got {value!r}") from e
    raise TypeError(f"{name} must be str, date, datetime, or None; got {type(value)}")


class BaseDataArtifact(ParquetArtifact):
    """
    Base class for Parquet artifacts with optional date window.

    Dates are always stored as strings in '%Y-%m-%d' format.
    """

    config: Mapping[str, Any] = {}

    parquet_start_date: Optional[str]
    parquet_end_date: Optional[str]
    data_wrapper_class: Optional[Type[Any]]
    class_params: Dict[str, Any]
    df: Union[pd.DataFrame | dd.DataFrame] = None

    def __init__(
        self,
        **kwargs: Any,
    ) -> None:
        merged = {**self.config, **kwargs}
        super().__init__(**merged)

        # Normalize and store as canonical strings
        self.parquet_start_date = _validate_and_format_date("parquet_start_date", merged.get("parquet_start_date", None))
        self.parquet_end_date   = _validate_and_format_date("parquet_end_date", merged.get("parquet_end_date", None))

        self.data_wrapper_class = merged.get("data_wrapper_class", None)
        self.class_params = merged.get("class_params", None) or {
            "debug": self.debug,
            "logger": self.logger,
            "fs": self.fs,
            "verbose": getattr(self, "verbose", False),
        }

        # Ordering check
        if self.parquet_start_date and self.parquet_end_date:
            if self.parquet_start_date > self.parquet_end_date:
                raise ValueError(
                    f"parquet_start_date {self.parquet_start_date} "
                    f"cannot be after parquet_end_date {self.parquet_end_date}"
                )

    # -------- Optional hooks --------

    def before_load(self, **kwargs: Any) -> None: return None
    def after_load(self, **kwargs: Any) -> None: return None
    async def abefore_load(self, **kwargs: Any) -> None: return None
    async def aafter_load(self, **kwargs: Any) -> None: return None

    # -------- Public API --------

    def load(self, **kwargs: Any):
        self.before_load(**kwargs)
        self.df = super().load(**kwargs)
        self.after_load(**kwargs)
        return self.df

    async def aload(self, **kwargs: Any):
        await self.abefore_load(**kwargs)
        df = await asyncio.to_thread(super().load, **kwargs)
        self.df = df
        await self.aafter_load(**kwargs)
        return self.df

    def has_date_window(self) -> bool:
        return bool(self.parquet_start_date or self.parquet_end_date)

    def date_window(self) -> tuple[Optional[str], Optional[str]]:
        return self.parquet_start_date, self.parquet_end_date

    def to_params(self) -> Dict[str, Any]:
        return {
            "parquet_start_date": self.parquet_start_date,
            "parquet_end_date": self.parquet_end_date,
            "data_wrapper_class": self.data_wrapper_class,
            "class_params": dict(self.class_params),
        }

