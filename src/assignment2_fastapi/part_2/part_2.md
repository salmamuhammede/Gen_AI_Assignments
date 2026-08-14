## Q5 — Trace

### 1. Number of log records

**Result:** 1

**Reason:**  
The request is successful, so only the `logger.info()` statement runs.
The `logger.error()` is inside the `except` block, so it does not run
because no exception occurs.

---

### 2. Where will the log record appear?

**Result:** Both

**Reason:**  
The logging configuration has two handlers: one for the console and one
for the `api-logs.log` file. Therefore, the same log record will appear
in both places.

- Console: Yes
- `api-logs.log`: Yes

---

### 3. What happens when the log file reaches the maximum size?

**Answer:**  
When the file reaches `10,485,760` bytes, the `RotatingFileHandler`
rotates the log file. It moves the current log file to a backup file and
creates a new `api-logs.log` file for new logs.

It can keep up to 5 backup files because `backupCount=5`.

---

### 4. How does `RotatingFileHandler` handle the existing log file?

**Answer:**  
It renames the existing log file as a backup, such as
`api-logs.log.1`, and starts writing new logs to a new
`api-logs.log` file. When there are already 5 backup files, the oldest
one is removed when a new backup is created.

---

## Q6 — Debug

### Problem

The problem is that `logger.info()` is called before
`logging.basicConfig()` is configured. Therefore, the intended logging
handlers and format may not be applied to the message.

### Corrected Code

```python
# Standard library
import logging
from logging.handlers import RotatingFileHandler

# Third-party libraries

# Local imports


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        RotatingFileHandler(
            "api-logs.log",
            maxBytes=10485760,
            backupCount=5,
        ),
        logging.StreamHandler(),
    ],
)


logger = logging.getLogger(__name__)


def main():
    logger.info("Application Starting")


if __name__ == "__main__":
    main()
```

---

## Q7 — Write

The `except` block should be modified to use `logger.exception()`:

```python
except Exception:
    # logger.exception() includes the traceback, while logger.error() does not by default.
    logger.exception("Prediction failed")
```

---

## Q8 — Write

```python
if request.temperature > 1.5:
    logger.warning(
        f"High temperature detected: {request.temperature} for model {request.model}"
    )
```