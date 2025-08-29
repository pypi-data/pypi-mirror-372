# ----------------------------------------------------------------------------
# EchoLog v3.0 — Modern Python logging with colors, levels, rotation, and JSON
# Developed by Aymene Boudali — MIT License
# ----------------------------------------------------------------------------
from __future__ import annotations

import datetime as _dt
import json as _json
import os as _os
from collections import deque
from enum import IntEnum
from typing import Callable, Deque, Dict, List, Optional, Tuple

try:
    from colorama import init as _colorama_init, Fore as _Fore, Style as _Style
    _colorama_init(autoreset=True)
    _COLORAMA_AVAILABLE = True
except Exception:  # pragma: no cover
    _COLORAMA_AVAILABLE = False
    class _Fore:
        CYAN = ""
        GREEN = ""
        BLUE = ""
        YELLOW = ""
        RED = ""
        MAGENTA = ""
        LIGHTCYAN_EX = ""
        LIGHTBLUE_EX = ""
        RESET = ""
    class _Style:
        RESET_ALL = ""


_DEFAULT_LOG_DIR = "logs"
_DATE_FMT = "%Y-%m-%d"
_TIME_FMT = "%Y-%m-%d %H:%M:%S"


class LogLevel(IntEnum):
    """Numeric log levels compatible with comparisons.

    Higher value = more severe. Used for filtering.
    """
    DEBUG = 10
    INFO = 20
    NOTICE = 25
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
    SMTP = 60
    AUDIT = 70


# Mapping: level -> (color, label)
_LEVEL_STYLE: Dict[LogLevel, Tuple[str, str]] = {
    LogLevel.DEBUG: (_Fore.CYAN, "[DEBUG]"),
    LogLevel.INFO: (_Fore.GREEN, "[INFO]"),
    LogLevel.NOTICE: (_Fore.BLUE, "[NOTICE]"),
    LogLevel.WARNING: (_Fore.YELLOW, "[WARNING]"),
    LogLevel.ERROR: (_Fore.RED, "[ERROR]"),
    LogLevel.CRITICAL: (_Fore.MAGENTA, "[CRITICAL]"),
    LogLevel.SMTP: (_Fore.LIGHTCYAN_EX, "[SMTP]"),
    LogLevel.AUDIT: (_Fore.LIGHTBLUE_EX, "[AUDIT]"),
}


def _ensure_dir(path: str) -> None:
    if not _os.path.exists(path):
        _os.makedirs(path, exist_ok=True)


def _today_filename(log_dir: str) -> str:
    return _os.path.join(log_dir, f"{_dt.datetime.now().strftime(_DATE_FMT)}.log")


def _now_str() -> str:
    return _dt.datetime.now().strftime(_TIME_FMT)


class Logger:
    """EchoLog main logger.

    Features:
    - Color-coded console output (auto-disabled if colorama missing or color=False)
    - Daily log file naming (YYYY-MM-DD.log)
    - Global level filtering
    - Optional JSON output
    - Optional rotation: by file size with backup history; optional retention by days
    - In-memory ring buffer of recent log records
    - Extensible: custom handlers invoked on each record

    Args:
        name: Optional short name to include in each message.
        level: Minimum level to emit (default: INFO).
        color: Enable colored console output when possible.
        log_dir: Directory for log files (default: "logs").
        json_output: If True, print JSON lines to console and file.
        memory: Number of recent entries to keep in memory (0 to disable).
        rotation: Dict configuration, e.g. {"type":"size", "max_bytes": 1_000_000, "backup_count": 5}
        retention_days: If set, delete log files older than this many days.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        level: LogLevel = LogLevel.INFO,
        *,
        color: bool = True,
        log_dir: str = _DEFAULT_LOG_DIR,
        json_output: bool = False,
        memory: int = 500,
        rotation: Optional[Dict[str, int]] = None,
        retention_days: Optional[int] = None,
    ) -> None:
        self.name = name
        self.level: LogLevel = LogLevel(level)
        self.color = bool(color and _COLORAMA_AVAILABLE)
        self.log_dir = log_dir
        self.json_output = json_output
        self._custom_format: Optional[Callable[[str, LogLevel], str]] = None
        self._handlers: List[Callable[[Dict[str, str]], None]] = []

        _ensure_dir(self.log_dir)
        self._file_path = _today_filename(self.log_dir)

        self._rotation = rotation or {}
        self._retention_days = retention_days

        self._buffer: Deque[Dict[str, str]] = deque(maxlen=memory) if memory > 0 else deque(maxlen=0)

        # housekeeping
        self._apply_retention()

    # ------------------------------- public API -------------------------------
    def set_level(self, level: LogLevel | int | str) -> None:
        if isinstance(level, str):
            level = level.upper()
            try:
                self.level = LogLevel[level]
            except KeyError:
                raise ValueError(f"Unknown level name: {level}")
        else:
            self.level = LogLevel(level)

    def enable_color(self) -> None:
        self.color = True and _COLORAMA_AVAILABLE

    def disable_color(self) -> None:
        self.color = False

    def set_custom_format(self, formatter: Callable[[str, LogLevel], str]) -> None:
        self._custom_format = formatter

    def add_handler(self, fn: Callable[[Dict[str, str]], None]) -> None:
        """Register a callback invoked with the structured record for each log."""
        self._handlers.append(fn)

    def get_logs(self) -> List[str]:
        """Read the current day's log file into memory and return lines."""
        try:
            with open(self._file_path, "r", encoding="utf-8") as f:
                return f.readlines()
        except FileNotFoundError:
            return []

    def file_name(self) -> str:
        return self._file_path

    # Convenience level methods
    def debug(self, text: str, *, print_only: bool = False) -> None:
        self._log(LogLevel.DEBUG, text, print_only=print_only)

    def info(self, text: str) -> None:
        self._log(LogLevel.INFO, text)

    def notice(self, text: str) -> None:
        self._log(LogLevel.NOTICE, text)

    def warning(self, text: str) -> None:
        self._log(LogLevel.WARNING, text)

    def error(self, text: str) -> None:
        self._log(LogLevel.ERROR, text)

    def critical(self, text: str) -> None:
        self._log(LogLevel.CRITICAL, text)

    def smtp(self, text: str) -> None:
        self._log(LogLevel.SMTP, text)

    def audit(self, text: str) -> None:
        self._log(LogLevel.AUDIT, text)

    # ------------------------------ core logging ------------------------------
    def _log(self, level: LogLevel, text: str, *, print_only: bool = False) -> None:
        if level < self.level:
            return

        now = _now_str()
        name_part = f" [{self.name}]" if self.name else ""
        color, label = _LEVEL_STYLE.get(level, ("", f"[{level.name}]"))

        record = {
            "timestamp": now,
            "level": level.name,
            "label": label,
            "name": self.name or "",
            "message": text,
            "file": self._file_path,
        }

        # Format console and file lines
        if self.json_output:
            console_line = _json.dumps(record, ensure_ascii=False)
            file_line = console_line
        else:
            if self._custom_format:
                console_line = self._custom_format(text, level)
                file_line = f"[{now}] {label}{name_part} {text}"
            else:
                if self.color:
                    console_line = f"\x1b[90m{now}\x1b[0m {color}{label}{_Style.RESET_ALL}{name_part} {text}"
                else:
                    console_line = f"{now} {label}{name_part} {text}"
                file_line = f"[{now}] {label}{name_part} {text}"

        # Write to file unless print_only
        if not print_only:
            self._rollover_if_needed()
            with open(self._file_path, "a", encoding="utf-8") as f:
                f.write(file_line + "\n")

        # Console output
        print(console_line)

        # Memory buffer
        if self._buffer.maxlen and self._buffer.maxlen > 0:
            self._buffer.append(record)

        # Handlers
        for h in self._handlers:
            try:
                h(record)
            except Exception:
                # Handlers must not crash the logger
                pass

    # --------------------------- rotation & retention -------------------------
    def _rollover_if_needed(self) -> None:
        # New day? switch file
        expected = _today_filename(self.log_dir)
        if expected != self._file_path:
            self._file_path = expected

        # Size-based rotation
        if self._rotation.get("type") == "size":
            max_bytes = int(self._rotation.get("max_bytes", 5_000_000))
            backup_count = int(self._rotation.get("backup_count", 5))
            size = _os.path.getsize(self._file_path) if _os.path.exists(self._file_path) else 0
            if size >= max_bytes:
                self._rotate_files(self._file_path, backup_count)

    def _rotate_files(self, base_path: str, backup_count: int) -> None:
        # Remove oldest
        oldest = f"{base_path}.{backup_count}"
        if _os.path.exists(oldest):
            try:
                _os.remove(oldest)
            except Exception:
                pass
        # Shift others
        for i in range(backup_count - 1, 0, -1):
            src = f"{base_path}.{i}"
            dst = f"{base_path}.{i+1}"
            if _os.path.exists(src):
                try:
                    _os.replace(src, dst)
                except Exception:
                    pass
        # Rotate current
        if _os.path.exists(base_path):
            try:
                _os.replace(base_path, f"{base_path}.1")
            except Exception:
                pass

    def _apply_retention(self) -> None:
        if not self._retention_days:
            return
        cutoff = _dt.datetime.now() - _dt.timedelta(days=int(self._retention_days))
        for name in _os.listdir(self.log_dir):
            path = _os.path.join(self.log_dir, name)
            if not name.endswith(".log"):
                continue
            try:
                date_str = name[:-4]  # YYYY-MM-DD
                dt = _dt.datetime.strptime(date_str, _DATE_FMT)
                if dt < cutoff:
                    _os.remove(path)
            except Exception:
                # ignore files with unexpected names
                pass