# SQL Splitter 🎯

Advanced MySQL SQL Parser with Visualization Component Support

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-6.0.0-orange.svg)](https://github.com/alexkwok22/sql-splitter)

## 🚀 Features

- **🎨 Field Type Classification**: Automatically categorizes fields as `column`, `aggregation`, `expression`, or `computed`
- **🔗 Aggregation Scope Tracking**: Tracks which tables are involved in aggregation functions like `COUNT(*)`
- **📊 Visualization-Ready Output**: Enhanced JSON format perfect for SQL diagram generation
- **🛠️ Advanced JOIN Detection**: Handles complex nested JOINs and old-style comma-separated syntax
- **🏷️ Smart Alias Resolution**: Context-aware alias mapping and resolution
- **🐬 MySQL Compatibility**: Full MySQL syntax support with normalization
- **📋 Comprehensive Metadata**: Provides detailed parsing information for debugging and visualization

## 📦 Installation

```bash
pip install sql-splitter
```

Or install from source:

```bash
git clone https://github.com/alexkwok22/sql-splitter.git
cd sql-splitter
pip install -e .
```

## 🎯 Quick Start

### Basic Usage

```python
from sql_splitter import SQLParserAST

# Initialize parser
parser = SQLParserAST()

# Parse SQL query
sql = """
SELECT 
    users.name,
    COUNT(*) as total_orders,
    SUM(orders.amount) as total_revenue
FROM users 
JOIN orders ON users.id = orders.user_id 
WHERE users.status = 'active'
GROUP BY users.name
"""

result = parser.parse(sql)
print(result)
```

### Enhanced JSON Output

```json
{
  "success": true,
  "fields": [
    {
      "table": "users",
      "field": "users.name",
      "alias": "name",
      "fieldType": "column",
      "involvedTables": ["users"]
    },
    {
      "table": null,
      "field": "COUNT(*)",
      "alias": "total_orders",
      "fieldType": "aggregation",
      "aggregationScope": ["users", "orders"],
      "involvedTables": ["users", "orders"]
    },
    {
      "table": "orders",
      "field": "SUM(orders.amount)",
      "alias": "total_revenue", 
      "fieldType": "aggregation",
      "involvedTables": ["orders"]
    }
  ],
  "tables": ["users", "orders"],
  "joins": [
    {
      "type": "JOIN",
      "leftTable": "users",
      "leftField": "id",
      "rightTable": "orders", 
      "rightField": "user_id",
      "condition": "users.id = orders.user_id"
    }
  ],
  "whereConditions": ["users.status = 'active'"],
  "parser": "sqlsplit",
  "metadata": {
    "aliasMapping": {},
    "aggregationFields": ["total_orders", "total_revenue"],
    "computedFields": [],
    "unresolved": {
      "aliases": [],
      "fields": []
    }
  }
}
```

## 🎨 Visualization Components Support

### Field Type Classification

SQL Splitter automatically classifies fields into four types:

- **`column`**: Simple table columns (`users.name`)
- **`aggregation`**: Aggregate functions (`COUNT(*)`, `SUM(amount)`)
- **`expression`**: Complex expressions (`DATE_FORMAT(created_at, '%Y-%m')`)
- **`computed`**: Conditional logic (`CASE WHEN status = 1 THEN 'active' END`)

### Aggregation Scope Tracking

For visualization components, aggregation functions include `aggregationScope` to show which tables are involved:

```python
# COUNT(*) shows all tables in the query
{
  "field": "COUNT(*)",
  "fieldType": "aggregation",
  "aggregationScope": ["users", "orders", "products"]  # All related tables
}

# Specific aggregations show only relevant tables
{
  "field": "SUM(orders.amount)",
  "fieldType": "aggregation", 
  "aggregationScope": ["orders"]  # Only orders table
}
```

## 🛠️ Advanced Features

### MySQL Normalization

```python
from sql_splitter import MySQLCompatibleNormalizer

normalizer = MySQLCompatibleNormalizer()
normalized_sql, rules, errors = normalizer.normalize_query(sql)
```

### Old-Style JOIN Conversion

Automatically converts old-style comma-separated JOINs:

```sql
-- Input: Old-style
SELECT * FROM users a, orders b WHERE a.id = b.user_id

-- Output: Modern JOIN
SELECT * FROM users a JOIN orders b ON a.id = b.user_id
```

### Context-Aware Alias Resolution

Handles complex alias scenarios:

```python
# Resolves aliases like 'u' -> 'users', 'o' -> 'orders'
"metadata": {
  "aliasMapping": {
    "u": "users",
    "o": "orders"
  }
}
```

## 📚 Documentation

- **[Quick Start Guide](docs/Quick-Start-Guide.md)** - Get started in 5 minutes
- **[API Documentation](docs/SQL-Parser-Usage-Guide.md)** - Complete API reference
- **[Expected Format](docs/expect.md)** - JSON output specification
- **[Examples](examples/)** - Real-world usage examples

## 🧪 Testing

```bash
# Run basic tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=sql_splitter --cov-report=html
```

## 📋 Requirements

- Python 3.7+
- No external dependencies (pure Python implementation)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for SQL visualization component developers
- Supports complex MySQL queries and edge cases
- Designed with performance and accuracy in mind

---

**Made with ❤️ for the SQL visualization community**
