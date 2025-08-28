from __future__ import annotations

from typing import Union
import dask.dataframe as dd
import pandas as pd

from sibi_dst.df_helper import DfHelper


class BaseDataCube(DfHelper):
    """
    Base cube with sync/async load hooks.

    Subclasses *may* override:
      - fix_data(self, **kwargs): synchronous, local transforms
      - async afix_data(self, **kwargs): asynchronous transforms (I/O, awaits)

    Semantics:
      - load() -> runs fix_data() if defined
      - aload() -> runs afix_data() if subclass overrides it, else fix_data()
    """
    df: Union[dd.DataFrame, pd.DataFrame, None] = None
    config: dict = {}

    def __init__(self, **kwargs):
        # kwargs override class config
        kwargs = {**self.config, **kwargs}
        super().__init__(**kwargs)

    # -------------------- optional hooks --------------------

    def fix_data(self, **kwargs) -> None:
        """Optional sync transform hook. Override in subclasses if needed."""
        return None

    async def afix_data(self, **kwargs) -> None:
        """Optional async transform hook. Override in subclasses if needed."""
        return None

    # -------------------- internals --------------------

    def _has_data(self) -> bool:
        """Check if dataframe has rows; avoids hidden heavy ops where possible."""
        if self.df is None:
            return False
        if isinstance(self.df, dd.DataFrame):
            return bool(self.df.shape[0].compute() > 0)
        return not self.df.empty

    def _afix_data_is_overridden(self) -> bool:
        """Check if subclass provided its own afix_data."""
        return self.__class__.afix_data is not BaseDataCube.afix_data

    def _fix_data_is_overridden(self) -> bool:
        """Check if subclass provided its own fix_data."""
        return self.__class__.fix_data is not BaseDataCube.fix_data

    # -------------------- public API --------------------

    def load(self, **kwargs):
        """Sync load path with optional fix_data hook."""
        self.df = super().load(**kwargs)
        if self._has_data() and self._fix_data_is_overridden():
            self.fix_data()
        elif not self._has_data():
            self.logger.debug(f"No data was found by {self.__class__.__name__} loader")
        return self.df

    async def aload(self, **kwargs):
        """Async load path with optional afix_data/fix_data hook."""
        self.df = await super().aload(**kwargs)
        if self._has_data():
            if self._afix_data_is_overridden():
                await self.afix_data()
            elif self._fix_data_is_overridden():
                self.fix_data()
        else:
            self.logger.debug(f"No data was found by {self.__class__.__name__} loader")
        return self.df
