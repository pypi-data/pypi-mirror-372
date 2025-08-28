"""
SQL Splitter - Advanced MySQL SQL Parser for Visualization Components

🎯 Features:
- Field type classification (column, aggregation, expression, computed)
- Aggregation scope tracking for visualization
- Advanced JOIN detection and normalization
- Context-aware table and alias extraction
- Enhanced metadata for SQL visualization components

🚀 Quick Start:
    from sql_splitter import SQLParserAST
    
    parser = SQLParserAST()
    result = parser.parse("SELECT users.name, COUNT(*) FROM users GROUP BY users.name")
    print(result)

📊 Enhanced JSON Output:
    {
        "success": true,
        "fields": [
            {
                "table": "users",
                "field": "users.name",
                "fieldType": "column",
                "involvedTables": ["users"]
            },
            {
                "table": null,
                "field": "COUNT(*)",
                "fieldType": "aggregation",
                "aggregationScope": ["users"]
            }
        ],
        "metadata": {
            "aliasMapping": {},
            "aggregationFields": ["COUNT(*)"]
        }
    }
"""

from .core.sql_parser_ast_v6_0 import SQLParserAST, parse_sql, parse_sql_to_json
from .core.sql_normalizer_mysql import MySQLCompatibleNormalizer, normalize_sql_query

__version__ = "6.0.0"
__author__ = "SQL Splitter Team"
__description__ = "Advanced MySQL SQL Parser with Visualization Component Support"

# Main exports
__all__ = [
    'SQLParserAST',
    'parse_sql',
    'parse_sql_to_json',
    'MySQLCompatibleNormalizer',
    'normalize_sql_query'
]
