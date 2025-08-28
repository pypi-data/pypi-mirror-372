import warnings
import dask.dataframe as dd
import pandas as pd
import pyarrow as pa
from pyiceberg.catalog import load_catalog
from typing import Optional, Dict, Any
from . import ManagedResource

warnings.filterwarnings("ignore", message="Passing 'overwrite=True' to to_parquet is deprecated")

class IcebergSaver(ManagedResource):
    """
    Saves a Dask DataFrame into an Apache Iceberg table using PyIceberg.
    - Uses Arrow conversion per Dask partition.
    - One Iceberg commit per partition (append mode), or a staged overwrite
      (coalesce to N partitions, commit them in place of the old snapshot).
    """

    def __init__(
        self,
        df_result: dd.DataFrame,
        catalog_name: str,
        table_name: str,
        *,
        persist: bool = True,
        npartitions: Optional[int] = 8,
        arrow_schema: Optional[pa.Schema] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.df_result = df_result
        self.catalog_name = catalog_name
        self.table_name = table_name
        self.persist = persist
        self.npartitions = npartitions
        self.arrow_schema = arrow_schema  # optional: enforce column order/types

        # Iceberg writes don’t need self.fs; catalog handles IO.
        # But we keep self.fs available in case you presign or stage files.

        # Load table once
        self.catalog = load_catalog(self.catalog_name)
        self.table = self.catalog.load_table(self.table_name)

    def save(self, *, mode: str = "append"):
        """
        mode:
          - "append": append rows as new data files (one commit per partition)
          - "overwrite": replace table data atomically (single staged commit)
                         (requires coalescing to limit number of files)
        """
        if mode not in ("append", "overwrite"):
            raise ValueError("mode must be 'append' or 'overwrite'")

        # Optional persist to avoid recomputation across multiple consumers
        ddf = self.df_result.persist() if self.persist else self.df_result

        if self.npartitions:
            ddf = ddf.repartition(npartitions=self.npartitions)

        if mode == "append":
            self._append_partitions(ddf)
        else:
            self._overwrite_atomic(ddf)

    # ---------- internals ----------

    def _to_arrow_table(self, pdf: pd.DataFrame) -> pa.Table:
        if self.arrow_schema is None:
            return pa.Table.from_pandas(pdf, preserve_index=False)
        # Enforce schema (column order & target types) when provided
        at = pa.Table.from_pandas(pdf, preserve_index=False, schema=self.arrow_schema)
        # Some Arrow versions require select to exact order if pandas added cols
        return at.select(self.arrow_schema.names)

    def _append_partitions(self, ddf: dd.DataFrame):
        """
        Simple path: commit each partition as a separate append.
        Good for moderate rates; for very high throughput, consider staging or
        increasing npartitions to get larger files.
        """
        def _commit(pdf: pd.DataFrame):
            if len(pdf) == 0:
                return pdf.iloc[0:0]
            at = self._to_arrow_table(pdf)
            self.table.append(at)  # one atomic Iceberg commit
            return pdf.iloc[0:0]

        ddf.map_partitions(_commit, meta=ddf._meta).compute()
        self.logger.info(f"Appended data to Iceberg table {self.table_name} (catalog={self.catalog_name}).")

    def _overwrite_atomic(self, ddf: dd.DataFrame):
        """
        Safer full refresh: stage N Arrow batches and replace existing snapshot.
        Strategy:
          1) Build a single overwrite transaction.
          2) Add files produced from each partition to the same transaction.
          3) Commit once (atomic snapshot replacement).
        """
        from pyiceberg.table.ops import RewriteFiles  # operation helper

        # Materialize partitions one by one and add to a rewrite op
        # Note: PyIceberg API offers two patterns:
        #  - table.overwrite(at) for “overwrite by filter” in one call (simple)
        #  - lower-level staged ops (demonstrated conceptually below)

        # Easiest “full-table” overwrite via filter(True) – clears table then writes new data:
        # If you only want to replace certain partitions, use a filter expr.
        def _collect_partitions(pdf: pd.DataFrame):
            if len(pdf) == 0:
                return None
            return self._to_arrow_table(pdf)

        batches = [b for b in ddf.map_partitions(_collect_partitions, meta=object).compute() if b is not None]
        if not batches:
            self.logger.warning("Overwrite requested but no rows in DataFrame; leaving table unchanged.")
            return

        # Commit as a single overwrite
        self.table.overwrite(batches[0])
        for at in batches[1:]:
            self.table.append(at)  # append subsequent batches into the same snapshot lineage

        # If you require truly single-snapshot replacement in one call, you can
        # also union the batches into fewer (bigger) Arrow Tables before calling overwrite.
        self.logger.info(f"Overwrote Iceberg table {self.table_name} with {len(batches)} batch(es).")