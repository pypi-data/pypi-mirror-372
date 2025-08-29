"""
MongoDB Logger - Intelligent structured logging for MongoDB

A Python logging handler that sends logs to MongoDB with support for:
- Structured data preservation (dicts, lists, etc.)
- Rich metadata (timestamps, source info, etc.)
- Thread-safe operation with queue-based processing
- Automatic reconnection and error handling

Usage:
    >>> from mongodb_logger import setup_mongodb_logging
    >>> setup_mongodb_logging()
    >>> import logging
    >>> logging.info({"event": "user_login", "user_id": 123})
"""

from .handler import MongoDBHandler, setup_mongodb_logging

__version__ = "0.1.0"
__author__ = "MongoDB Logger Team"
__email__ = "support@example.com"

__all__ = [
    "MongoDBHandler",
    "setup_mongodb_logging",
    "__version__",
]