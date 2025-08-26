# Python Business Rule Validator (pybrv)

A robust Python package for validating business rules against databases.

## Installation

```bash
pip install pybrv
```

## Configuration

1. Create a `.env` file in your project directory:
   - Fill in your database credentials

2. Or configure programmatically:
```python
from pybrv import RuleManager
from pybrv.utils import DbConnections

# Configure database connection
db_config = {
    "host": "your_host",
    "database": "your_database",
    "user": "your_username",
    "password": "your_password",
    "port": 5432
}

# Initialize with configuration
db = DbConnections(credentials=db_config)
manager = RuleManager()

# Load and process rules
manager.load_config("rules.json")
result = manager.business_rule_check()
```

## Features

- Supports PostgreSQL and Databricks
- SQL template management
- Bookmarking capabilities
- Pass/fail validation with thresholds
- Detailed reporting
- Error handling and retries

## Development

To install in development mode:
```bash
git clone https://github.com/your-username/pybrv.git
cd pybrv
pip install -e .
```
