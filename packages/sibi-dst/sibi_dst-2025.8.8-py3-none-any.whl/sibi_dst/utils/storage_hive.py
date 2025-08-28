from __future__ import annotations

import asyncio

import pandas as pd
import dask.dataframe as dd
from typing import Iterable, Optional, List, Tuple, Union
import fsspec

DNFFilter = List[List[Tuple[str, str, Union[str, int]]]]


class HiveDatePartitionedStore:
    """
    Dask-only Parquet store with Hive-style yyyy=…/mm=…/dd=… partitions.

    - `write(...)` safely "overwrites" S3 prefixes via per-object deletes (no bulk DeleteObjects).
    - `read_range(...)` builds DNF filters and auto-matches partition types (string vs int).
    """

    def __init__(
        self,
        path: str,
        *,
        filesystem=None,                # fsspec filesystem or None to infer from path
        date_col: str = "tracking_dt",
        compression: str = "zstd",
        partition_values_as_strings: bool = True,  # keep mm=07, dd=01 folder names
        logger=None,
    ) -> None:
        self.path = path
        self.fs = filesystem or fsspec.open(path).fs
        self.date_col = date_col
        self.compression = compression
        self.partition_values_as_strings = partition_values_as_strings
        self.log = logger

    # ----------------- public API -----------------

    def write(
        self,
        df: dd.DataFrame,
        *,
        repartition: Optional[int] = None,
        overwrite: bool = False,
    ) -> None:
        """Write Dask DataFrame to Hive-style yyyy/mm/dd partitions."""
        self._require_col(df, self.date_col)
        ser = dd.to_datetime(df[self.date_col], errors="coerce")

        if self.partition_values_as_strings:
            parts = {
                "yyyy": ser.dt.strftime("%Y"),
                "mm":   ser.dt.strftime("%m"),
                "dd":   ser.dt.strftime("%d"),
            }
        else:
            parts = {
                "yyyy": ser.dt.year.astype("int32"),
                "mm":   ser.dt.month.astype("int8"),
                "dd":   ser.dt.day.astype("int8"),
            }

        df = df.assign(**{self.date_col: ser}, **parts)

        if repartition:
            df = df.repartition(npartitions=repartition)

        if overwrite:
            self._safe_rm_prefix(self.path)

        if self.log:
            self.log.info(f"Writing parquet to {self.path} (hive yyyy/mm/dd)…")

        df.to_parquet(
            self.path,
            engine="pyarrow",
            write_index=False,
            filesystem=self.fs,
            partition_on=["yyyy", "mm", "dd"],
            compression=self.compression,
            overwrite=False,  # we pre-cleaned if overwrite=True
        )

    def read_range(
        self,
        start: Union[str, pd.Timestamp],
        end: Union[str, pd.Timestamp],
        *,
        columns: Optional[Iterable[str]] = None,
    ) -> dd.DataFrame:
        """
        Read a date window with partition pruning. Tries string filters first,
        falls back to integer filters if Arrow infers partition types as ints.
        """
        str_filters = self._dnf_filters_for_range_str(start, end)
        try:
            return dd.read_parquet(
                self.path,
                engine="pyarrow",
                filesystem=self.fs,
                columns=list(columns) if columns else None,
                filters=str_filters,
            )
        except Exception:
            int_filters = self._dnf_filters_for_range_int(start, end)
            return dd.read_parquet(
                self.path,
                engine="pyarrow",
                filesystem=self.fs,
                columns=list(columns) if columns else None,
                filters=int_filters,
            )

    # Convenience: full month / single day
    def read_month(self, year: int, month: int, *, columns=None) -> dd.DataFrame:
        start = pd.Timestamp(year=year, month=month, day=1)
        end = (start + pd.offsets.MonthEnd(0))
        return self.read_range(start, end, columns=columns)

    def read_day(self, year: int, month: int, day: int, *, columns=None) -> dd.DataFrame:
        ts = pd.Timestamp(year=year, month=month, day=day)
        return self.read_range(ts, ts, columns=columns)

    # ----------------- internals -----------------

    @staticmethod
    def _pad2(n: int) -> str:
        return f"{n:02d}"

    def _safe_rm_prefix(self, path: str) -> None:
        """Per-object delete to avoid S3 bulk DeleteObjects (and Content-MD5 issues)."""
        if not self.fs.exists(path):
            return
        if self.log:
            self.log.info(f"Cleaning prefix (safe delete): {path}")
        for k in self.fs.find(path):
            try:
                (self.fs.rm_file(k) if hasattr(self.fs, "rm_file") else self.fs.rm(k, recursive=False))
            except Exception as e:
                if self.log:
                    self.log.warning(f"Could not delete {k}: {e}")

    @staticmethod
    def _require_col(df: dd.DataFrame, col: str) -> None:
        if col not in df.columns:
            raise KeyError(f"'{col}' not in DataFrame")

    # ---- DNF builders (string vs int) ----
    def _dnf_filters_for_range_str(self, start, end) -> DNFFilter:
        s, e = pd.Timestamp(start), pd.Timestamp(end)
        if s > e:
            raise ValueError("start > end")
        sY, sM, sD = s.year, s.month, s.day
        eY, eM, eD = e.year, e.month, e.day
        p2 = self._pad2
        if sY == eY and sM == eM:
            return [[("yyyy","==",str(sY)),("mm","==",p2(sM)),("dd",">=",p2(sD)),("dd","<=",p2(eD))]]
        clauses: DNFFilter = [
            [("yyyy","==",str(sY)),("mm","==",p2(sM)),("dd",">=",p2(sD))],
            [("yyyy","==",str(eY)),("mm","==",p2(eM)),("dd","<=",p2(eD))]
        ]
        if sY == eY:
            for m in range(sM+1, eM):
                clauses.append([("yyyy","==",str(sY)),("mm","==",p2(m))])
            return clauses
        for m in range(sM+1, 13):
            clauses.append([("yyyy","==",str(sY)),("mm","==",p2(m))])
        for y in range(sY+1, eY):
            clauses.append([("yyyy","==",str(y))])
        for m in range(1, eM):
            clauses.append([("yyyy","==",str(eY)),("mm","==",p2(m))])
        return clauses

    @staticmethod
    def _dnf_filters_for_range_int(start, end) -> DNFFilter:
        s, e = pd.Timestamp(start), pd.Timestamp(end)
        if s > e:
            raise ValueError("start > end")
        sY, sM, sD = s.year, s.month, s.day
        eY, eM, eD = e.year, e.month, e.day
        if sY == eY and sM == eM:
            return [[("yyyy","==",sY),("mm","==",sM),("dd",">=",sD),("dd","<=",eD)]]
        clauses: DNFFilter = [
            [("yyyy","==",sY),("mm","==",sM),("dd",">=",sD)],
            [("yyyy","==",eY),("mm","==",eM),("dd","<=",eD)],
        ]
        if sY == eY:
            for m in range(sM+1, eM):
                clauses.append([("yyyy","==",sY),("mm","==",m)])
            return clauses
        for m in range(sM+1, 13):
            clauses.append([("yyyy","==",sY),("mm","==",m)])
        for y in range(sY+1, eY):
            clauses.append([("yyyy","==",y)])
        for m in range(1, eM):
            clauses.append([("yyyy","==",eY),("mm","==",m)])
        return clauses

    async def write_async(
            self,
            df: dd.DataFrame,
            *,
            repartition: int | None = None,
            overwrite: bool = False,
            timeout: float | None = None,
    ) -> None:
        async def _run():
            return await asyncio.to_thread(self.write, df, repartition=repartition, overwrite=overwrite)

        return await (asyncio.wait_for(_run(), timeout) if timeout else _run())

    async def read_range_async(
            self,
            start, end, *, columns: Iterable[str] | None = None, timeout: float | None = None
    ) -> dd.DataFrame:
        async def _run():
            return await asyncio.to_thread(self.read_range, start, end, columns=columns)

        return await (asyncio.wait_for(_run(), timeout) if timeout else _run())

    async def read_month_async(self, year: int, month: int, *, columns=None, timeout: float | None = None):
        async def _run():
            return await asyncio.to_thread(self.read_month, year, month, columns=columns)

        return await (asyncio.wait_for(_run(), timeout) if timeout else _run())

    async def read_day_async(self, year: int, month: int, day: int, *, columns=None, timeout: float | None = None):
        async def _run():
            return await asyncio.to_thread(self.read_day, year, month, day, columns=columns)

        return await (asyncio.wait_for(_run(), timeout) if timeout else _run())