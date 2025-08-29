# mongo_logger.py
import json
import logging
import os
import sys
from datetime import datetime, timezone
from logging.handlers import QueueHandler, QueueListener
from queue import Queue

from dotenv import load_dotenv

load_dotenv()

try:
    from bson import ObjectId
    from pymongo import MongoClient
except ImportError:
    MongoClient = None


class MongoDBHandler(logging.Handler):
    """
    MongoDB logging handler with connection retry logic.
    Sends log records to MongoDB with format:
    {
        "_id": ObjectId(),
        "from": <LOG_FROM>,
        "timestamp": <UTC now>,
        "details": "<stringified message>"
    }
    """

    def __init__(self, uri: str, db: str, collection: str, from_value: str):
        super().__init__()
        if MongoClient is None:
            raise RuntimeError("pymongo not available - install with: pip install pymongo")
        
        self.uri = uri
        self.db_name = db
        self.collection_name = collection
        self.from_value = from_value
        self.client = None
        self.collection = None
        self._connect()

    def _connect(self):
        """Establish MongoDB connection"""
        try:
            self.client = MongoClient(self.uri, connect=False, serverSelectionTimeoutMS=5000)
            self.collection = self.client[self.db_name][self.collection_name]
            # Test connection
            self.client.admin.command('ping')
        except Exception as e:
            sys.stderr.write(f"[mongo_logger] Connection failed: {e}\n")
            self.client = None
            self.collection = None

    def _reconnect(self):
        """Attempt to reconnect to MongoDB"""
        if self.client:
            try:
                self.client.close()
            except:
                pass
        self._connect()

    def _prepare_message(self, record: logging.LogRecord):
        """Intelligently prepare message data preserving structure"""
        # Handle formatted messages like logging.info("hello %s", "world")
        if record.args:
            return record.getMessage()  # Returns formatted string

        msg = record.msg
        
        # Preserve structured data types as-is for MongoDB
        if isinstance(msg, (dict, list)):
            return msg
        
        # Convert other containers to lists for MongoDB
        if isinstance(msg, (tuple, set)):
            return list(msg)
        
        # Everything else becomes a string with error handling
        try:
            return str(msg)
        except Exception:
            return ""

    def emit(self, record: logging.LogRecord):
        """Emit log record to MongoDB with retry logic"""
        if self.collection is None:
            return

        try:
            self._insert_log(record)
        except Exception as e:
            sys.stderr.write(f"[mongo_logger] Insert failed: {e}, retrying...\n")
            # Try to reconnect and retry once
            self._reconnect()
            if self.collection is not None:
                try:
                    self._insert_log(record)
                except Exception as e2:
                    sys.stderr.write(f"[mongo_logger] Retry failed: {e2}\n")

    def _insert_log(self, record: logging.LogRecord):
        """Insert comprehensive log record into MongoDB"""
        doc = {
            "_id": ObjectId(),
            "from": self.from_value,
            "timestamp": datetime.now(timezone.utc),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module if hasattr(record, 'module') else record.pathname.split('/')[-1] if record.pathname else 'unknown',
            "line_number": record.lineno,
            "function": record.funcName,
            "message": self._prepare_message(record),
        }
        
        # Add original args if they exist (for formatted messages)
        if record.args:
            doc["formatted_args"] = list(record.args) if isinstance(record.args, (tuple, list)) else [record.args]
                
        self.collection.insert_one(doc)


def setup_mongodb_logging():
    """
    Set up MongoDB logging using environment variables:
    - MONGODB_URI: MongoDB connection string
    - LOG_FROM: Identifier for log source
    - LOG_LEVEL: Logging level (optional, defaults to INFO)
    - LOG_COLLECTION: Collection name (optional, defaults to LOG_FROM value)
    """
    if MongoClient is None:
        sys.stderr.write("[mongo_logger] pymongo not installed, MongoDB logging disabled\n")
        return False

    uri = os.getenv("MONGODB_URI")
    log_from = os.getenv("LOG_FROM")
    
    if not uri or not log_from:
        sys.stderr.write("[mongo_logger] MONGODB_URI or LOG_FROM not set, MongoDB logging disabled\n")
        return False

    # Configuration
    db_name = "logs"
    collection_name = os.getenv("LOG_COLLECTION") or log_from
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    try:
        # Set up root logger level
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level, logging.INFO))

        # Create MongoDB handler with queue for thread safety
        queue = Queue(-1)
        mongo_handler = MongoDBHandler(uri, db_name, collection_name, log_from)
        
        # Use QueueListener for thread-safe logging
        listener = QueueListener(queue, mongo_handler, respect_handler_level=True)
        listener.daemon = True
        listener.start()
        
        # Add console handler for stdout output
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        # Add queue handler to root logger
        queue_handler = QueueHandler(queue)
        root_logger.addHandler(queue_handler)

        print(f"[mongo_logger] MongoDB logging enabled: {db_name}.{collection_name}")
        return True

    except Exception as e:
        sys.stderr.write(f"[mongo_logger] Setup failed: {e}\n")
        return False