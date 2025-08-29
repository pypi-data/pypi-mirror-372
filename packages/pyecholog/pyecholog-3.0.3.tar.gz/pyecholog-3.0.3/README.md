# EchoLog

**EchoLog** is a modern, colorful logging library for Python with:
- Color-coded console output
- Daily log files
- Global level filtering
- Optional JSON output
- Size-based rotation with backups
- Retention policy by days
- In-memory ring buffer
- Custom handlers for integrations (e.g., send to webhook)

## Install
```bash
pip install echolog
````

## Quick Start

```python
from echolog import Logger, LogLevel

logger = Logger(
    name="MyApp",
    level=LogLevel.INFO,
    color=True,
    log_dir="logs",
    json_output=False,
    rotation={"type": "size", "max_bytes": 1_000_000, "backup_count": 5},
    retention_days=14,
)

logger.info("Application started")
logger.warning("This is a warning")
logger.error("Something failed")

# Change level dynamically
logger.set_level("DEBUG")
logger.debug("Debug details")

# Add a custom handler
logger.add_handler(lambda rec: print("[HOOK]", rec["level"], rec["message"]))
```

## JSON Output

```python
Logger(json_output=True).info("Structured log")
```

## Disable Colors

```python
logger.disable_color()
```

## Read Current Log File

```python
print("Log file:", logger.file_name())
print("Lines:", logger.get_logs()[:5])
```