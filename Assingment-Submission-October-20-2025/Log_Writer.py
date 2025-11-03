#!/usr/bin/env python3
"""
Log writer that tracks script execution time and errors.

Features:
- Rotating file + console logging
- Run ID to correlate all logs from one execution
- Context manager and decorator for timing steps
- Automatic exception logging with tracebacks
"""

import argparse
import logging
import os
import sys
import time
import uuid
from logging.handlers import RotatingFileHandler
from functools import wraps

# --------- 1) Logger setup ---------
def setup_logger(log_path: str,
                 level: int = logging.INFO,
                 max_bytes: int = 5_000_000,
                 backup_count: int = 3,
                 fmt: str | None = None,
                 run_id: str | None = None) -> tuple[logging.Logger, str]:
    """
    Create a logger that writes to console and a rotating file.

    Returns (logger, run_id).
    """
    os.makedirs(os.path.dirname(log_path) or ".", exist_ok=True)
    logger = logging.getLogger("logwriter")
    logger.setLevel(level)
    logger.handlers.clear()  # avoid duplicate handlers if called twice

    # Attach a run_id so you can filter/grep all logs for one execution
    run_id = run_id or str(uuid.uuid4())[:8]

    # Default format: timestamp level run_id module:line - message
    fmt = fmt or "%(asctime)s %(levelname)-8s [run=%(run_id)s] %(name)s:%(lineno)d - %(message)s"
    formatter = logging.Formatter(fmt, datefmt="%Y-%m-%d %H:%M:%S")

    # We inject run_id to every LogRecord using a Filter
    class RunIdFilter(logging.Filter):
        def filter(self, record):
            record.run_id = run_id
            return True

    # File handler (rotating)
    fh = RotatingFileHandler(log_path, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
    fh.setLevel(level)
    fh.setFormatter(formatter)
    fh.addFilter(RunIdFilter())
    logger.addHandler(fh)

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    ch.setFormatter(formatter)
    ch.addFilter(RunIdFilter())
    logger.addHandler(ch)

    logger.debug("Logger initialized.")
    return logger, run_id


# --------- 2) Timing tools ---------
class log_time:
    """
    Context manager to time a code block and log its duration.

    Usage:
        with log_time(logger, "load_data"):
            ...
    """
    def __init__(self, logger: logging.Logger, label: str, level=logging.INFO):
        self.logger = logger
        self.label = label
        self.level = level
        self._t0 = None

    def __enter__(self):
        self._t0 = time.perf_counter()
        self.logger.log(self.level, f"START: {self.label}")
        return self

    def __exit__(self, exc_type, exc, tb):
        elapsed = (time.perf_counter() - self._t0) * 1000.0  # ms
        if exc_type is None:
            self.logger.log(self.level, f"END:   {self.label} (elapsed={elapsed:.2f} ms)")
            return False  # do not suppress
        else:
            # Log the error with traceback, then propagate
            self.logger.exception(f"ERROR during '{self.label}' (elapsed={elapsed:.2f} ms): {exc}")
            return False  # re-raise after logging


def timed(label: str | None = None, level=logging.INFO):
    """
    Decorator to time a function and log duration & errors.

    Usage:
        @timed("compute_stats")
        def compute_stats(...):
            ...
    """
    def decorator(func):
        func_label = label or func.__name__

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Expect a logger in kwargs or fallback to module logger
            logger = kwargs.get("logger") or logging.getLogger("logwriter")
            t0 = time.perf_counter()
            logger.log(level, f"START: {func_label}")
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                elapsed = (time.perf_counter() - t0) * 1000.0
                logger.exception(f"ERROR in '{func_label}' (elapsed={elapsed:.2f} ms): {e}")
                raise
            finally:
                elapsed = (time.perf_counter() - t0) * 1000.0
                logger.log(level, f"END:   {func_label} (elapsed={elapsed:.2f} ms)")

        return wrapper
    return decorator


# --------- 3) Example workload (for demo/CLI) ---------
@timed("fake_step_compute")
def fake_compute(n: int, *, logger: logging.Logger):
    total = 0
    for i in range(n):
        total += i * i
    # Simulate a small delay
    time.sleep(0.1)
    return total

@timed()  # label defaults to function name
def fake_io(*, logger: logging.Logger):
    time.sleep(0.05)
    return "ok-io"


# --------- 4) Script entry point with error handling ---------
def main():
    ap = argparse.ArgumentParser(description="Demo: log writer with timing and errors")
    ap.add_argument("--log", default="logs/app.log", help="Path to log file")
    ap.add_argument("--fail", action="store_true", help="Intentionally raise an error to show exception logging")
    args = ap.parse_args()

    logger, run_id = setup_logger(args.log, level=logging.INFO)
    logger.info(f"Script START (run_id={run_id}) pid={os.getpid()} python={sys.version.split()[0]}")

    try:
        with log_time(logger, "pipeline"):
            with log_time(logger, "step:load"):
                time.sleep(0.02)  # simulate load

            # Decorated function calls
            result = fake_compute(50_000, logger=logger)
            logger.info(f"fake_compute result={result}")

            _ = fake_io(logger=logger)

            if args.fail:
                # This will be logged with full traceback by the context manager/decorator
                raise RuntimeError("Boom! Something went wrong")

    finally:
        logger.info("Script END")

if __name__ == "__main__":
    main()
