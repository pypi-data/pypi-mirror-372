# test_logging.py - Various logging test cases
import logging
import time
import sys
import os

# Add src directory to path for importing our package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mongodb_logger import setup_mongodb_logging

# Set up MongoDB logging
setup_mongodb_logging()

# ensure INFO flows even if LOG_LEVEL isn't set
logging.getLogger().setLevel(logging.INFO)

print("Testing various logging cases...")

# Case 1: Simple string message
logging.info("Simple plain text message")

# Case 2: Formatted string with multiple args
logging.info("Formatted: %s user logged in at %s with ID %d", "john_doe", "2024-08-28", 12345)

# Case 3: Dictionary object (should preserve structure in MongoDB)
logging.info({
    "event": "user_login", 
    "user_id": 456, 
    "success": True,
    "ip_address": "192.168.1.100"
})

# Case 4: Complex nested dictionary
logging.info({
    "event": "api_request",
    "endpoint": "/api/v1/users",
    "method": "POST",
    "payload": {
        "name": "Alice Smith",
        "email": "alice@example.com",
        "preferences": {
            "theme": "dark",
            "notifications": True,
            "languages": ["en", "es"]
        }
    },
    "response": {
        "status": 201,
        "user_id": 789,
        "created_at": "2024-08-28T10:30:00Z"
    }
})

# Case 5: Array/List
logging.info(["task1", "task2", "task3", {"urgent": True}])

# Case 6: Simple array
logging.info([1, 2, 3, 4, 5])

# Case 7: Tuple (should convert to list)
logging.info(("coordinate_x", 10.5, "coordinate_y", 20.3))

# Case 8: Set (should convert to list)  
logging.info({"python", "javascript", "go", "rust"})

# Case 9: Mixed formatting with object
logging.info("Processing order %s with details: %s", "ORD-001", {"items": 3, "total": 99.99})

# Case 10: Different log levels with structured data
logging.warning({
    "alert_type": "disk_space_low",
    "percentage_used": 85,
    "server": "web-01",
    "threshold": 80
})

logging.error({
    "error_type": "database_connection_timeout",
    "database": "user_db",
    "timeout_seconds": 30,
    "retry_attempts": 3,
    "last_error": "Connection timeout"
})

# Case 11: Exception with context
try:
    result = 10 / 0
except ZeroDivisionError:
    logging.error("Mathematical error occurred in calculation module")

# Case 12: Empty structures
logging.info({})
logging.info([])

# Case 13: Boolean and numeric values
logging.info({
    "feature_enabled": True,
    "user_count": 1500,
    "success_rate": 99.7,
    "last_updated": None
})

print("All test cases completed. Check your MongoDB collection 'logs.test' for:")
print("- Simple strings as strings")  
print("- Dictionaries preserved as structured objects")
print("- Arrays preserved as arrays")
print("- Tuples/sets converted to arrays")
print("- All metadata: level, logger, module, line_number, function")
print("- Formatted args captured separately when used")

# Give time for all logs to be processed by QueueListener
time.sleep(3)
