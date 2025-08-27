# 📘 SmartProfiler & ContextLogger

A **lightweight Python toolkit** for profiling function execution times and enhancing logging with **contextual information** and **AI-powered error suggestions**.

---

## ✨ Features

### 🔍 SmartProfiler

* Captures **nested function timings** using `sys.setprofile`.
* Measures execution time of each function call.
* Provides detailed breakdowns for performance tuning.

### 📝 ContextLogger

* Adds **caller context** (function, file, line number) to every log.
* Supports **JSON** and **human-readable** logging modes.
* Captures exceptions with **tracebacks**.
* Generates **error fix suggestions** using Hugging Face’s `transformers`.

---

## 🚀 Installation

```bash
pip install transformers torch
```

> `torch` is required for Hugging Face `transformers`.

---

## ⚡ Quick Start

### 1. Setup Logging

```python
import logging
from your_module import ContextLogger

logging.basicConfig(level=logging.DEBUG)
base_logger = logging.getLogger("app")

logger = ContextLogger(base_logger, json_mode=False)
```

### 2. Logging Examples

#### Info & Debug Logs

```python
logger.info("Application started")
logger.debug("Configuration loaded successfully")
```

#### Warnings

```python
logger.warning("Low disk space detected")
```

#### Errors with Auto-Suggestions

```python
try:
    1 / 0
except Exception:
    logger.error("Division error occurred")
```

📌 Example output:

```
2025-08-26 19:45:12 - ERROR - <module> (app.py:12) - Division error occurred
Traceback:
Traceback (most recent call last):
  File "app.py", line 12, in <module>
    1 / 0
ZeroDivisionError: division by zero

Suggestion: Check if the divisor is zero before performing division.
```

#### JSON Logging

```python
json_logger = ContextLogger(base_logger, json_mode=True)
json_logger.info("User API call", extra={"endpoint": "/users", "method": "GET"})
```

📌 Example JSON output:

```json
{
  "timestamp": "2025-08-26 19:45:12",
  "level": "INFO",
  "message": "User API call",
  "context": "<module> (app.py:20)",
  "extra": {"endpoint": "/users", "method": "GET"}
}
```

---

## ⏱️ Profiling Functions

```python
@logger.timeit
def process_data(n):
    total = 0
    for i in range(n):
        total += helper(i)
    return total

def helper(x):
    return x * x

result = process_data(1000)
print("Result:", result)
```

📌 Example output:

```
2025-08-26 19:45:12 - INFO - process_data (app.py:10) - Function process_data executed in 0.003200 seconds
2025-08-26 19:45:12 - DEBUG - process_data (app.py:10) -    └── helper (app.py:16) took 0.001500 seconds
```

---

## 🔧 Advanced Usage

### Adding Metadata

```python
logger.info("User logged in", extra={"user_id": 42, "role": "admin"})
```

### Manual Suggestions

```python
logger.error("File not found", suggestion="Verify the file path before accessing.")
```

---

## 📊 Use Cases

* Debugging slow functions with **nested profiling**.
* Capturing and understanding **errors faster** with AI suggestions.
* Structured JSON logs for **microservices & observability tools**.
* Automatic caller context for **simpler debugging**.

---

## 📜 License

MIT License – Free to use and modify.

---

## 👨‍💻 Author

Crafted by an **Ramakrishna Bapathu** to improve **debugging, observability, and developer productivity**.
