from __future__ import annotations

import logging
import os
import sys
import time
from contextlib import contextmanager, nullcontext, suppress
from logging import LoggerAdapter
from logging.handlers import RotatingFileHandler
from typing import Optional, Dict, Any, Union

# --- OpenTelemetry (optional) ---
try:
    from opentelemetry import trace
    from opentelemetry._logs import set_logger_provider, get_logger_provider
    from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
    from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    _OTEL_AVAILABLE = True
except Exception:
    _OTEL_AVAILABLE = False


class Logger:
    """
    Process-safe logger with optional OpenTelemetry integration.
    Idempotent handler setup. No propagation to root.
    """

    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    # idempotency guards per process
    _attached_keys: set[tuple[str, str]] = set()  # (logger_name, sink_id)
    _otel_initialized_names: set[str] = set()

    def __init__(
        self,
        log_dir: str,
        logger_name: str,
        log_file: str,
        log_level: int = logging.INFO,
        enable_otel: bool = False,
        otel_service_name: Optional[str] = None,
        otel_stream_name: Optional[str] = None,
        otel_endpoint: str = "0.0.0.0:4317",
        otel_insecure: bool = False,
    ):
        self.log_dir = log_dir
        self.logger_name = logger_name
        self.log_file = log_file
        self.log_level = log_level

        self.enable_otel = bool(enable_otel and _OTEL_AVAILABLE)
        self.otel_service_name = (otel_service_name or logger_name or "app").strip()
        self.otel_stream_name = (otel_stream_name or "").strip() or None
        self.otel_endpoint = otel_endpoint
        self.otel_insecure = otel_insecure

        self.logger_provider = None
        self.tracer_provider = None
        self.tracer = None

        self._core: logging.Logger = logging.getLogger(self.logger_name)
        self._core.setLevel(self.log_level)
        self._core.propagate = False

        # public handle (may be LoggerAdapter)
        self.logger: Union[logging.Logger, LoggerAdapter] = self._core

        self._setup_handlers()
        if self.enable_otel:
            self._setup_otel()

        if self.enable_otel and self.otel_stream_name:
            attrs = {
                "log_stream": self.otel_stream_name,
                "log_service_name": self.otel_service_name,
                "logger_name": self.logger_name,
            }
            self.logger = LoggerAdapter(self._core, extra=attrs)

    # ---------------- Public API ----------------

    @classmethod
    def default_logger(
        cls,
        log_dir: str = "./logs/",
        logger_name: Optional[str] = None,
        log_file: Optional[str] = None,
        log_level: int = logging.INFO,
        enable_otel: bool = False,
        otel_service_name: Optional[str] = None,
        otel_stream_name: Optional[str] = None,
        otel_endpoint: str = "0.0.0.0:4317",
        otel_insecure: bool = False,
    ) -> "Logger":
        try:
            caller_name = sys._getframe(1).f_globals.get("__name__", "default_logger")
        except Exception:
            caller_name = "default_logger"
        logger_name = logger_name or caller_name
        log_file = log_file or logger_name
        return cls(
            log_dir=log_dir,
            logger_name=logger_name,
            log_file=log_file,
            log_level=log_level,
            enable_otel=enable_otel,
            otel_service_name=otel_service_name,
            otel_stream_name=otel_stream_name,
            otel_endpoint=otel_endpoint,
            otel_insecure=otel_insecure,
        )

    def set_level(self, level: int) -> None:
        self._core.setLevel(level)

    # passthrough
    def _log(self, level: int, msg: str, *args, **kwargs) -> None:
        extra = kwargs.pop("extra", None)
        if extra is not None:
            if isinstance(self.logger, LoggerAdapter):
                merged = {**self.logger.extra, **extra}
                LoggerAdapter(self.logger.logger, merged).log(level, msg, *args, **kwargs)
            else:
                LoggerAdapter(self.logger, extra).log(level, msg, *args, **kwargs)
        else:
            self.logger.log(level, msg, *args, **kwargs)

    def debug(self, msg: str, *a, **k): self._log(logging.DEBUG, msg, *a, **k)
    def info(self, msg: str, *a, **k): self._log(logging.INFO, msg, *a, **k)
    def warning(self, msg: str, *a, **k): self._log(logging.WARNING, msg, *a, **k)
    def error(self, msg: str, *a, **k): self._log(logging.ERROR, msg, *a, **k)
    def critical(self, msg: str, *a, **k): self._log(logging.CRITICAL, msg, *a, **k)

    def bind(self, **extra: Any) -> LoggerAdapter:
        if isinstance(self.logger, LoggerAdapter):
            return LoggerAdapter(self.logger.logger, {**self.logger.extra, **extra})
        return LoggerAdapter(self.logger, extra)

    @contextmanager
    def bound(self, **extra: Any):
        yield self.bind(**extra)

    def start_span(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        if not (self.enable_otel and _OTEL_AVAILABLE and self.tracer):
            return nullcontext()
        cm = self.tracer.start_as_current_span(name)
        class _SpanCtx:
            def __enter__(_self):
                span = cm.__enter__()
                if attributes:
                    for k, v in attributes.items():
                        with suppress(Exception):
                            span.set_attribute(k, v)
                return span
            def __exit__(_self, et, ev, tb):
                return cm.__exit__(et, ev, tb)
        return _SpanCtx()

    def trace_function(self, span_name: Optional[str] = None):
        def deco(func):
            def wrapper(*a, **k):
                name = span_name or func.__name__
                with self.start_span(name):
                    return func(*a, **k)
            return wrapper
        return deco

    def shutdown(self) -> None:
        try:
            if self.enable_otel and _OTEL_AVAILABLE:
                if self.logger_provider:
                    with suppress(Exception):
                        self._core.info("Flushing OpenTelemetry logs...")
                        self.logger_provider.force_flush()
                    with suppress(Exception):
                        self._core.info("Shutting down OpenTelemetry logs...")
                        self.logger_provider.shutdown()
                if self.tracer_provider:
                    with suppress(Exception):
                        self._core.info("Flushing OpenTelemetry traces...")
                        self.tracer_provider.force_flush()
                    with suppress(Exception):
                        self._core.info("Shutting down OpenTelemetry traces...")
                        self.tracer_provider.shutdown()
        finally:
            for h in list(self._core.handlers):
                with suppress(Exception): h.flush()
                with suppress(Exception): h.close()
                with suppress(Exception): self._core.removeHandler(h)
            logging.shutdown()

    # ---------------- Internal ----------------

    def _setup_handlers(self) -> None:
        os.makedirs(self.log_dir, exist_ok=True)
        calling_script = os.path.splitext(os.path.basename(sys.argv[0]))[0]
        log_file_path = os.path.join(self.log_dir, f"{self.log_file}_{calling_script}.log")
        file_key = (self.logger_name, os.path.abspath(log_file_path))
        console_key = (self.logger_name, "__console__")

        fmt = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        fmt.converter = time.gmtime  # UTC

        if file_key not in self._attached_keys:
            fh = RotatingFileHandler(log_file_path, maxBytes=5 * 1024 * 1024, backupCount=5, delay=True)
            fh.setFormatter(fmt)
            self._core.addHandler(fh)
            self._attached_keys.add(file_key)

        if console_key not in self._attached_keys:
            ch = logging.StreamHandler(sys.stdout)
            ch.setFormatter(fmt)
            self._core.addHandler(ch)
            self._attached_keys.add(console_key)

    def _normalize_otlp_endpoint(self, ep: str) -> str:
        if "://" not in ep:
            ep = ("http://" if self.otel_insecure else "https://") + ep
        return ep

    def _setup_otel(self) -> None:
        if not _OTEL_AVAILABLE:
            self._core.warning("OpenTelemetry not available — skipping OTel setup.")
            return
        if self.logger_name in self._otel_initialized_names:
            with suppress(Exception):
                self.tracer = trace.get_tracer(self.logger_name)
            return

        # resources
        attrs = {"service.name": self.otel_service_name, "logger.name": self.logger_name}
        if self.otel_stream_name:
            attrs["log.stream"] = self.otel_stream_name
        resource = Resource.create(attrs)

        # providers (reuse if already set globally)
        existing_lp = None
        with suppress(Exception):
            existing_lp = get_logger_provider()
        if getattr(existing_lp, "add_log_record_processor", None):
            self.logger_provider = existing_lp
        else:
            self.logger_provider = LoggerProvider(resource=resource)
            set_logger_provider(self.logger_provider)

        existing_tp = None
        with suppress(Exception):
            existing_tp = trace.get_tracer_provider()
        if getattr(existing_tp, "add_span_processor", None):
            self.tracer_provider = existing_tp
        else:
            self.tracer_provider = TracerProvider(resource=resource)
            trace.set_tracer_provider(self.tracer_provider)

        endpoint = self._normalize_otlp_endpoint(self.otel_endpoint)

        # exporters/processors (only if we own the providers we created above)
        if isinstance(self.logger_provider, LoggerProvider):
            with suppress(Exception):
                log_exporter = OTLPLogExporter(endpoint=endpoint, insecure=self.otel_insecure)
                self.logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))

        if isinstance(self.tracer_provider, TracerProvider):
            with suppress(Exception):
                span_exporter = OTLPSpanExporter(endpoint=endpoint, insecure=self.otel_insecure)
                self.tracer_provider.add_span_processor(BatchSpanProcessor(span_exporter))

        # attach OTel log handler once
        if not any(type(h).__name__ == "LoggingHandler" for h in self._core.handlers):
            with suppress(Exception):
                self._core.addHandler(LoggingHandler(level=logging.NOTSET, logger_provider=self.logger_provider))  # type: ignore

        with suppress(Exception):
            self.tracer = trace.get_tracer(self.logger_name)

        self._otel_initialized_names.add(self.logger_name)
        self._core.info("OpenTelemetry logging/tracing initialized.")