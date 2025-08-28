import warnings

from pandas.api.types import is_period_dtype, is_bool_dtype, is_string_dtype
import pandas as pd
import dask.dataframe as dd
import pyarrow as pa

from . import ManagedResource

warnings.filterwarnings("ignore", message="Passing 'overwrite=True' to to_parquet is deprecated")


class ParquetSaver(ManagedResource):
    """
    Saves Dask DataFrames to Parquet, with a workaround for S3-compatible
    storage providers that misbehave on batch delete operations.

    Assumes `df_result` is a Dask DataFrame.
    """
    logger_extra = {"sibi_dst_component": __name__}

    def __init__(
        self,
        df_result: dd.DataFrame,
        parquet_storage_path: str,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.df_result = df_result
        self.parquet_storage_path = parquet_storage_path.rstrip("/")
        if not self.fs:
            raise ValueError("File system (fs) must be provided to ParquetSaver.")

        self.protocol = "file"
        if "://" in self.parquet_storage_path:
            self.protocol = self.parquet_storage_path.split(":", 1)[0]

        self.persist = kwargs.get("persist",True)
        self.write_index = kwargs.get("write_index", False)
        self.write_metadata_file = kwargs.get("write_metadata_file", True)

    def save_to_parquet(self, output_directory_name: str = "default_output", overwrite: bool = True):
        """
        Saves the Dask DataFrame to a Parquet dataset.

        If overwrite is True, it manually clears the destination directory before
        writing to avoid issues with certain S3-compatible storage providers.
        """
        full_path = f"{self.parquet_storage_path}/{output_directory_name}"

        if overwrite and self.fs and self.fs.exists(full_path):
            self.logger.info(f"Overwrite is True, clearing destination path: {full_path}", extra=self.logger_extra)
            self._clear_directory_safely(full_path)

        # Ensure the base directory exists after clearing
        self.fs.mkdirs(full_path, exist_ok=True)

        schema = self._define_schema()
        self.logger.info(f"Saving DataFrame to Parquet dataset at: {full_path}", extra=self.logger_extra)
        # 1) Normalize to declared schema (fixes bool→string, Period→string, etc.)
        ddf = self._coerce_ddf_to_schema(self.df_result, schema)

        # 2) Persist after coercion so all partitions share the coerced dtypes
        ddf = ddf.persist() if self.persist else ddf

        try:
            ddf.to_parquet(
                path=full_path,
                engine="pyarrow",
                schema=schema,
                overwrite=False,         # we've handled deletion already
                filesystem=self.fs,
                write_index=self.write_index,  # whether to write the index
                write_metadata_file=self.write_metadata_file,  # write _metadata for easier reading later
            )
            self.logger.info(f"Successfully saved Parquet dataset to: {full_path}", extra=self.logger_extra)
        except Exception as e:
            self.logger.error(f"Failed to save Parquet dataset to {full_path}: {e}", extra=self.logger_extra)
            raise

    def _clear_directory_safely(self, directory: str):
        """
        Clears the contents of a directory robustly.
        - For S3, deletes files one-by-one to bypass brittle multi-delete.
        - For other filesystems, uses the standard recursive remove.
        """
        if self.protocol == "s3":
            self.logger.warning(
                "Using single-file S3 deletion for compatibility. "
                "This may be slow for directories with many files."
            )
            # Glob all contents (files and subdirs) and delete them individually.
            all_paths = self.fs.glob(f"{directory}/**")
            # delete contents (deepest first)
            for path in sorted([p for p in all_paths if p != directory], key=len, reverse=True):
                self.logger.debug(f"Deleting: {path}")
                try:
                    # prefer rm_file if available (minio, s3fs expose it)
                    if hasattr(self.fs, "rm_file"):
                        self.fs.rm_file(path)
                    else:
                        self.fs.rm(path, recursive=False)
                except Exception as e:
                    self.logger.warning(f"Failed to delete '{path}': {e}", extra=self.logger_extra)
            # remove the (now empty) directory if present
            try:
                self.fs.rm(directory, recursive=False)
            except Exception:
                pass
        else:
            # Standard, fast deletion for other filesystems (local, etc.)
            self.fs.rm(directory, recursive=True)

    def _define_schema(self) -> pa.Schema:
        """
        Defines a PyArrow schema dynamically based on DataFrame's column types.
        Works for Dask by using known dtypes on the collection.
        """
        pandas_dtype_to_pa = {
            "object": pa.string(), "string": pa.string(),
            "int64": pa.int64(), "Int64": pa.int64(),
            "int32": pa.int32(), "Int32": pa.int32(),
            "float64": pa.float64(), "float32": pa.float32(),
            "bool": pa.bool_(), "boolean": pa.bool_(),
            "datetime64[ns]": pa.timestamp("ns"),
            "datetime64[ns, UTC]": pa.timestamp("ns", tz="UTC"),
            "category": pa.string(),
        }
        fields = [
            pa.field(c, pandas_dtype_to_pa.get(str(d), pa.string()))
            for c, d in self.df_result.dtypes.items()
        ]
        return pa.schema(fields)


    def _coerce_ddf_to_schema(self, ddf: dd.DataFrame, schema: pa.Schema) -> dd.DataFrame:
        """
        Coerce Dask DataFrame columns to match the provided PyArrow schema.
        - Ensures cross-partition consistency.
        - Converts troublesome dtypes (Period, mixed object/bool) to the declared type.
        """
        # Build a map: name -> target kind
        target = {field.name: field.type for field in schema}

        def _coerce_partition(pdf: pd.DataFrame) -> pd.DataFrame:
            for col, typ in target.items():
                if col not in pdf.columns:
                    continue

                pa_type = typ

                # String targets
                if pa.types.is_string(pa_type) or pa.types.is_large_string(pa_type):
                    # Convert Period or any dtype to string with NA-preservation
                    s = pdf[col]
                    if is_period_dtype(s):
                        pdf[col] = s.astype(str)
                    elif not is_string_dtype(s):
                        # astype("string") keeps NA; str(s) can produce "NaT" strings
                        try:
                            pdf[col] = s.astype("string")
                        except Exception:
                            pdf[col] = s.astype(str).astype("string")
                    continue

                # Boolean targets
                if pa.types.is_boolean(pa_type):
                    s = pdf[col]
                    # Allow object/bool mixtures; coerce via pandas nullable boolean then to bool
                    try:
                        pdf[col] = s.astype("boolean").astype(bool)
                    except Exception:
                        pdf[col] = s.astype(bool)
                    continue

                # Integer targets
                if pa.types.is_integer(pa_type):
                    s = pdf[col]
                    # Go through pandas nullable Int64 to preserve NA, then to int64 if clean
                    s2 = pd.to_numeric(s, errors="coerce").astype("Int64")
                    # If there are no nulls, downcast to numpy int64 for speed
                    if not s2.isna().any():
                        s2 = s2.astype("int64")
                    pdf[col] = s2
                    continue

                # Floating targets
                if pa.types.is_floating(pa_type):
                    pdf[col] = pd.to_numeric(pdf[col], errors="coerce").astype("float64")
                    continue

                # Timestamp[ns] (optionally with tz)
                if pa.types.is_timestamp(pa_type):
                    # If tz in Arrow type, you may want to localize; here we just ensure ns
                    pdf[col] = pd.to_datetime(pdf[col], errors="coerce")
                    continue

                # Fallback: leave as-is
            return pdf

        # Provide a meta with target dtypes to avoid meta mismatch warnings
        meta = {}
        for name, typ in target.items():
            # Rough meta mapping; Arrow large_string vs string both → 'string'
            if pa.types.is_string(typ) or pa.types.is_large_string(typ):
                meta[name] = pd.Series([], dtype="string")
            elif pa.types.is_boolean(typ):
                meta[name] = pd.Series([], dtype="bool")
            elif pa.types.is_integer(typ):
                meta[name] = pd.Series([], dtype="Int64")  # nullable int
            elif pa.types.is_floating(typ):
                meta[name] = pd.Series([], dtype="float64")
            elif pa.types.is_timestamp(typ):
                meta[name] = pd.Series([], dtype="datetime64[ns]")
            else:
                meta[name] = pd.Series([], dtype="object")

        # Start from current meta and update known columns
        new_meta = ddf._meta.copy()
        for k, v in meta.items():
            if k in new_meta.columns:
                new_meta[k] = v

        return ddf.map_partitions(_coerce_partition, meta=new_meta)