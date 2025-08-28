import keyword
import re
import threading
from sqlalchemy.engine import Engine

from ._model_registry import ModelRegistry, apps_label


# Global process-wide registry for backward compatibility
_global_model_registry = ModelRegistry()


class SqlAlchemyModelBuilder:
    """
    Builds a single SQLAlchemy ORM model from a specific database table.
    Thread-safe and uses a process-wide registry for reuse.

    Backward compatibility:
      - Keeps CamelCase(table) as preferred class name
      - Publishes classes under `apps_label` unless overridden
      - Public API unchanged
    """

    _lock = threading.Lock()

    def __init__(self, engine: Engine, table_name: str):
        self.engine = engine
        self.table_name = table_name

    def build_model(self) -> type:
        with self._lock:
            return _global_model_registry.get_model(
                engine=self.engine,
                table_name=self.table_name,
                module_label=apps_label,
                prefer_stable_names=True,
            )

    @staticmethod
    def _normalize_class_name(table_name: str) -> str:
        return "".join(word.capitalize() for word in table_name.split("_"))

    @staticmethod
    def _normalize_column_name(column_name: str) -> str:
        sane_name = re.sub(r"\W", "_", column_name)
        sane_name = re.sub(r"^\d", r"_\g<0>", sane_name)
        if keyword.iskeyword(sane_name):
            return f"{sane_name}_field"
        return sane_name

