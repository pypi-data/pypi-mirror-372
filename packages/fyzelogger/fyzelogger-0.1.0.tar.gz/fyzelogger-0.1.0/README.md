# FyzeLogger

A colorful, timestamped logger for Python.  
Supports Success, Error, Debug, Warning, Ratelimit messages with colored dots.

## Installation

```bash
pip install fyzelogger
```

## Usage

```python
from fyzelogger import FyzeLogger

log = FyzeLogger("FyZe-Test")
log.success("Operation successful!")
log.error("Something went wrong!")
log.debug("Debug information")
log.warn("Warning message")
log.ratelimit("Ratelimit message")
user_input = log.input("Enter your email: ")
log.log(f"You entered: {user_input}")
```
