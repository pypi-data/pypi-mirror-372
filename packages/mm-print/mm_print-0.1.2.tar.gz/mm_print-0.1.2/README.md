# mm-print

Enhanced printing library with rich formatting support.

## Overview

`mm-print` provides a set of enhanced printing functions with beautiful formatting and table display. JSON serialization is handled by the `mm-std` library for extended type support.

## Quick Start

```python
import mm_print

# Pretty print JSON
data = {"name": "John", "age": 30, "active": True}
mm_print.json(data)

# Create beautiful tables
mm_print.table(
    title="Users",
    columns=["Name", "Age", "City"],
    rows=[
        ["Alice", 25, "New York"],
        ["Bob", 30, "London"],
    ]
)

# Syntax highlighted TOML
config = {
    "database": {
        "host": "localhost",
        "port": 5432
    }
}
mm_print.toml(data=config)
```

## API Reference

### `mm_print.plain(*messages)`

Print messages to stdout without any formatting.

```python
import mm_print

mm_print.plain("Hello, world!")
mm_print.plain(42)
```

### `mm_print.json(data, type_handlers=None)`

Print objects as beautifully formatted JSON with syntax highlighting.

```python
import mm_print

# Basic usage
mm_print.json({"key": "value", "number": 42})

# With custom type handlers
class CustomObject:
    def __init__(self, value):
        self.value = value

def serialize_custom(obj):
    return {"custom_value": obj.value}

data = {"obj": CustomObject("test")}
mm_print.json(data, type_handlers={CustomObject: serialize_custom})
```

### `mm_print.table(title, columns, rows)`

Create and print formatted tables with rich styling.

```python
import mm_print

mm_print.table(
    title="Sales Report",
    columns=["Product", "Quantity", "Revenue"],
    rows=[
        ["Widget A", 150, "$1,500.00"],
        ["Widget B", 89, "$890.00"],
        ["Widget C", 200, "$2,000.00"],
    ]
)
```

### `mm_print.toml(*, toml=None, data=None, line_numbers=False, theme="monokai")`

Print TOML with syntax highlighting. Either `toml` string or `data` object must be provided.

```python
import mm_print

# From TOML string
toml_content = """
[server]
host = "0.0.0.0"
port = 8080

[database]
url = "postgresql://localhost/mydb"
max_connections = 20
"""
mm_print.toml(toml=toml_content)

# From Python object
config = {
    "server": {"host": "0.0.0.0", "port": 8080},
    "database": {"url": "postgresql://localhost/mydb", "max_connections": 20}
}
mm_print.toml(data=config)

# With line numbers and custom theme
mm_print.toml(toml=toml_content, line_numbers=True, theme="github")
```

### `mm_print.fatal(message, code=1)`

Print error message to stderr and exit with specified code.

```python
import mm_print

# Exit with code 1
mm_print.fatal("Configuration file not found!")

# Exit with custom code
mm_print.fatal("Database connection failed", code=2)
```

## Examples

### Configuration Display
```python
import mm_print

# Display config as JSON
config = {
    "app_name": "MyApp",
    "version": "1.0.0",
    "features": ["auth", "api", "web"]
}
mm_print.json(config)

# Show database connections as table
connections = [
    ["Primary", "postgresql://localhost:5432/main", "active"],
    ["Cache", "redis://localhost:6379/0", "active"],
    ["Analytics", "clickhouse://localhost:8123/stats", "inactive"],
]
mm_print.table("Database Connections", ["Name", "URL", "Status"], connections)
```

### Error Handling
```python
import mm_print

try:
    result = risky_operation()
    mm_print.json({"status": "success", "result": result})
except FileNotFoundError:
    mm_print.fatal("Required configuration file not found")
except Exception as e:
    mm_print.json({"status": "error", "error": str(e)})
    mm_print.fatal("Operation failed", code=1)
```
