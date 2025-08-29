# MongoDB Logger

[![PyPI version](https://badge.fury.io/py/mongodb-logger.svg)](https://badge.fury.io/py/mongodb-logger)
[![Python Support](https://img.shields.io/pypi/pyversions/mongodb-logger.svg)](https://pypi.org/project/mongodb-logger/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Intelligent MongoDB logging handler for Python with structured data support**

MongoDB Logger is a Python library that provides seamless integration between Python's standard logging module and MongoDB. It preserves structured data (dictionaries, lists, etc.) in their native format while adding comprehensive metadata for better log analysis.

## ✨ Features

### 🎯 **Intelligent Data Handling**
- **Structured Data Preservation**: Dictionaries and lists stored as native MongoDB objects
- **Type-Aware Processing**: Automatic handling of strings, numbers, booleans, and complex types
- **Container Conversion**: Smart conversion of tuples and sets to arrays

### 🔧 **Rich Metadata**
Every log entry automatically includes:
- **Source Information**: Module, function, line number
- **Temporal Data**: UTC timestamp with timezone awareness
- **Log Context**: Logger name, level, formatted arguments
- **Custom Identifiers**: Application/service identification via `LOG_FROM`

### 🚀 **Production Ready**
- **Thread-Safe**: Queue-based processing for high-concurrency applications
- **Auto-Reconnection**: Robust connection handling with retry logic
- **Dual Output**: Simultaneous console and MongoDB logging
- **Environment-Based Config**: Simple setup via environment variables

## 📦 Installation

### From PyPI (Recommended)
```bash
pip install mongodb-logger
```

### From Source
```bash
git clone https://github.com/your-username/mongodb-logger.git
cd mongodb-logger
pip install -e .
```

### Development Installation
```bash
git clone https://github.com/your-username/mongodb-logger.git
cd mongodb-logger
pip install -e ".[dev]"
```

## 🚀 Quick Start

### 1. Environment Setup
Create a `.env` file in your project root:

```env
MONGODB_URI="mongodb://user:password@host:port/database"
LOG_FROM="your_app_name"
```

**Example:**
```env
MONGODB_URI="mongodb://username:password@localhost:27017/mydatabase"
LOG_FROM="my_application"
```

### 2. Basic Usage

```python
import logging
from mongodb_logger import setup_mongodb_logging

# Initialize MongoDB logging (call once at application startup)
setup_mongodb_logging()

# Use standard Python logging
logging.info("Application started successfully")

# Log structured data (preserved as MongoDB objects)
logging.info({
    "event": "user_login",
    "user_id": 12345,
    "metadata": {
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0...",
        "session_id": "abc123"
    }
})

# Log arrays and lists
logging.info(["task_completed", "task_started", "task_pending"])

# Different log levels work seamlessly
logging.warning({
    "alert_type": "disk_space_low",
    "usage_percent": 85,
    "server": "web-01"
})

logging.error({
    "error_type": "database_timeout",
    "operation": "user_fetch",
    "timeout_ms": 5000,
    "retry_count": 3
})
```

### 3. Framework Integration

#### Flask
```python
from flask import Flask, request
import logging
from mongodb_logger import setup_mongodb_logging

app = Flask(__name__)

# Setup logging once at startup
setup_mongodb_logging()

@app.route('/')
def home():
    logging.info({
        "event": "page_view",
        "endpoint": "/",
        "method": request.method,
        "user_agent": request.headers.get('User-Agent'),
        "remote_addr": request.remote_addr
    })
    return "Hello World"

if __name__ == '__main__':
    app.run()
```

#### FastAPI
```python
from fastapi import FastAPI, Request
import logging
from mongodb_logger import setup_mongodb_logging

# Setup logging at startup
setup_mongodb_logging()

app = FastAPI()

@app.get("/")
async def read_root(request: Request):
    logging.info({
        "event": "api_request",
        "endpoint": "/",
        "method": request.method,
        "client": request.client.host if request.client else None
    })
    return {"message": "Hello World"}
```

#### Django
```python
# In settings.py or apps.py
import logging
from mongodb_logger import setup_mongodb_logging

# Setup once during Django startup
setup_mongodb_logging()

# Use anywhere in your Django application
def my_view(request):
    logging.info({
        "event": "view_accessed",
        "view": "my_view",
        "user": str(request.user),
        "method": request.method,
        "path": request.path
    })
    return HttpResponse("Success")
```

## 📊 MongoDB Document Structure

Every log entry in MongoDB follows this structure:

```javascript
{
    "_id": ObjectId("..."),
    "from": "your_app_name",           // From LOG_FROM environment variable
    "timestamp": ISODate("..."),       // UTC timestamp
    "level": "INFO",                   // Log level
    "logger": "root",                  // Logger name
    "module": "app.py",               // Source module
    "line_number": 42,                // Source line number
    "function": "my_function",        // Source function name
    "message": {                      // Your actual log data
        "event": "user_login",
        "user_id": 123,
        "success": true
    },
    "formatted_args": ["arg1", "arg2"] // Present only for formatted string logs
}
```

## 🔧 Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MONGODB_URI` | ✅ | - | MongoDB connection string |
| `LOG_FROM` | ✅ | - | Application identifier (used as collection name) |
| `LOG_LEVEL` | ❌ | `INFO` | Minimum log level |
| `LOG_COLLECTION` | ❌ | `LOG_FROM` value | Custom collection name |

### Advanced Configuration

For custom configuration, you can use the `MongoDBHandler` directly:

```python
import logging
from mongodb_logger import MongoDBHandler

# Custom handler setup
handler = MongoDBHandler(
    uri="mongodb://localhost:27017",
    db="custom_logs",
    collection="app_logs",
    from_value="my_service"
)

logger = logging.getLogger("my_logger")
logger.addHandler(handler)
logger.setLevel(logging.INFO)

logger.info({"custom": "configuration", "working": True})
```

## 📋 Supported Data Types

MongoDB Logger intelligently handles various Python data types:

```python
# Strings (preserved as strings)
logging.info("Simple text message")

# Formatted strings (args preserved separately)
logging.info("User %s logged in at %s", username, timestamp)

# Dictionaries (preserved as MongoDB objects)
logging.info({
    "event": "api_call",
    "endpoint": "/users",
    "response_time": 45.2,
    "success": True
})

# Lists (preserved as MongoDB arrays)
logging.info(["item1", "item2", "item3"])

# Tuples (converted to arrays)
logging.info(("x", 10.5, "y", 20.3))

# Sets (converted to arrays)
logging.info({"python", "mongodb", "logging"})

# Mixed types
logging.info({
    "metrics": [1, 2, 3],
    "metadata": {"version": "1.0"},
    "active": True,
    "count": 42
})
```

## 🧪 Testing

Run the included test suite:

```bash
# Run basic tests
python tests/test_logging.py

# With pytest (for development)
pytest tests/ -v

# With coverage
pytest tests/ --cov=mongodb_logger --cov-report=html
```

## 🔍 Troubleshooting

### Common Issues

**1. "pymongo not available"**
```bash
pip install pymongo>=4.0.0
```

**2. "MongoDB connection failed"**
- Verify `MONGODB_URI` format
- Check network connectivity to MongoDB server
- Confirm authentication credentials
- Test connection manually:

```python
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
print("Connected:", client.admin.command('ping'))
```

**3. "Logs not appearing in MongoDB"**
- Ensure proper flush time for queue processing
- Add small delay before application exit:

```python
import time
# ... your logging code ...
time.sleep(2)  # Allow queue to flush
```

**4. "Import errors after installation"**
- Verify installation: `pip list | grep mongodb-logger`
- Check Python path and virtual environment
- Try reimporting: `python -c "import mongodb_logger; print('OK')"`

### Performance Considerations

- **Queue Processing**: Uses async queues to prevent blocking
- **Connection Pooling**: Maintains persistent MongoDB connections
- **Batch Processing**: Consider batching for high-volume applications
- **Resource Monitoring**: Monitor MongoDB collection size and implement rotation if needed

## 🛡️ Security Best Practices

- **Never log sensitive data** (passwords, API keys, personal information)
- **Use authentication** in MongoDB connection strings
- **Network security**: Ensure secure connections (TLS/SSL)
- **Access control**: Implement proper MongoDB user permissions
- **Environment variables**: Keep credentials in `.env` files (not in code)

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
git clone https://github.com/miroblog/mongodb-logger.git
cd mongodb-logger
pip install -e ".[dev]"
pre-commit install
```

### Running Tests

```bash
pytest tests/ -v
black src/ tests/
isort src/ tests/
flake8 src/ tests/
mypy src/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/miroblog/mongodb-logger/issues)
- **Documentation**: [GitHub README](https://github.com/miroblog/mongodb-logger#readme)
- **PyPI**: [mongodb-logger](https://pypi.org/project/mongodb-logger/)

## 🎯 Roadmap

- [ ] Batch processing for high-volume applications
- [ ] MongoDB TTL (Time To Live) index support
- [ ] Custom field transformation and filtering
- [ ] Structured query interface for log analysis
- [ ] Integration with popular observability platforms
- [ ] Performance monitoring and metrics

---

**MongoDB Logger** - Making structured logging simple and powerful! 🚀