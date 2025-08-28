import datetime as dt
from concurrent.futures import ThreadPoolExecutor, wait
from typing import List, Optional, Dict, Union, Tuple, Set, Iterator, ClassVar

import pandas as pd

from sibi_dst.utils import ManagedResource
from . import FileAgeChecker


class UpdatePlanner(ManagedResource):
    """
    Scans date-partitioned storage and builds an 'update plan' for dates that need processing.
    Backward compatible: public API and legacy attributes preserved; enhancements are opt-in via kwargs.

    Enhancements:
      - Batch listings via fsspec.find(..., detail=True) to avoid N×exists() roundtrips.
      - Age computed from the NEWEST data file (ignoring control files).
      - Optional completeness check: partitions with files but no _SUCCESS => 'incomplete'.
      - Real timeouts using concurrent.futures.wait(...).
      - Future dates marked as 'future' (not actionable).
    """

    # -------- Defaults (extended, but original keys retained) --------
    DEFAULT_PRIORITY_MAP: ClassVar[Dict[str, int]] = {
        "file_is_recent": 0,
        "missing_ignored": 0,
        "overwrite_forced": 1,
        "incomplete": 1,            # new: prioritize just under overwrite
        "create_missing": 2,
        "missing_in_history": 3,
        "stale_in_history": 4,
        "future": 99,               # new: not actionable
    }

    DEFAULT_MAX_AGE_MINUTES: int = 1440
    DEFAULT_HISTORY_DAYS_THRESHOLD: int = 30

    # Data/Control file heuristics (can be overridden)
    DATA_FILE_PATTERNS: ClassVar[Tuple[str, ...]] = (".parquet", ".orc", ".csv", ".json")
    CONTROL_BASENAMES: ClassVar[Set[str]] = {"_SUCCESS", "_metadata", "_common_metadata"}

    logger_extra = {"sibi_dst_component": __name__}

    def __init__(
        self,
        parquet_storage_path: str,
        parquet_filename: str,
        description: str = "Update Planner",
        reference_date: Union[str, dt.date, None] = None,
        history_days_threshold: int = DEFAULT_HISTORY_DAYS_THRESHOLD,
        max_age_minutes: int = DEFAULT_MAX_AGE_MINUTES,
        overwrite: bool = False,
        ignore_missing: bool = False,
        custom_priority_map: Optional[Dict[str, int]] = None,
        reverse_order: bool = False,
        show_progress: bool = False,
        skipped: Optional[List[Union[str, dt.date]]] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        # ---- Existing public-ish attributes (unchanged) ----
        self.description = description
        self.data_path = self._ensure_trailing_slash(parquet_storage_path)
        self.filename = parquet_filename
        self.reverse_order = reverse_order
        self.show_progress = show_progress
        self.overwrite = overwrite
        self.ignore_missing = ignore_missing
        self.history_days_threshold = history_days_threshold
        self.max_age_minutes = max_age_minutes
        # copy to avoid shared mutation
        self.priority_map = dict(custom_priority_map) if custom_priority_map else dict(self.DEFAULT_PRIORITY_MAP)

        # Execution knobs from kwargs (kept)
        self.max_threads: int = int(kwargs.get("max_threads", 3))
        self.timeout: float = float(kwargs.get("timeout", 30.0))  # legacy overall timeout

        # Date window (kept)
        self.start_date = kwargs.get("parquet_start_date")
        self.end_date = kwargs.get("parquet_end_date")

        # Reference date (kept; tolerant)
        self.reference_date = pd.to_datetime(reference_date).date() if reference_date is not None else dt.date.today()

        # Helpers & state (kept)
        self.age_checker = FileAgeChecker(debug=self.debug, logger=self.logger)
        self.plan: pd.DataFrame = pd.DataFrame()
        self.df_req: pd.DataFrame = pd.DataFrame()
        self._printed_this_run: bool = False

        # ---- New feature flags / knobs (all default to safe choices) ----
        # Completeness check via _SUCCESS
        self.check_completeness: bool = bool(kwargs.get("check_completeness", True))
        self.require_success_marker: bool = bool(kwargs.get("require_success_marker", True))
        # Listing granularity: 'month' (default) or 'day'
        self.list_granularity: str = str(kwargs.get("list_granularity", "month"))
        # Data file suffixes to consider for age (default common formats)
        self.data_file_suffixes: Tuple[str, ...] = tuple(kwargs.get("data_file_suffixes", self.DATA_FILE_PATTERNS))
        # Timeouts
        self.list_timeout: float = float(kwargs.get("list_timeout", self.timeout))       # per-future
        self.total_timeout: float = float(kwargs.get("total_timeout", self.timeout))     # across all listings
        # Dependency-injected clock (UTC) for tests
        self._utcnow = kwargs.get("utcnow_func", None) or (lambda: dt.datetime.utcnow())

        # ------------ Backward-compatible skip handling ------------
        # Keep legacy attribute and derive new internal canonical sets.
        self.skipped = list(skipped or kwargs.get("skipped", []) or [])
        self.skipped_paths = {p.rstrip("/") + "/" for p in self.skipped if isinstance(p, str)}
        self.skipped_dates = {p for p in self.skipped if isinstance(p, dt.date)}

        # Validate fs presence (you rely on it)
        if not getattr(self, "fs", None):
            raise ValueError("UpdatePlanner requires a valid fsspec filesystem (fs).")

    # --------------------- Back-compat property bridge ---------------------
    @property
    def skipped(self) -> List[Union[str, dt.date]]:  # type: ignore[override]
        """
        Backward-compatible view of skip configuration.
        Returns a merged list of path-strings and dates.
        """
        paths = sorted(self.skipped_paths)
        dates = sorted(self.skipped_dates)
        return [*paths, *dates]

    @skipped.setter
    def skipped(self, value: List[Union[str, dt.date]]) -> None:  # type: ignore[override]
        """
        Accepts legacy assignments like:
            planner.skipped = ["s3://.../2025/01/03/", date(2025,1,4)]
        and keeps new internals in sync.
        """
        value = list(value or [])
        self.skipped_paths = {p.rstrip("/") + "/" for p in value if isinstance(p, str)}
        self.skipped_dates = {p for p in value if isinstance(p, dt.date)}

    # --------------------- public helpers (kept) ---------------------
    def has_plan(self) -> bool:
        return isinstance(self.plan, pd.DataFrame) and not self.plan.empty

    def required_count(self) -> int:
        return 0 if not isinstance(self.df_req, pd.DataFrame) else len(self.df_req)

    # --------------------- core API (kept) ---------------------
    def generate_plan(
        self,
        start: Union[str, dt.date, None] = None,
        end: Union[str, dt.date, None] = None,
        freq: str = "D",
    ) -> pd.DataFrame:
        """Build a plan for [start, end]. Returns rows that require update (df_req)."""
        start = start or self.start_date
        end = end or self.end_date
        if start is None or end is None:
            raise ValueError("start and end must be provided (or set via parquet_* kwargs).")

        sd = pd.to_datetime(start).date()
        ed = pd.to_datetime(end).date()
        if sd > ed:
            raise ValueError(f"Start date ({sd}) must be on or before end date ({ed}).")

        self.logger.info(
            f"Generating update plan for {self.description} from {sd} to {ed}",
            extra=self._log_extra(),
        )
        self._generate_plan(sd, ed, freq=freq)
        self.logger.info(
            f"Plan built for {self.description}: {len(self.plan)} dates evaluated, "
            f"{len(self.df_req)} require update",
            extra=self._log_extra(),
        )
        return self.df_req

    def show_update_plan(self) -> None:
        """Pretty-print the current plan once per run, now respecting terminal width fully."""
        if not self.has_plan():
            self.logger.info("No update plan to show.", extra=self._log_extra())
            return
        if self._printed_this_run:
            return

        try:
            from rich.console import Console
            from rich.table import Table

            console = Console()  # auto-detect terminal size
            terminal_width = console.size.width

            table = Table(
                title=f"Update Plan for {self.data_path}",
                show_header=True,
                header_style="bold magenta",
                expand=True,  # fill available width
                pad_edge=False,
            )
            max_w = max(terminal_width - 50, 640)
            for col in self.plan.columns:
                if col in {"date", "update_category", "update_priority", "update_required", "file_exists"}:
                    table.add_column(col, justify="left", no_wrap=True, overflow="fold", max_width=max_w)
                elif col == "description":
                    # Let description wrap, but set a max width to avoid huge columns
                    table.add_column(col, justify="left", overflow="fold", max_width=max_w)
                else:
                    table.add_column(col, justify="left", overflow="fold")

            for _, row in self.plan.iterrows():
                table.add_row(*(str(row[c]) for c in self.plan.columns))

            # Capture with the same console so width stays consistent
            with console.capture() as cap:
                console.print(table)
            self.logger.info(f"Full Update Plan:\n{cap.get().strip()}", extra=self._log_extra())

        except Exception:
            preview = self.plan.head(200).to_string(index=False)
            self.logger.info(f"Update Plan (first 200 rows):\n{preview}", extra=self._log_extra())

        self._printed_this_run = True

    def get_tasks_by_priority(self) -> Iterator[Tuple[int, List[dt.date]]]:
        """Yield (priority, [dates...]) batches, smallest priority first."""
        if not self.has_plan():
            return
        req = self.plan[self.plan["update_required"]]
        if req.empty:
            return
        for priority in sorted(req["update_priority"].unique()):
            dates_df = req[req["update_priority"] == priority]
            dates_df = dates_df.sort_values(by="date", ascending=not self.reverse_order)
            dates = dates_df["date"].tolist()
            if dates:
                yield int(priority), dates

    # --------------------- internals ---------------------
    @staticmethod
    def _ensure_trailing_slash(path: str) -> str:
        return path.rstrip("/") + "/"

    @staticmethod
    def _month_floor(d: dt.date) -> dt.date:
        return d.replace(day=1)

    @staticmethod
    def _iter_month_starts(start: dt.date, end: dt.date) -> Iterator[dt.date]:
        cur = start.replace(day=1)
        while cur <= end:
            yield cur
            y, m = cur.year, cur.month
            cur = dt.date(y + (m == 12), 1 if m == 12 else m + 1, 1)

    def _month_prefix(self, month_start: dt.date) -> str:
        return f"{self.data_path}{month_start.year}/{month_start.month:02d}/"

    def _day_prefix(self, d: dt.date) -> str:
        return f"{self.data_path}{d.year}/{d.month:02d}/{d.day:02d}/"

    def _log_extra(self, **overrides) -> dict:
        base = {
            "sibi_dst_component": __name__,
            "date_of_update": self.reference_date.strftime("%Y-%m-%d"),
            "dataclass": self.description,
            "action_module_name": "update_plan",
        }
        base.update(overrides)
        return base

    def _is_data_file(self, path: str) -> bool:
        base = path.rsplit("/", 1)[-1]
        if not base or base.startswith(".") or base in self.CONTROL_BASENAMES:
            return False
        lower = base.lower()
        return any(lower.endswith(suf) for suf in self.data_file_suffixes)

    def _is_skipped(self, d: dt.date) -> bool:
        """True if the date or its canonical path is in the skip config."""
        just_path = f"{self.data_path}{d.year}/{d.month:02d}/{d.day:02d}/"
        return (d in self.skipped_dates) or (just_path in self.skipped_paths)

    def _list_prefix(self, prefix: str) -> Dict[dt.date, Dict[str, object]]:
        """
        Return {date: {'files': [paths], 'has_success': bool, 'newest_ts': datetime|None}} under prefix.
        Uses fsspec.find(detail=True) for one-shot listing with metadata (mtime).  [oai_citation:0‡fsspec](https://filesystem-spec.readthedocs.io/en/latest/api.html?utm_source=chatgpt.com) [oai_citation:1‡GitHub](https://github.com/fsspec/filesystem_spec/blob/master/fsspec%2Fspec.py?utm_source=chatgpt.com)
        """
        try:
            items = self.fs.find(prefix, withdirs=False, detail=True)  # returns {path: info} when detail=True
        except Exception as e:
            self.logger.warning(f"Listing failed for {prefix}: {e}", extra=self._log_extra())
            return {}

        out: Dict[dt.date, Dict[str, object]] = {}
        for path, info in items.items():
            parts = path.strip("/").split("/")
            if len(parts) < 4:
                continue
            try:
                y, m, dd = int(parts[-4]), int(parts[-3]), int(parts[-2])
                d = dt.date(y, m, dd)
            except Exception:
                continue

            rec = out.setdefault(d, {"files": [], "has_success": False, "newest_ts": None})
            base = path.rsplit("/", 1)[-1]
            if base == "_SUCCESS":
                rec["has_success"] = True

            if self._is_data_file(path):
                rec["files"].append(path)
                mtime = info.get("mtime") or info.get("LastModified") or info.get("last_modified")
                ts = None
                if isinstance(mtime, (int, float)):
                    ts = dt.datetime.utcfromtimestamp(mtime)
                elif isinstance(mtime, str):
                    try:
                        ts = pd.to_datetime(mtime, utc=True).to_pydatetime()
                    except Exception:
                        ts = None
                elif isinstance(mtime, dt.datetime):
                    ts = mtime if mtime.tzinfo else mtime.replace(tzinfo=dt.timezone.utc)
                if ts:
                    cur = rec["newest_ts"]
                    rec["newest_ts"] = ts if (cur is None or ts > cur) else cur
        return out

    def _summarize_partition(
        self, d: dt.date, cache: Dict[dt.date, Dict[str, object]]
    ) -> Tuple[bool, Optional[float], bool]:
        """
        (exists, age_minutes, incomplete)
        - exists: True iff at least one *data* file is present for day `d`
        - age_minutes: minutes since the NEWEST data file (UTC 'now')
        - incomplete: True if files exist but required _SUCCESS is missing
        """
        rec = cache.get(d, {})
        files = rec.get("files", [])
        has_success = bool(rec.get("has_success", False))
        exists = len(files) > 0
        if not exists:
            return False, None, False
        newest_ts = rec.get("newest_ts")
        if newest_ts:
            now_utc = self._utcnow().replace(tzinfo=None)
            ts_naive = newest_ts.replace(tzinfo=None) if newest_ts.tzinfo else newest_ts
            age_min = max(0.0, (now_utc - ts_naive).total_seconds() / 60.0)
        else:
            age_min = None
        incomplete = self.check_completeness and self.require_success_marker and not has_success
        return True, age_min, incomplete

    def _generate_plan(self, start: dt.date, end: dt.date, freq: str = "D") -> None:
        """
        Populate self.plan with all dates and self.df_req with the subset to update.
        - Pre-lists months or days (configurable) with timeouts that actually apply
        - Computes staleness from newest *data* file
        - Flags partitions without _SUCCESS as 'incomplete' (unless disabled)
        - Marks future dates as 'future' (not actionable)
        """
        dates: List[dt.date] = pd.date_range(start=start, end=end, freq=freq).date.tolist()
        history_start = self.reference_date - dt.timedelta(days=self.history_days_threshold)
        rows: List[Dict] = []

        def is_future(d: dt.date) -> bool:
            return d > self.reference_date

        # Choose listing units
        if self.list_granularity == "day":
            units: List[Tuple[str, dt.date]] = [("day", d) for d in dates]
        else:
            months = list(self._iter_month_starts(self._month_floor(start), self._month_floor(end)))
            units = [("month", m) for m in months]

        self.logger.info(
            f"Pre-listing {len(units)} {'days' if self.list_granularity=='day' else 'month prefixes'} for {self.description}",
            extra=self._log_extra(),
        )

        # Parallel listing with real timeout (uses futures.wait)  [oai_citation:2‡Python documentation](https://docs.python.org/3/library/concurrent.futures.html?utm_source=chatgpt.com) [oai_citation:3‡alexwlchan.net](https://alexwlchan.net/2019/adventures-with-concurrent-futures/?utm_source=chatgpt.com)
        caches: Dict[dt.date, Dict[dt.date, Dict[str, object]]] = {}
        max_workers = max(1, int(self.max_threads))
        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            futs = {}
            for kind, val in units:
                prefix = self._day_prefix(val) if kind == "day" else self._month_prefix(val)
                futs[ex.submit(self._list_prefix, prefix)] = (kind, val)
            done, not_done = wait(futs, timeout=self.total_timeout or None)
            for f in done:
                kind, val = futs[f]
                try:
                    cache = f.result(timeout=self.list_timeout or None)
                except Exception as e:
                    self.logger.warning(f"Listing failed for {kind}:{val} — {e}", extra=self._log_extra())
                    cache = {}
                if kind == "month":
                    caches[val] = cache
                else:
                    # day → store into its month bucket for summarization reuse
                    mk = val.replace(day=1)
                    caches.setdefault(mk, {}).update(cache)
            for f in not_done:
                kind, val = futs[f]
                self.logger.error(f"Listing timed out for {kind}:{val}", extra=self._log_extra())
                if kind == "month":
                    caches[val] = {}
                else:
                    caches.setdefault(val.replace(day=1), {})

        # Summarize each date
        for d in dates:
            if is_future(d):
                rows.append({
                    "date": d, "file_exists": False, "file_age_minutes": None,
                    "update_category": "future", "update_priority": self.priority_map.get("future", 99),
                    "update_required": False, "description": self.description,
                })
                continue

            if self._is_skipped(d):
                self.logger.debug(f"Skipping {d}: in skipped set.", extra=self._log_extra())
                rows.append(self._make_row(d, history_start, False, None))
                continue

            month_key = d.replace(day=1)
            cache = caches.get(month_key, {})
            exists, age_min, incomplete = self._summarize_partition(d, cache)

            # Incomplete partitions get their own category (unless overwrite)
            if incomplete and not self.overwrite:
                rows.append({
                    "date": d, "file_exists": True, "file_age_minutes": age_min,
                    "update_category": "incomplete", "update_priority": self.priority_map.get("incomplete", 1),
                    "update_required": True, "description": self.description,
                })
                continue

            # Fall back to your existing policy (overwrite / history / staleness / missing)
            rows.append(self._make_row(d, history_start, exists, age_min))

        df = pd.DataFrame.from_records(rows)
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"]).dt.date
            df["update_priority"] = df["update_priority"].astype(int)

        df = df.sort_values(
            by=["update_priority", "date"],
            ascending=[True, not self.reverse_order],
            kind="mergesort",
        ).reset_index(drop=True)

        self.plan = df
        self.df_req = df[df["update_required"]].copy()
        self._printed_this_run = False

    # --------------------- original policy (kept) ---------------------
    def _make_row(
        self,
        date: dt.date,
        history_start: dt.date,
        file_exists: bool,
        file_age: Optional[float],
    ) -> Dict:
        """
        Build a single plan row based on flags and thresholds.
        (Categories 'future'/'incomplete' are injected earlier.)
        """
        within_history = history_start <= date <= self.reference_date
        update_required = False

        if self.overwrite:
            category = "overwrite_forced"
            update_required = True
        elif within_history:
            if not file_exists:
                category = "missing_in_history"
                update_required = True
            elif file_age is not None and file_age > self.max_age_minutes:
                category = "stale_in_history"
                update_required = True
            else:
                category = "file_is_recent"
        elif not file_exists and not self.ignore_missing:
            category = "create_missing"
            update_required = True
        else:
            category = "missing_ignored" if not file_exists else "file_is_recent"

        return {
            "date": date,
            "file_exists": bool(file_exists),
            "file_age_minutes": file_age,
            "update_category": category,
            "update_priority": self.priority_map.get(category, 99),
            "update_required": bool(update_required),
            "description": self.description,
        }

# import datetime as dt
# from concurrent.futures import ThreadPoolExecutor, as_completed
# from typing import List, Optional, Dict, Union, Tuple, Set, Iterator, ClassVar
#
# import pandas as pd
#
# from sibi_dst.utils import ManagedResource
# from . import FileAgeChecker
#
#
# class UpdatePlanner(ManagedResource):
#     """
#     Scans date-partitioned storage and builds an 'update plan' for dates that need processing.
#     Produces a Pandas DataFrame plan; it does *not* load data frames, so Dask-vs-Pandas
#     concerns do not apply here.
#     """
#
#     DEFAULT_PRIORITY_MAP: ClassVar[Dict[str, int]] = {
#         "file_is_recent": 0,
#         "missing_ignored": 0,
#         "overwrite_forced": 1,
#         "create_missing": 2,
#         "missing_in_history": 3,
#         "stale_in_history": 4,
#     }
#
#     DEFAULT_MAX_AGE_MINUTES: int = 1440
#     DEFAULT_HISTORY_DAYS_THRESHOLD: int = 30
#     logger_extra = {"sibi_dst_component": __name__}
#
#     def __init__(
#         self,
#         parquet_storage_path: str,
#         parquet_filename: str,
#         description: str = "Update Planner",
#         reference_date: Union[str, dt.date, None] = None,
#         history_days_threshold: int = DEFAULT_HISTORY_DAYS_THRESHOLD,
#         max_age_minutes: int = DEFAULT_MAX_AGE_MINUTES,
#         overwrite: bool = False,
#         ignore_missing: bool = False,
#         custom_priority_map: Optional[Dict[str, int]] = None,
#         reverse_order: bool = False,
#         show_progress: bool = False,
#         skipped: Optional[List[str]] = None,
#         **kwargs,
#     ):
#         super().__init__(**kwargs)
#
#         # Public-ish attributes
#         self.description = description
#         self.data_path = self._ensure_trailing_slash(parquet_storage_path)
#         self.filename = parquet_filename
#         self.reverse_order = reverse_order
#         self.show_progress = show_progress
#         self.overwrite = overwrite
#         self.ignore_missing = ignore_missing
#         self.history_days_threshold = history_days_threshold
#         self.max_age_minutes = max_age_minutes
#         self.priority_map = custom_priority_map or self.DEFAULT_PRIORITY_MAP
#         self.skipped = set(skipped or [])
#
#         # Execution knobs from kwargs (fed by upstream config)
#         self.max_threads: int = int(kwargs.get("max_threads", 3))
#         self.timeout: float = float(kwargs.get("timeout", 30.0))
#
#         # Date window
#         self.start_date = kwargs.get("parquet_start_date")
#         self.end_date = kwargs.get("parquet_end_date")
#
#         # Reference "today"
#         if reference_date is None:
#             self.reference_date = dt.date.today()
#         else:
#             self.reference_date = pd.to_datetime(reference_date).date()
#
#         # Helpers & state
#         self.age_checker = FileAgeChecker(debug=self.debug, logger=self.logger)
#         self.plan: pd.DataFrame = pd.DataFrame()
#         self.df_req: pd.DataFrame = pd.DataFrame()
#
#         # internal run flag to print once per run if caller reuses instance
#         self._printed_this_run: bool = False
#
#     # --------------------- public helpers ---------------------
#     def has_plan(self) -> bool:
#         """Safe truthiness for plan existence."""
#         return isinstance(self.plan, pd.DataFrame) and not self.plan.empty
#
#     def required_count(self) -> int:
#         return 0 if not isinstance(self.df_req, pd.DataFrame) else len(self.df_req)
#
#     # --------------------- core API ---------------------
#     def generate_plan(
#         self,
#         start: Union[str, dt.date, None] = None,
#         end: Union[str, dt.date, None] = None,
#         freq: str = "D",
#     ) -> pd.DataFrame:
#         """
#         Build a plan for [start, end]. Returns rows that require update (df_req).
#         """
#         start = start or self.start_date
#         end = end or self.end_date
#         sd = pd.to_datetime(start).date()
#         ed = pd.to_datetime(end).date()
#         if sd > ed:
#             raise ValueError(f"Start date ({sd}) must be on or before end date ({ed}).")
#
#         self.logger.info(f"Generating update plan for {self.description} from {sd} to {ed}", extra=self.logger_extra)
#         self._generate_plan(sd, ed, freq=freq)
#         self.logger.info(
#             f"Plan built for {self.description}: {len(self.plan)} dates evaluated, "
#             f"{len(self.df_req)} require update",
#             extra=self.logger_extra
#         )
#         return self.df_req
#
#     def show_update_plan(self) -> None:
#         logger_extra =  self.logger_extra.update({"date_of_update": self.reference_date.strftime('%Y-%m-%d'), "dataclass": self.description,"action_module_name": "update_plan"})
#
#         """Pretty-print the current plan once per run."""
#         if not self.has_plan():
#             self.logger.info("No update plan to show.")
#             return
#         if self._printed_this_run:
#             return
#
#         try:
#             from rich.console import Console
#             from rich.table import Table
#         except Exception:
#             # Fallback: plain text
#             self.logger.info(f"Update Plan (plain list):\n{self.plan.to_string(index=False)}", extra=logger_extra)
#             self._printed_this_run = True
#             return
#
#         table = Table(
#             title=f"Update Plan for {self.data_path}",
#             show_header=True,
#             header_style="bold magenta",
#         )
#         for column in self.plan.columns:
#             table.add_column(column, justify="left")
#
#         for _, row in self.plan.iterrows():
#             table.add_row(*(str(row[col]) for col in self.plan.columns))
#
#         console = Console()
#         with console.capture() as capture:
#             console.print(table)
#         self.logger.info(f"Full Update Plan:\n{capture.get().strip()}", extra=logger_extra)
#         self._printed_this_run = True
#
#     def get_tasks_by_priority(self) -> Iterator[Tuple[int, List[dt.date]]]:
#         """
#         Yield (priority, [dates...]) batches, smallest priority first.
#         """
#         if not self.has_plan():
#             return
#         req = self.plan[self.plan["update_required"]]
#         if req.empty:
#             return
#         for priority in sorted(req["update_priority"].unique()):
#             dates_df = req[req["update_priority"] == priority]
#             # sort within group
#             dates_df = dates_df.sort_values(by="date", ascending=not self.reverse_order)
#             dates = dates_df["date"].tolist()
#             if dates:
#                 yield int(priority), dates
#
#     # --------------------- internals ---------------------
#     @staticmethod
#     def _ensure_trailing_slash(path: str) -> str:
#         return path.rstrip("/") + "/"
#
#     def _generate_plan(self, start: dt.date, end: dt.date, freq: str = "D") -> None:
#         """
#         Populate self.plan with all dates and self.df_req with the subset to update.
#         """
#         dates = pd.date_range(start=start, end=end, freq=freq).date.tolist()
#         history_start = self.reference_date - dt.timedelta(days=self.history_days_threshold)
#         rows: List[Dict] = []
#
#         # bound threads
#         max_workers = max(1, int(self.max_threads))
#
#         with ThreadPoolExecutor(max_workers=max_workers) as executor:
#             futures = {executor.submit(self._get_file_status, d): d for d in dates}
#             iterator = as_completed(futures)
#             if self.show_progress:
#                 try:
#                     from tqdm import tqdm
#                     iterator = tqdm(
#                         iterator, total=len(futures),
#                         desc=f"Scanning dates for {self.description}",
#                         unit="date", leave=False
#                     )
#                 except Exception:
#                     pass  # no tqdm → proceed without progress bar
#
#             for future in iterator:
#                 d = futures[future]
#                 try:
#                     exists, age = future.result(timeout=self.timeout)
#                     rows.append(self._make_row(d, history_start, exists, age))
#                 except Exception as exc:
#                     self.logger.error(f"Error processing date {d}: {exc}", extra=self.logger_extra)
#                     rows.append(self._make_row(d, history_start, False, None))
#
#         df = pd.DataFrame(rows)
#         # consistent types
#         if not df.empty:
#             df["date"] = pd.to_datetime(df["date"]).dt.date
#             df["update_priority"] = df["update_priority"].astype(int)
#
#         df = df.sort_values(
#             by=["update_priority", "date"],
#             ascending=[True, not self.reverse_order],
#             kind="mergesort",  # stable
#         ).reset_index(drop=True)
#
#         self.plan = df
#         self.df_req = df[df["update_required"]].copy()
#         self._printed_this_run = False
#
#     def _get_file_status(self, date: dt.date) -> Tuple[bool, Optional[float]]:
#         """
#         Check file existence and age for the given date.
#         """
#         just_path = f"{self.data_path}{date.year}/{date.month:02d}/{date.day:02d}/"
#         if just_path in self.skipped:
#             self.logger.debug(f"Skipping {date}: path in skipped list.", extra=self.logger_extra)
#             return False, None
#
#         path = f"{just_path}{self.filename}"
#         try:
#             exists = self.fs.exists(path)
#             age = self.age_checker.get_file_or_dir_age_minutes(path, self.fs) if exists else None
#             return bool(exists), age
#         except Exception as e:
#             self.logger.warning(f"exists/age check failed for {path}: {e}", extra=self.logger_extra)
#             return False, None
#
#     def _make_row(
#         self,
#         date: dt.date,
#         history_start: dt.date,
#         file_exists: bool,
#         file_age: Optional[float],
#     ) -> Dict:
#         """
#         Build a single plan row based on flags and thresholds.
#         """
#         within_history = history_start <= date <= self.reference_date
#         update_required = False
#
#         # 1) Overwrite forces update
#         if self.overwrite:
#             category = "overwrite_forced"
#             update_required = True
#         # 2) Inside history window
#         elif within_history:
#             if not file_exists:
#                 category = "missing_in_history"
#                 update_required = True
#             elif file_age is not None and file_age > self.max_age_minutes:
#                 category = "stale_in_history"
#                 update_required = True
#             else:
#                 category = "file_is_recent"
#         # 3) Outside history, missing file (and not ignoring)
#         elif not file_exists and not self.ignore_missing:
#             category = "create_missing"
#             update_required = True
#         # 4) Everything else
#         else:
#             category = "missing_ignored" if not file_exists else "file_is_recent"
#
#         return {
#             "date": date,
#             "file_exists": bool(file_exists),
#             "file_age_minutes": file_age,
#             "update_category": category,
#             "update_priority": self.priority_map.get(category, 99),
#             "update_required": bool(update_required),
#             "description": self.description,
#         }
#
#     def exclude_dates(self, dates: Set[dt.date]) -> None:
#         """
#         Exclude specific dates from the update plan.
#         """
#         if not isinstance(dates, set):
#             raise ValueError("dates must be a set[date].")
#         if not self.has_plan():
#             self.logger.info("No update plan to modify. Call generate_plan() first.", extra=self.logger_extra)
#             return
#
#         before = len(self.plan)
#         self.plan = self.plan[~self.plan["date"].isin(dates)]
#         self.df_req = self.plan[self.plan["update_required"]].copy()
#         self.logger.info(
#             f"Excluded {len(dates)} dates from the update plan (from {before} to {len(self.plan)} rows).",
#             extra=self.logger_extra
#         )