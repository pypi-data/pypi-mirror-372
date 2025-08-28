#!/usr/bin/env python3
"""
Console utilities using Rich for beautiful terminal output.
"""

# IMPORTS
########################################################
# Standard library imports
import contextlib
import json
import logging
from enum import Enum
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

# Third-party imports
from rich.console import Console
from rich.text import Text

# Local imports
# (None for this file)


# CONSTANTS
########################################################
# Configuration values and constants

# Color mapping for essential patterns
PATTERN_COLORS = {
    # === MAIN PATTERNS ===
    "SUCCESS": "bright_green",  # 🟢 Success
    "ERROR": "bright_red",  # 🔴 Error
    "WARN": "bright_yellow",  # 🟡 Warning
    "TIP": "bright_magenta",  # 🟣 Tip
    "DEBUG": "dim white",  # ⚪ Debug (dimmed)
    # === SYSTEM PATTERNS ===
    "SYSTEM": "bright_blue",  # 🔵 System operations
    "INSTALL": "bright_green",  # 🟢 Installation
    "DETECT": "bright_blue",  # 🔵 Detection/Analysis
    "CONFIG": "bright_green",  # 🟢 Configuration
    "DEPS": "bright_cyan",  # 🔵 Dependencies
}


# CLASSES
########################################################
# Class and enumeration definitions


class LogLevel(Enum):
    """Logging levels with colors."""

    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
    CRITICAL = "critical"


# CONFIGURATION
########################################################
# Global variables and settings

# Global console instance
console = Console()

# Minimum configurable log level (default INFO)
_min_log_level = LogLevel.INFO

# Optional structured file logger (disabled by default)
_structured_logger: Optional[logging.Logger] = None
_log_json_format: bool = False

# Map UI log levels to Python logging
_PY_LOG_LEVEL = {
    LogLevel.DEBUG: logging.DEBUG,
    LogLevel.INFO: logging.INFO,
    LogLevel.WARN: logging.WARNING,
    LogLevel.ERROR: logging.ERROR,
    LogLevel.CRITICAL: logging.CRITICAL,
}


# CONFIGURATION FUNCTIONS
########################################################
# Settings and configuration management


def set_log_level(level: LogLevel):
    """Configure the minimum logging level."""
    global _min_log_level
    _min_log_level = level


def configure_file_logging(
    log_path: Optional[str] = None,
    level: LogLevel = LogLevel.INFO,
    json_format: bool = False,
    max_bytes: int = 1_000_000,
    backup_count: int = 3,
) -> None:
    """Enable structured file logging (rotating handler).

    Args:
        log_path: Optional path to log file. Defaults to ~/.womm/.logs/womm.log
        level: Minimum UI level to write to file
        json_format: If True, write JSON lines
        max_bytes: Max file size before rotation
        backup_count: Number of rotated files to keep
    """
    global _structured_logger, _log_json_format

    # Determine default log file path
    if not log_path:
        default_dir = Path.home() / ".womm" / ".logs"
        default_dir.mkdir(parents=True, exist_ok=True)
        log_path = str(default_dir / "womm.log")

    logger = logging.getLogger("womm")
    logger.setLevel(_PY_LOG_LEVEL.get(level, logging.INFO))

    # Clear existing file handlers to avoid duplicates
    for h in list(logger.handlers):
        if isinstance(h, RotatingFileHandler):
            logger.removeHandler(h)
            h.close()

    file_handler = RotatingFileHandler(
        log_path, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
    )

    if json_format:
        # Plain message; we will pass JSON string as the LogRecord message
        formatter = logging.Formatter("%(message)s")
    else:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    _structured_logger = logger
    _log_json_format = json_format


def disable_file_logging() -> None:
    """Disable structured file logging and close handlers."""
    global _structured_logger
    if _structured_logger is None:
        return
    for h in list(_structured_logger.handlers):
        _structured_logger.removeHandler(h)
        with contextlib.suppress(Exception):
            h.close()
    _structured_logger = None


def to_loglevel(value: str) -> LogLevel:
    """Convert string to LogLevel (case-insensitive)."""
    value_norm = (value or "").strip().lower()
    mapping = {
        "debug": LogLevel.DEBUG,
        "info": LogLevel.INFO,
        "warn": LogLevel.WARN,
        "warning": LogLevel.WARN,
        "error": LogLevel.ERROR,
        "critical": LogLevel.CRITICAL,
    }
    return mapping.get(value_norm, LogLevel.INFO)


def configure_logging(
    level: LogLevel = LogLevel.INFO,
    file: Optional[str] = None,
    json_format: bool = False,
    max_bytes: int = 1_000_000,
    backup_count: int = 3,
) -> None:
    """Configure both console print level and optional file logger."""
    set_log_level(level)
    if file:
        configure_file_logging(
            log_path=file,
            level=level,
            json_format=json_format,
            max_bytes=max_bytes,
            backup_count=backup_count,
        )
    else:
        disable_file_logging()


def get_log_level() -> LogLevel:
    """Return the current minimum logging level."""
    return _min_log_level


def _should_print(level: LogLevel) -> bool:
    """Check if a level should be displayed based on the minimum configured level."""
    # Order of severity levels (from least to most critical)
    level_order = {
        LogLevel.DEBUG: 0,
        LogLevel.INFO: 1,
        LogLevel.WARN: 2,
        LogLevel.ERROR: 3,
        LogLevel.CRITICAL: 4,
    }

    return level_order.get(level, 0) >= level_order.get(_min_log_level, 1)


def set_debug_level():
    """Set logging level to DEBUG."""
    set_log_level(LogLevel.DEBUG)


def set_info_level():
    """Set logging level to INFO."""
    set_log_level(LogLevel.INFO)


def set_warn_level():
    """Set logging level to WARN."""
    set_log_level(LogLevel.WARN)


def set_error_level():
    """Set logging level to ERROR."""
    set_log_level(LogLevel.ERROR)


def set_critical_level():
    """Set logging level to CRITICAL."""
    set_log_level(LogLevel.CRITICAL)


# MAIN FUNCTIONS
########################################################
# Core functionality and primary operations


def print_pattern(level: LogLevel, pattern: str, message: str, **kwargs):
    """
    Display a message with the new format: • PATTERN :: message

    Args:
        level: Logging level (DEBUG, INFO, WARN, ERROR, CRITICAL)
        pattern: Contextual pattern (SUCCESS, ERROR, SYSTEM, etc.)
        message: Message to display
        **kwargs: Arguments passed to console.print()
    """
    # Check if the level should be displayed
    if not _should_print(level):
        return

    pattern_color = PATTERN_COLORS.get(pattern, "white")

    # Build text with the new format
    text = Text()
    text.append("• ", style=pattern_color)
    text.append(pattern.ljust(8), style=f"bold {pattern_color}")
    text.append(":: ", style="dim white")
    text.append(str(message), style="white")

    console.print(text, **kwargs)

    # Structured logging to file if enabled
    if _structured_logger is not None:
        py_level = _PY_LOG_LEVEL.get(level, logging.INFO)
        record = {
            "level": level.value,
            "pattern": pattern.strip() or "INFO",
            "message": str(message),
        }
        if _log_json_format:
            _structured_logger.log(py_level, json.dumps(record, ensure_ascii=False))
        else:
            _structured_logger.log(
                py_level, f"[{record['pattern']}] {record['message']}"
            )


def print_info(message: str, **kwargs):
    """Display an info message."""
    print_pattern(LogLevel.INFO, "INFO", message, **kwargs)


def print_debug(message: str, **kwargs):
    """Display a debug message."""
    print_pattern(LogLevel.DEBUG, "DEBUG", message, **kwargs)


def print_success(message: str, level: LogLevel = LogLevel.INFO, **kwargs):
    """Display a success message."""
    print_pattern(level, "SUCCESS", message, **kwargs)


def print_error(message: str, level: LogLevel = LogLevel.ERROR, **kwargs):
    """Display an error message."""
    print_pattern(level, "ERROR", message, **kwargs)


def print_warn(message: str, level: LogLevel = LogLevel.WARN, **kwargs):
    """Display a warning message."""
    print_pattern(level, "WARN", message, **kwargs)


def print_tip(message: str, level: LogLevel = LogLevel.INFO, **kwargs):
    """Display a tip message."""
    print_pattern(level, "TIP", message, **kwargs)


def print_system(message: str, level: LogLevel = LogLevel.INFO, **kwargs):
    """Display a system message."""
    print_pattern(level, "SYSTEM", message, **kwargs)


def print_install(message: str, level: LogLevel = LogLevel.INFO, **kwargs):
    """Display an installation message."""
    print_pattern(level, "INSTALL", message, **kwargs)


def print_detect(message: str, level: LogLevel = LogLevel.INFO, **kwargs):
    """Display a detection message."""
    print_pattern(level, "DETECT", message, **kwargs)


def print_config(message: str, level: LogLevel = LogLevel.INFO, **kwargs):
    """Display a configuration message."""
    print_pattern(level, "CONFIG", message, **kwargs)


def print_deps(message: str, level: LogLevel = LogLevel.INFO, **kwargs):
    """Display a dependencies message."""
    print_pattern(level, "DEPS", message, **kwargs)


# UTILITY FUNCTIONS
########################################################
# Helper functions and utilities


def print_header(title: str, **kwargs):
    """Display a header with separators."""
    console.print(f"{':' * 80}", style="dim black", **kwargs)
    console.print(
        f"** {title} **",
        style="bold black",
        justify="center",
        width=80,
        **kwargs,
    )
    console.print(f"{':' * 80}", style="dim black", **kwargs)
    console.print("")


def print_separator(separator: str = "-", **kwargs):
    """Display a separation line."""
    console.print(separator * 80, style="dim white", **kwargs)


def print_command(command: str, **kwargs):
    """Display an executed command."""
    console.print(f"$ {command}", style="bold cyan", **kwargs)


def print_result(result: str, success: bool = True, **kwargs):
    """Display the result of an operation."""
    style = "bold green" if success else "bold red"
    console.print(result, style=style, **kwargs)
