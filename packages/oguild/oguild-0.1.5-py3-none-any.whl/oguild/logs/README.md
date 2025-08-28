# Python Logger Package

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

Enhanced logging utilities for Python applications with automatic formatting, UUID handling, and multi-output support.

## 🚀 Features

### Enhanced Logging System

- **Smart Logger**: Advanced logging with automatic JSON formatting and UUID handling
- **Multi-Output Support**: Console, file, and Logstash integration
- **Automatic Module Detection**: Automatically detects and uses the calling module's name
- **Pretty Formatting**: Intelligent message formatting for complex data structures
- **Environment-Based Configuration**: Configurable log levels via environment variables

### Key Capabilities

- **UUID Sanitization**: Automatically converts UUID objects to readable strings
- **JSON Structure Detection**: Identifies and pretty-prints JSON-like structures in log messages
- **Flexible Output**: Support for console, file, and asynchronous Logstash logging
- **Production Ready**: Built-in error handling and graceful degradation

## 📦 Installation

### Prerequisites

- Python 3.9 or higher
- Poetry (recommended) or pip

### Using Poetry (Recommended)

```bash
poetry add oguild
```

### Using pip

```bash
pip install oguild
```

### Optional Dependencies

For Logstash support, install with the `logstash` extra:

```bash
poetry add oguild --extras "logstash"
# or
pip install "oguild[logstash]"
```

## 🎯 Quick Start

### Basic Usage

```python
from oguild.logs import logger

# Simple logging
logger.info("Hello, World!")
logger.debug("Debug information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical failure")

# The logger automatically detects the module name
# Output: INFO: (your_module_name) == Hello, World! [timestamp]
```

### Advanced Logging with Formatting

```python
from oguild.logs import logger
import uuid

# Complex data structures are automatically formatted
data = {
    "user_id": uuid.uuid4(),
    "nested": {
        "list": [1, 2, 3],
        "dict": {"key": "value"}
    }
}

# Use format=True for pretty printing
logger.info(data, format=True)
```

### Custom Logger Configuration

```python
from oguild.logs import Logger

# Create a custom logger with file output
custom_logger = Logger(
    logger_name="my_app",
    log_file="/path/to/app.log",
    log_level="DEBUG"
).get_logger()

custom_logger.info("This goes to both console and file")
```

### Logstash Integration

```python
from oguild.logs import Logger

# Configure Logstash logging
logstash_logger = Logger(
    logger_name="production_app",
    logstash_host="logstash.example.com",
    logstash_port=5959,
    logstash_database_path="/tmp/logstash.db"
).get_logger()

logstash_logger.info("This will be sent to Logstash")
```

## 🔧 Configuration

### Environment Variables

- `LOG_LEVEL`: Set the default log level (default: INFO)
  - Options: DEBUG, INFO, WARNING, ERROR, CRITICAL

### Logger Parameters

- `logger_name`: Custom logger name (auto-detected if not provided)
- `log_file`: Path to log file for file-based logging
- `log_level`: Logging level (int or string)
- `log_format`: Custom log message format
- `logstash_host`: Logstash server hostname
- `logstash_port`: Logstash server port (default: 5959)
- `logstash_database_path`: Path for Logstash database

### Log Format

Default format: `%(levelname)s: (%(name)s) == %(message)s [%(asctime)s]`

## 📚 API Reference

### SmartLogger Class

Extends Python's standard `logging.Logger` with enhanced formatting capabilities.

#### Methods

- `info(msg, *args, format=False, **kwargs)`: Log info message
- `debug(msg, *args, format=False, **kwargs)`: Log debug message
- `warning(msg, *args, format=False, **kwargs)`: Log warning message
- `error(msg, *args, format=False, **kwargs)`: Log error message
- `critical(msg, *args, format=False, **kwargs)`: Log critical message

#### Parameters

- `msg`: Message to log (string, dict, list, or any object)
- `format`: If True, applies pretty formatting to the message
- `*args, **kwargs`: Standard logging parameters

### Logger Class

Main logger factory class for creating configured loggers.

#### Constructor

```python
Logger(
    logger_name=None,
    log_file=None,
    log_level=None,
    log_format=None,
    logstash_host=None,
    logstash_port=5959,
    logstash_database_path=None
)
```

#### Methods

- `get_logger()`: Returns the configured logger instance

## 🔍 Examples

### Web Application Logging

```python
from oguild.logs import Logger
from flask import Flask, request

app = Flask(__name__)
logger = Logger(logger_name="web_app").get_logger()

@app.route('/api/users', methods=['POST'])
def create_user():
    user_data = request.get_json()
    logger.info(f"Creating user: {user_data}", format=True)

    try:
        # User creation logic
        user_id = create_user_in_db(user_data)
        logger.info(f"User created successfully with ID: {user_id}")
        return {"user_id": user_id}, 201
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        return {"error": "User creation failed"}, 500
```

### Background Task Logging

```python
from oguild.logs import Logger
import uuid

class TaskProcessor:
    def __init__(self):
        self.logger = Logger(
            logger_name="task_processor",
            log_file="/var/log/tasks.log"
        ).get_logger()

    def process_task(self, task_data):
        task_id = uuid.uuid4()
        self.logger.info(f"Starting task {task_id}: {task_data}", format=True)

        try:
            # Process task logic
            result = self._execute_task(task_data)
            self.logger.info(f"Task {task_id} completed successfully: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Task {task_id} failed: {e}")
            raise
```

### Production Logging with Logstash

```python
from oguild.logs import Logger
import os

# Production logger configuration
prod_logger = Logger(
    logger_name="production_service",
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    logstash_host=os.getenv("LOGSTASH_HOST"),
    logstash_port=int(os.getenv("LOGSTASH_PORT", "5959")),
    logstash_database_path="/tmp/logstash.db"
).get_logger()

# Structured logging for production
prod_logger.info({
    "event": "user_login",
    "user_id": "12345",
    "timestamp": "2024-01-01T00:00:00Z",
    "ip_address": "192.168.1.1"
}, format=True)
```

## 🚨 Troubleshooting

### Common Issues

#### Logstash Connection Failed

```
Failed to initialize Logstash handler: [Errno 111] Connection refused
```

**Solution**: Check if Logstash is running and accessible on the specified host/port.

#### Permission Denied for Log File

```
PermissionError: [Errno 13] Permission denied: '/var/log/app.log'
```

**Solution**: Ensure the application has write permissions to the log directory.

#### UUID Objects Not Formatting

If UUID objects appear as `UUID('...')` in logs:

- Use `format=True` parameter for pretty formatting
- Ensure the message is passed as a dict/list, not a string

## 🔗 Related Documentation

- [Main OpsGuild Pack README](../README.md)
- [Python Package Configuration](../../pyproject.toml)
- [Test Suite](../../../test/)

---

**Part of the OpsGuild Utilities Pack**
