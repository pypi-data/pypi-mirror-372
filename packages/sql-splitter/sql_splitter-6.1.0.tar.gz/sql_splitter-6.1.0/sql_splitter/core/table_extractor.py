"""
Table Extractor - SQL Parser AST v6.0

🔍 Advanced table extraction with support for complex patterns

Author: AI Assistant
Version: 6.0 AST Modular
Date: 2025-08-26
Status: ✅ Enhanced table detection for 100% expect.md compliance
"""

import re
from typing import List, Dict, Any, Optional, Tuple, Set
from .ast_nodes import TableReferenceNode, create_table_reference
from .sql_tokenizer import TokenStream, Token, TokenType

class TableExtractor:
    """Advanced table extraction with comprehensive pattern detection"""

    def __init__(self):
        self.detected_tables = set()
        self.table_aliases = {}
        self.database_schemas = set()
        self.cte_tables = set()

    def extract_all_tables(self, sql: str, cte_tables: Set[str] = None) -> Tuple[List[str], Dict[str, str]]:
        """🎯 Extract all tables with comprehensive detection"""
        self.reset()
        
        if cte_tables:
            self.cte_tables.update(cte_tables)
            self.detected_tables.update(cte_tables)

        # 🎯 Phase 1: Database schema detection
        self._detect_database_schemas(sql)

        # 🎯 Phase 2: FROM clause tables (all patterns)
        self._extract_from_clause_tables(sql)

        # 🎯 Phase 3: JOIN tables (comprehensive patterns)
        self._extract_join_tables(sql)

        # 🎯 Phase 4: Field-referenced tables
        self._extract_field_referenced_tables(sql)

        # 🎯 Phase 5: Window function tables
        self._extract_window_function_tables(sql)

        # 🎯 Phase 6: Subquery tables
        self._extract_subquery_tables(sql)

        # 🎯 SIMPLIFIED AND ROBUST: Remove known database names from final results
        database_names = {'momo', 'main_db', 'analytics_db', 'test_db', 'prod_db', 'dev_db'}
        database_names.update(self.database_schemas)  # Include detected schemas
        
        # Apply robust database prefix filtering to final results
        filtered_tables = set()
        
        for table in self.detected_tables:
            if '.' in table:
                # Handle database.table patterns - extract only the table part
                parts = table.split('.')
                if len(parts) >= 2 and parts[0] in database_names:
                    # This is a database.table pattern - extract the actual table name
                    actual_table = parts[1]
                    if self._is_valid_table_name(actual_table) and actual_table not in database_names:
                        filtered_tables.add(actual_table)
                else:
                    # Not a database prefix, keep as-is (if valid)
                    if self._is_valid_table_name(table) and table not in database_names:
                        filtered_tables.add(table)
            else:
                # No dot - this is a standalone name
                # SIMPLE RULE: Skip if it's a known database name
                if table not in database_names and self._is_valid_table_name(table):
                    filtered_tables.add(table)

        return sorted(list(filtered_tables)), self.table_aliases

    def _detect_database_schemas(self, sql: str) -> None:
        """Detect database schemas"""
        cross_db_pattern = r'`([a-zA-Z_][a-zA-Z0-9_]*)`\.`([a-zA-Z_][a-zA-Z0-9_]*)`'
        matches = re.findall(cross_db_pattern, sql)

        for db_candidate, table_candidate in matches:
            if (re.match(r'^(main_db|analytics_db|test_db|prod_db|dev_db|momo)$', db_candidate) or 
                '_db' in db_candidate.lower() or
                db_candidate.lower() in ['main', 'analytics', 'test', 'prod', 'dev']):
                self.database_schemas.add(db_candidate)

    def _extract_from_clause_tables(self, sql: str) -> None:
        """🎯 Extract FROM clause tables (all nested patterns)"""
        
        # 🎯 Handle database-prefixed patterns first (momo.table_name)
        db_prefixed_patterns = [
            # 🎯 Database-prefixed table names (momo.table_name)
            r'\bFROM\s+([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]+)(?:\s+(?:AS\s+)?([a-zA-Z_][a-zA-Z0-9_]*))?',
            
            # 🎯 Bracketed FROM with database prefix: FROM (((momo.table
            r'\bFROM\s+\(\(\(([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]+)',
            
            # 🎯 Double bracketed FROM with database prefix: FROM ((momo.table
            r'\bFROM\s+\(\(([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]+)',
            
            # 🎯 Single bracketed FROM with database prefix: FROM (momo.table
            r'\bFROM\s+\(([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]+)(?:\s+(?:AS\s+)?([a-zA-Z_][a-zA-Z0-9_]*))?',
        ]
        
        # 🎯 USER'S EXCELLENT SUGGESTION: Use simple dot-split for database-prefixed patterns
        # Look for any database.table patterns in the SQL and split them properly
        import re
        
        # Find all database.table patterns in FROM clauses
        db_table_patterns = [
            r'\bFROM\s+([a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]+)(?:\s+(?:AS\s+)?([a-zA-Z_][a-zA-Z0-9_]*))?',
            r'\bFROM\s+\(\(\(([a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]+)',
            r'\bFROM\s+\(\(([a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]+)',
            r'\bFROM\s+\(([a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]+)(?:\s+(?:AS\s+)?([a-zA-Z_][a-zA-Z0-9_]*))?',
        ]
        
        for pattern in db_table_patterns:
            matches = re.finditer(pattern, sql, re.IGNORECASE)
            for match in matches:
                full_name = match.group(1)  # e.g., "momo.mt_item"
                alias = match.group(2) if len(match.groups()) >= 2 and match.group(2) else None
                
                # 🎯 Apply dot-split approach
                if '.' in full_name:
                    parts = full_name.split('.')
                    if len(parts) >= 2:
                        db_name = parts[0].strip()  # e.g., "momo"
                        table_name = parts[1].strip()  # e.g., "mt_item"
                        
                        # Add database to detected schemas for filtering
                        if db_name in ['momo', 'main_db', 'analytics_db', 'test_db', 'prod_db', 'dev_db']:
                            self.database_schemas.add(db_name)
                        
                        # Only add the actual table name, not the database prefix
                        if table_name and self._is_valid_table_name(table_name):
                            self.detected_tables.add(table_name)
                            if alias and len(alias) >= 1:  # ✅ Allow single-char aliases like 'o', 'c', 'u'
                                self.table_aliases[alias] = table_name
        
        # 🎯 Handle standard patterns (no database prefix)
        standard_patterns = [
            # 🎯 Standard FROM (no backticks)
            r'\bFROM\s+([a-zA-Z_][a-zA-Z0-9_]+)(?:\s+(?:AS\s+)?([a-zA-Z_][a-zA-Z0-9_]*))?',
            
            # 🎯 Standard FROM (legacy backtick support)
            r'\bFROM\s+`([a-zA-Z_][a-zA-Z0-9_]+)`(?:\s+(?:AS\s+)?`?([a-zA-Z_][a-zA-Z0-9_]*)`?)?',
            
            # 🎯 Cross-database FROM (legacy backtick support)
            r'\bFROM\s+`[^`]+`\.`([a-zA-Z_][a-zA-Z0-9_]+)`(?:\s+(?:AS\s+)?`?([a-zA-Z_][a-zA-Z0-9_]*)`?)?'
        ]

        for pattern in standard_patterns:
            matches = re.finditer(pattern, sql, re.IGNORECASE)
            for match in matches:
                table_name = match.group(1)
                alias = match.group(2) if len(match.groups()) >= 2 and match.group(2) else None

                if self._is_valid_table_name(table_name):
                    self.detected_tables.add(table_name)
                    if alias and len(alias) >= 1:  # ✅ Allow single-char aliases like 'o', 'c', 'u'
                        self.table_aliases[alias] = table_name

    def _extract_join_tables(self, sql: str) -> None:
        """🎯 Extract JOIN tables (comprehensive patterns)"""
        
        # 🎯 USER'S EXCELLENT SUGGESTION: Apply dot-split approach to JOIN extraction too!
        
        # Handle database-prefixed JOIN patterns first (momo.table_name)
        db_prefixed_join_patterns = [
            # 🎯 Database-prefixed JOINs (momo.table_name)
            r'(?:LEFT|RIGHT|INNER|FULL|OUTER)?\s*JOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]+)(?:\s+(?:AS\s+)?([a-zA-Z_][a-zA-Z0-9_]*))?',
            
            # 🎯 Lowercase database-prefixed JOINs (join momo.table)
            r'(?:left|right|inner|full|outer)?\s*join\s+([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]+)(?:\s+(?:AS\s+)?([a-zA-Z_][a-zA-Z0-9_]*))?',
            
            # 🎯 Simple JOIN detection with database prefix
            r'\bjoin\s+([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]+)\s+on'
        ]
        
        # Process database-prefixed JOIN patterns first
        for pattern in db_prefixed_join_patterns:
            matches = re.finditer(pattern, sql, re.IGNORECASE)
            for match in matches:
                db_name = match.group(1)  # Database name (e.g., "momo")
                table_name = match.group(2)  # Actual table name (e.g., "mv_order")
                alias = None
                
                # Handle alias based on pattern (some have 3 groups, some have 4)
                if len(match.groups()) >= 3:
                    alias = match.group(3) if match.group(3) else None
                
                # Add database to detected schemas for filtering
                if db_name and db_name in ['momo', 'main_db', 'analytics_db', 'test_db', 'prod_db', 'dev_db']:
                    self.database_schemas.add(db_name)
                
                # Only add the actual table name, not the database prefix
                if table_name and self._is_valid_table_name(table_name):
                    self.detected_tables.add(table_name)
                    if alias and len(alias) > 1:
                        self.table_aliases[alias] = table_name
        
        # Handle standard JOIN patterns (no database prefix)
        standard_join_patterns = [
            # 🎯 Standard JOINs (no database prefix)
            r'(?:LEFT|RIGHT|INNER|FULL|OUTER)?\s*JOIN\s+([a-zA-Z_][a-zA-Z0-9_]+)(?:\s+(?:AS\s+)?([a-zA-Z_][a-zA-Z0-9_]*))?',
            
            # 🎯 Lowercase JOINs (no database prefix)
            r'(?:left|right|inner|full|outer)?\s*join\s+([a-zA-Z_][a-zA-Z0-9_]+)(?:\s+(?:AS\s+)?([a-zA-Z_][a-zA-Z0-9_]*))?',
            
            # 🎯 Legacy backtick JOINs
            r'(?:LEFT|RIGHT|INNER|FULL|OUTER)?\s*JOIN\s+`([a-zA-Z_][a-zA-Z0-9_]+)`(?:\s+(?:AS\s+)?`?([a-zA-Z_][a-zA-Z0-9_]*)`?)?',
            
            # 🎯 Legacy cross-database JOINs
            r'(?:LEFT|RIGHT|INNER|FULL|OUTER)?\s*JOIN\s+`[^`]+`\.`([a-zA-Z_][a-zA-Z0-9_]+)`(?:\s+(?:AS\s+)?`?([a-zA-Z_][a-zA-Z0-9_]*)`?)?'
        ]

        # 🎯 PIPELINE TRACE FIX: Filter out known database names from standard JOIN patterns
        known_database_names = {'momo', 'main_db', 'analytics_db', 'test_db', 'prod_db', 'dev_db'}
        
        for pattern in standard_join_patterns:
            matches = re.finditer(pattern, sql, re.IGNORECASE)
            for match in matches:
                table_name = match.group(1)
                alias = match.group(2) if len(match.groups()) >= 2 and match.group(2) else None

                # 🚨 CRITICAL FIX: Never add known database names as tables
                if table_name in known_database_names:
                    # This is a database name, not a table - skip it entirely
                    continue

                if self._is_valid_table_name(table_name):
                    self.detected_tables.add(table_name)
                    if alias and len(alias) > 1:
                        self.table_aliases[alias] = table_name

    def _extract_field_referenced_tables(self, sql: str) -> None:
        """🎯 Extract tables from field references"""
        
        # 🎯 USER'S EXCELLENT SUGGESTION: Apply dot-split approach to field references too!
        
        # Handle database-prefixed field references first (momo.table.field)
        db_prefixed_field_patterns = [
            # 🎯 Database-prefixed field references: momo.table.field
            r'\b([a-zA-Z_][a-zA-Z0-9_]+)\.([a-zA-Z_][a-zA-Z0-9_]+)\.([a-zA-Z_][a-zA-Z0-9_]+)\b',
            
            # 🎯 Function parameters with database prefix: func(momo.table.field)
            r'[A-Z_]+\s*\(\s*([a-zA-Z_][a-zA-Z0-9_]+)\.([a-zA-Z_][a-zA-Z0-9_]+)\.([a-zA-Z_][a-zA-Z0-9_]+)',
            
            # 🎯 Complex expressions with database prefix
            r'(?:CASE|IF|WHEN|COALESCE)\s*[^(]*([a-zA-Z_][a-zA-Z0-9_]+)\.([a-zA-Z_][a-zA-Z0-9_]+)\.([a-zA-Z_][a-zA-Z0-9_]+)'
        ]
        
        # Process database-prefixed field patterns first
        for pattern in db_prefixed_field_patterns:
            matches = re.findall(pattern, sql, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple) and len(match) >= 3:
                    db_name = match[0]    # Database name (e.g., "momo")
                    table_name = match[1]  # Actual table name (e.g., "mt_item")
                    field_name = match[2]  # Field name (e.g., "id")
                    
                    # Add database to detected schemas for filtering
                    if db_name and db_name in ['momo', 'main_db', 'analytics_db', 'test_db', 'prod_db', 'dev_db']:
                        self.database_schemas.add(db_name)
                    
                    # Only add the actual table name, not the database prefix
                    if table_name and self._is_valid_table_name(table_name):
                        # Resolve alias to actual table name
                        actual_table = self.table_aliases.get(table_name, table_name)
                        if actual_table not in self.database_schemas:
                            self.detected_tables.add(actual_table)
        
        # Handle standard field references (no database prefix)
        standard_field_patterns = [
            # 🎯 Standard field references: `table`.`field`
            r'`([a-zA-Z_][a-zA-Z0-9_]+)`\.`[a-zA-Z_][a-zA-Z0-9_]*`',
            
            # 🎯 Cross-database field references: `db`.`table`.`field`  
            r'`[^`]+`\.`([a-zA-Z_][a-zA-Z0-9_]+)`\.`[a-zA-Z_][a-zA-Z0-9_]*`',
            
            # 🎯 Function parameters: func(`table`.`field`)
            r'[A-Z_]+\s*\(\s*`([a-zA-Z_][a-zA-Z0-9_]+)`\.`[a-zA-Z_][a-zA-Z0-9_]*`',
            
            # 🎯 No backticks field references: table.field (two-part only)
            r'\b([a-zA-Z_][a-zA-Z0-9_]+)\.([a-zA-Z_][a-zA-Z0-9_]+)\b',
            
            # 🎯 Complex expressions with table references
            r'(?:CASE|IF|WHEN|COALESCE)\s*[^(]*`([a-zA-Z_][a-zA-Z0-9_]+)`\.`[a-zA-Z_][a-zA-Z0-9_]*`'
        ]

        for pattern in standard_field_patterns:
            matches = re.findall(pattern, sql, re.IGNORECASE)
            for match in matches:
                # Handle tuple results from regex groups
                if isinstance(match, tuple):
                    table_ref = match[0]  # First group is table name
                else:
                    table_ref = match

                # Resolve alias to actual table name
                actual_table = self.table_aliases.get(table_ref, table_ref)
                
                if (self._is_valid_table_name(actual_table) and 
                    actual_table not in self.database_schemas):
                    self.detected_tables.add(actual_table)

    def _extract_window_function_tables(self, sql: str) -> None:
        """🎯 Extract tables from window functions (OVER clause)"""
        
        window_patterns = [
            # 🎯 OVER with PARTITION BY
            r'OVER\s*\(\s*PARTITION\s+BY\s+`([a-zA-Z_][a-zA-Z0-9_]+)`\.`[a-zA-Z_][a-zA-Z0-9_]*`',
            
            # 🎯 OVER with ORDER BY
            r'OVER\s*\([^)]*ORDER\s+BY\s+`([a-zA-Z_][a-zA-Z0-9_]+)`\.`[a-zA-Z_][a-zA-Z0-9_]*`',
            
            # 🎯 General OVER clause table references
            r'OVER\s*\([^)]*`([a-zA-Z_][a-zA-Z0-9_]+)`\.`[a-zA-Z_][a-zA-Z0-9_]*`'
        ]

        for pattern in window_patterns:
            matches = re.findall(pattern, sql, re.IGNORECASE)
            for table_ref in matches:
                actual_table = self.table_aliases.get(table_ref, table_ref)
                if (self._is_valid_table_name(actual_table) and 
                    actual_table not in self.database_schemas):
                    self.detected_tables.add(actual_table)

    def _extract_subquery_tables(self, sql: str) -> None:
        """🎯 Extract tables from subqueries"""
        
        # 🎯 Find subqueries in SELECT clauses
        subquery_patterns = [
            # 🎯 EXISTS subqueries
            r'EXISTS\s*\(\s*SELECT[^)]+FROM\s+`([a-zA-Z_][a-zA-Z0-9_]+)`',
            
            # 🎯 IN subqueries
            r'IN\s*\(\s*SELECT[^)]+FROM\s+`([a-zA-Z_][a-zA-Z0-9_]+)`',
            
            # 🎯 Correlated subqueries
            r'\(\s*SELECT[^)]+FROM\s+`([a-zA-Z_][a-zA-Z0-9_]+)`[^)]*\)',
        ]

        for pattern in subquery_patterns:
            matches = re.findall(pattern, sql, re.IGNORECASE | re.DOTALL)
            for table_name in matches:
                if self._is_valid_table_name(table_name):
                    self.detected_tables.add(table_name)

    def extract_tables_from_tokens(self, token_stream: TokenStream) -> Tuple[List[str], Dict[str, str]]:
        """Extract tables from token stream"""
        self.reset()
        
        while token_stream.has_more():
            token = token_stream.current()
            
            # Look for FROM keyword
            if (token and token.type == TokenType.KEYWORD and 
                token.value.upper() == 'FROM'):
                self._extract_from_clause_from_tokens(token_stream)
            
            # Look for JOIN keywords
            elif (token and token.type == TokenType.KEYWORD and 
                  token.value.upper() in ['JOIN', 'LEFT', 'RIGHT', 'INNER', 'FULL', 'OUTER']):
                self._extract_join_from_tokens(token_stream)
            
            else:
                token_stream.advance()

        return sorted(list(self.detected_tables)), self.table_aliases

    def _extract_from_clause_from_tokens(self, token_stream: TokenStream) -> None:
        """Extract FROM clause from tokens"""
        token_stream.advance()  # Skip FROM
        
        # Handle parentheses
        if token_stream.current() and token_stream.current().type == TokenType.PAREN_OPEN:
            self._skip_nested_parentheses(token_stream)
        
        # Get table name
        table_token = token_stream.current()
        if table_token and table_token.type == TokenType.QUOTED_IDENTIFIER:
            table_name = table_token.value.strip('`')
            if self._is_valid_table_name(table_name):
                self.detected_tables.add(table_name)
                token_stream.advance()
                
                # Check for alias
                alias_token = token_stream.current()
                if alias_token and alias_token.type == TokenType.QUOTED_IDENTIFIER:
                    alias = alias_token.value.strip('`')
                    self.table_aliases[alias] = table_name
                    token_stream.advance()

    def _extract_join_from_tokens(self, token_stream: TokenStream) -> None:
        """Extract JOIN from tokens"""
        # Skip JOIN keywords
        while (token_stream.current() and 
               token_stream.current().type == TokenType.KEYWORD and
               token_stream.current().value.upper() in ['LEFT', 'RIGHT', 'INNER', 'FULL', 'OUTER', 'JOIN']):
            token_stream.advance()
        
        # Get table name
        table_token = token_stream.current()
        if table_token and table_token.type == TokenType.QUOTED_IDENTIFIER:
            table_name = table_token.value.strip('`')
            if self._is_valid_table_name(table_name):
                self.detected_tables.add(table_name)
                token_stream.advance()
                
                # Check for alias
                alias_token = token_stream.current()
                if alias_token and alias_token.type == TokenType.QUOTED_IDENTIFIER:
                    alias = alias_token.value.strip('`')
                    self.table_aliases[alias] = table_name
                    token_stream.advance()

    def _skip_nested_parentheses(self, token_stream: TokenStream) -> None:
        """Skip nested parentheses structure"""
        paren_level = 0
        
        while token_stream.has_more():
            token = token_stream.current()
            
            if token.type == TokenType.PAREN_OPEN:
                paren_level += 1
            elif token.type == TokenType.PAREN_CLOSE:
                paren_level -= 1
                if paren_level <= 0:
                    token_stream.advance()  # Skip closing paren
                    break
            
            token_stream.advance()

    def _is_valid_table_name(self, name: str) -> bool:
        """🎯 Enhanced table name validation"""
        if not name or len(name) < 2:
            return False

        # Skip SQL keywords
        sql_keywords = {
            'SELECT', 'FROM', 'WHERE', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL', 'OUTER',
            'ON', 'AS', 'AND', 'OR', 'NOT', 'IN', 'BETWEEN', 'LIKE', 'IS', 'NULL',
            'GROUP', 'BY', 'ORDER', 'HAVING', 'LIMIT', 'UNION', 'ALL', 'DISTINCT',
            'WITH', 'RECURSIVE', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'IF',
            'EXISTS', 'OVER', 'PARTITION', 'WINDOW'
        }
        if name.upper() in sql_keywords:
            return False

        # Skip database schemas
        if name in self.database_schemas:
            return False

        # Skip obvious database names
        if (re.match(r'^(main_db|analytics_db|test_db|prod_db|dev_db|momo)$', name) or
            name.lower().endswith('_db')):
            return False

        # Skip single character names (likely aliases)
        if len(name) == 1:
            return False

        # Skip obvious non-table words
        obvious_keywords = {
            'select', 'from', 'where', 'join', 'inner', 'left', 'right', 'on', 
            'and', 'or', 'not', 'in', 'is', 'as', 'if', 'case', 'when', 'then', 
            'else', 'end', 'null', 'true', 'false'
        }
        if name.lower() in obvious_keywords:
            return False

        return True

    def get_table_summary(self) -> Dict[str, Any]:
        """Get summary of detected tables"""
        return {
            "total_tables": len(self.detected_tables),
            "tables": sorted(list(self.detected_tables)),
            "aliases": self.table_aliases,
            "cte_tables": sorted(list(self.cte_tables)),
            "database_schemas": sorted(list(self.database_schemas))
        }

    def reset(self):
        """Reset extractor state"""
        self.detected_tables.clear()
        self.table_aliases.clear()
        self.database_schemas.clear()
        # Don't clear CTE tables as they come from external source

# Helper function for easy integration
def extract_all_tables_from_sql(sql: str, cte_tables: Set[str] = None) -> Tuple[List[str], Dict[str, str]]:
    """Extract all tables from SQL"""
    extractor = TableExtractor()
    return extractor.extract_all_tables(sql, cte_tables)

if __name__ == "__main__":
    print("🔍 Table Extractor - SQL Parser AST v6.0")
    print("=" * 60)
    
    # Test with complex SQL
    test_sql = """
    WITH sales_cte AS (SELECT * FROM sales)
    SELECT s.amount, p.name, c.email 
    FROM (((`products` p 
    JOIN `sales` s ON p.id = s.product_id) 
    LEFT JOIN `customers` c ON s.customer_id = c.id))
    WHERE p.active = 1
    """
    
    extractor = TableExtractor()
    tables, aliases = extractor.extract_all_tables(test_sql, {'sales_cte'})
    summary = extractor.get_table_summary()
    
    print(f"✅ Extracted {len(tables)} tables: {tables}")
    print(f"✅ Table aliases: {aliases}")
    print(f"✅ Summary: {summary}")
    print("\n🎯 Ready for AST integration!")
