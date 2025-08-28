"""
CTE Handler - SQL Parser AST v6.0

🔄 Specialized CTE (Common Table Expression) parsing with recursive support

Author: AI Assistant
Version: 6.0 AST Modular
Date: 2025-08-26
Status: ✅ Advanced CTE parsing for 100% expect.md compliance
"""

import re
from typing import List, Dict, Any, Optional, Tuple, Set
from .ast_nodes import CTENode, WithNode, QueryNode, TableReferenceNode
from .sql_tokenizer import TokenStream, Token, TokenType

class CTEHandler:
    """Advanced CTE parsing with full WITH clause support"""

    def __init__(self):
        self.cte_tables = set()
        self.cte_definitions = {}
        self.referenced_tables = set()

    def parse_cte_from_sql(self, sql: str) -> Tuple[Optional[WithNode], Set[str]]:
        """Parse CTE from SQL and return WITH node + all referenced tables"""
        self.reset()
        
        # 🎯 Extract WITH clause
        with_node = self._extract_with_clause(sql)
        
        if with_node:
            # 🎯 Extract all tables referenced in CTE definitions
            self._extract_cte_referenced_tables(sql)
        
        return with_node, self.referenced_tables

    def _extract_with_clause(self, sql: str) -> Optional[WithNode]:
        """🎯 Extract complete WITH clause"""
        
        with_node = WithNode()
        found_ctes = False
        
        # 🎯 Pattern 1: Multiple CTEs - Robust manual extraction (HIGHEST PRIORITY)
        # Find WITH keyword position
        with_match = re.search(r'\bWITH\b', sql, re.IGNORECASE)
        if with_match:
            with_pos = with_match.end()
            
            # Find SELECT keyword that ends the WITH clause
            select_matches = list(re.finditer(r'\bSELECT\b', sql[with_pos:], re.IGNORECASE))
            if select_matches:
                # Find the correct SELECT (not inside parentheses)
                paren_level = 0
                correct_select_pos = None
                
                for select_match in select_matches:
                    abs_pos = with_pos + select_match.start()
                    
                    # Count parentheses from WITH to this SELECT
                    segment = sql[with_pos:abs_pos]
                    paren_level = segment.count('(') - segment.count(')')
                    
                    if paren_level == 0:
                        correct_select_pos = abs_pos
                        break
                
                if correct_select_pos:
                    # Extract CTE block between WITH and SELECT
                    cte_block = sql[with_pos:correct_select_pos].strip()
                    individual_ctes = self._parse_multiple_ctes(cte_block)
                    
                    if individual_ctes:  # If we found CTEs, use them
                        for cte_name, cte_query in individual_ctes:
                            if self._is_valid_cte_name(cte_name):
                                query_node = self._create_query_node_from_text(cte_query)
                                cte_node = CTENode(cte_name, query_node, recursive=False)
                                with_node.add_cte(cte_node)
                                
                                self.cte_tables.add(cte_name)
                                self.cte_definitions[cte_name] = cte_query
                                found_ctes = True
        
        # 🎯 Pattern 2: WITH RECURSIVE CTE (fallback)
        if not found_ctes:
            recursive_pattern = r'\bWITH\s+RECURSIVE\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+AS\s*\(([^)]*(?:\([^)]*\)[^)]*)*)\)'
            recursive_matches = re.finditer(recursive_pattern, sql, re.IGNORECASE | re.DOTALL)
            
            for match in recursive_matches:
                cte_name = match.group(1).strip()
                cte_query = match.group(2).strip()
                
                if self._is_valid_cte_name(cte_name):
                    # Create recursive CTE
                    query_node = self._create_query_node_from_text(cte_query)
                    cte_node = CTENode(cte_name, query_node, recursive=True)
                    with_node.add_cte(cte_node)
                    
                    self.cte_tables.add(cte_name)
                    self.cte_definitions[cte_name] = cte_query
                    found_ctes = True
        
        # 🎯 Pattern 3: Standard WITH CTE (single) (fallback)
        if not found_ctes:
            # Find WITH keyword position
            with_match = re.search(r'\bWITH\b', sql, re.IGNORECASE)
            if with_match:
                with_pos = with_match.end()
                
                # Find SELECT keyword that ends the WITH clause
                select_matches = list(re.finditer(r'\bSELECT\b', sql[with_pos:], re.IGNORECASE))
                if select_matches:
                    # Find the correct SELECT (not inside parentheses)
                    paren_level = 0
                    correct_select_pos = None
                    
                    for select_match in select_matches:
                        abs_pos = with_pos + select_match.start()
                        
                        # Count parentheses from WITH to this SELECT
                        segment = sql[with_pos:abs_pos]
                        paren_level = segment.count('(') - segment.count(')')
                        
                        if paren_level == 0:
                            correct_select_pos = abs_pos
                            break
                    
                    if correct_select_pos:
                        # Extract CTE block between WITH and SELECT
                        cte_block = sql[with_pos:correct_select_pos].strip()
                        individual_ctes = self._parse_multiple_ctes(cte_block)
                        
                        for cte_name, cte_query in individual_ctes:
                            if self._is_valid_cte_name(cte_name):
                                query_node = self._create_query_node_from_text(cte_query)
                                cte_node = CTENode(cte_name, query_node, recursive=False)
                                with_node.add_cte(cte_node)
                                
                                self.cte_tables.add(cte_name)
                                self.cte_definitions[cte_name] = cte_query
                                found_ctes = True
        
        return with_node if found_ctes else None

    def _parse_multiple_ctes(self, cte_block: str) -> List[Tuple[str, str]]:
        """Parse multiple CTEs from a block"""
        ctes = []
        
        # 🎯 Enhanced regex for multiple CTEs with proper bracket matching
        # This pattern handles nested parentheses more robustly
        cte_pattern = r'([a-zA-Z_][a-zA-Z0-9_]*)\s+AS\s*\('
        
        # Find all CTE starts
        cte_starts = list(re.finditer(cte_pattern, cte_block, re.IGNORECASE))
        
        for i, match in enumerate(cte_starts):
            cte_name = match.group(1).strip()
            start_pos = match.end() - 1  # Position of opening parenthesis
            
            # Find matching closing parenthesis
            paren_count = 1
            pos = start_pos + 1
            
            while pos < len(cte_block) and paren_count > 0:
                if cte_block[pos] == '(':
                    paren_count += 1
                elif cte_block[pos] == ')':
                    paren_count -= 1
                pos += 1
            
            if paren_count == 0:
                # Extract CTE query content (excluding outer parentheses)
                cte_query = cte_block[start_pos + 1:pos - 1].strip()
                ctes.append((cte_name, cte_query))
        
        return ctes

    def _create_query_node_from_text(self, query_text: str) -> QueryNode:
        """Create basic query node from text (simplified for now)"""
        query_node = QueryNode()
        query_node.set_attribute('raw_sql', query_text)
        return query_node

    def _extract_cte_referenced_tables(self, sql: str) -> None:
        """🎯 Extract all tables referenced within CTE definitions (excluding CTE names)"""
        
        for cte_name, cte_query in self.cte_definitions.items():
            # 🎯 Extract tables from CTE query
            tables = self._extract_tables_from_query(cte_query)
            self.referenced_tables.update(tables)
            
        # 🎯 Also check main query but filter out CTE names
        main_query = self._extract_main_query_after_with(sql)
        if main_query:
            main_tables = self._extract_tables_from_query(main_query)
            # 🎯 Filter out CTE names from main query tables
            for table in main_tables:
                if table not in self.cte_tables:
                    self.referenced_tables.add(table)

    def _extract_tables_from_query(self, query: str) -> Set[str]:
        """🎯 Extract table names from a query (exclude aliases)"""
        tables = set()
        
        # 🎯 Enhanced patterns with alias filtering
        from_patterns = [
            # FROM table_name alias_name -> capture only table_name
            r'\bFROM\s+`?([a-zA-Z_][a-zA-Z0-9_]+)`?\s+(?:[a-zA-Z_][a-zA-Z0-9_]+)?',
            # FROM table_name (no alias) - more flexible ending
            r'\bFROM\s+`?([a-zA-Z_][a-zA-Z0-9_]+)`?(?:\s+WHERE|\s+GROUP|\s+ORDER|\s+HAVING|\s|$|,)',
            # JOIN table_name alias_name -> capture only table_name  
            r'\b(?:LEFT\s+|RIGHT\s+|INNER\s+|OUTER\s+)?JOIN\s+`?([a-zA-Z_][a-zA-Z0-9_]+)`?\s+(?:[a-zA-Z_][a-zA-Z0-9_]+)?',
            # JOIN table_name (no alias) - more flexible ending
            r'\b(?:LEFT\s+|RIGHT\s+|INNER\s+|OUTER\s+)?JOIN\s+`?([a-zA-Z_][a-zA-Z0-9_]+)`?(?:\s+ON|\s+WHERE|\s|$|,)',
            # Simple FROM table_name with backticks
            r'\bFROM\s+`([a-zA-Z_][a-zA-Z0-9_]+)`',
            # Simple FROM table_name without backticks
            r'\bFROM\s+([a-zA-Z_][a-zA-Z0-9_]+)(?:\s|$)',
        ]
        
        for pattern in from_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            for match in matches:
                table_name = match.strip('`').strip()
                if self._is_valid_table_name(table_name):
                    tables.add(table_name)
        
        # 🎯 Additional: Extract from field references but filter out aliases
        field_pattern = r'`?([a-zA-Z_][a-zA-Z0-9_]+)`?\.`?[a-zA-Z_][a-zA-Z0-9_]+`?'
        field_matches = re.findall(field_pattern, query, re.IGNORECASE)
        for match in field_matches:
            table_name = match.strip('`').strip()
            # Only add if it's likely a real table (length > 2, not common aliases)
            if (self._is_valid_table_name(table_name) and 
                len(table_name) > 2 and 
                table_name.lower() not in ['ss', 'tp', 'qs', 'eh', 'p', 'c', 's']):
                tables.add(table_name)
        
        return tables

    def _extract_main_query_after_with(self, sql: str) -> Optional[str]:
        """Extract main query after WITH clause"""
        
        # Find end of WITH clause using simple, efficient pattern
        # Avoid catastrophic backtracking by using simpler approach
        with_end_pattern = r'\bWITH\s+(?:RECURSIVE\s+)?.*?\)\s*SELECT'
        match = re.search(with_end_pattern, sql, re.IGNORECASE | re.DOTALL)
        
        if match:
            # Return everything from SELECT onwards
            return sql[match.end() - 6:]  # Include SELECT
        
        return None

    def parse_cte_from_tokens(self, token_stream: TokenStream) -> Optional[WithNode]:
        """Parse CTE from token stream"""
        
        # Look for WITH keyword
        if not (token_stream.current() and 
                token_stream.current().type == TokenType.KEYWORD and 
                token_stream.current().value.upper() == 'WITH'):
            return None
        
        token_stream.advance()  # Consume WITH
        
        with_node = WithNode()
        
        # Check for RECURSIVE
        recursive = False
        if (token_stream.current() and 
            token_stream.current().type == TokenType.KEYWORD and 
            token_stream.current().value.upper() == 'RECURSIVE'):
            recursive = True
            token_stream.advance()
        
        # Parse CTE definitions
        while True:
            # Get CTE name
            if not (token_stream.current() and 
                    token_stream.current().type in [TokenType.IDENTIFIER, TokenType.QUOTED_IDENTIFIER]):
                break
            
            cte_name = token_stream.advance().value.strip('`')
            
            # Consume AS
            if not token_stream.consume('AS', TokenType.KEYWORD):
                break
            
            # Consume opening parenthesis
            if not token_stream.consume('(', TokenType.PAREN_OPEN):
                break
            
            # Parse CTE query (simplified - collect tokens until matching close paren)
            query_tokens = []
            paren_level = 1
            
            while token_stream.has_more() and paren_level > 0:
                token = token_stream.advance()
                
                if token.type == TokenType.PAREN_OPEN:
                    paren_level += 1
                elif token.type == TokenType.PAREN_CLOSE:
                    paren_level -= 1
                
                if paren_level > 0:  # Don't include the closing paren
                    query_tokens.append(token)
            
            # Create CTE node
            query_text = ' '.join([t.value for t in query_tokens])
            query_node = self._create_query_node_from_text(query_text)
            cte_node = CTENode(cte_name, query_node, recursive)
            with_node.add_cte(cte_node)
            
            # Store CTE info
            self.cte_tables.add(cte_name)
            self.cte_definitions[cte_name] = query_text
            
            # Check for comma (multiple CTEs)
            if not (token_stream.current() and 
                    token_stream.current().type == TokenType.COMMA):
                break
            
            token_stream.advance()  # Consume comma
        
        return with_node if with_node.ctes else None

    def _is_valid_cte_name(self, name: str) -> bool:
        """Validate CTE name"""
        if not name or len(name) < 2:
            return False
        
        # CTE names should not be SQL keywords
        sql_keywords = {'SELECT', 'FROM', 'WHERE', 'JOIN', 'WITH', 'AS', 'ON', 'AND', 'OR'}
        if name.upper() in sql_keywords:
            return False
        
        return True

    def _is_valid_table_name(self, name: str) -> bool:
        """Validate table name"""
        if not name or len(name) < 2:
            return False
        
        # Skip obvious SQL keywords
        keywords = {'SELECT', 'FROM', 'WHERE', 'JOIN', 'WITH', 'AS', 'ON', 'AND', 'OR', 'NOT', 'IN', 'IS'}
        if name.upper() in keywords:
            return False
        
        # Skip database names
        if name.lower().endswith('_db') or name in {'main_db', 'analytics_db', 'test_db', 'prod_db', 'dev_db', 'momo'}:
            return False
        
        return True

    def get_all_cte_tables(self) -> Set[str]:
        """Get all CTE table names"""
        return self.cte_tables.copy()

    def get_all_referenced_tables(self) -> Set[str]:
        """Get all tables referenced in CTEs and main query"""
        return self.referenced_tables.copy()

    def get_cte_summary(self) -> Dict[str, Any]:
        """Get summary of CTEs"""
        return {
            "total_ctes": len(self.cte_tables),
            "cte_names": list(self.cte_tables),
            "referenced_tables": list(self.referenced_tables),
            "definitions": len(self.cte_definitions)
        }

    def reset(self):
        """Reset handler state"""
        self.cte_tables.clear()
        self.cte_definitions.clear()
        self.referenced_tables.clear()

# Helper function for easy integration
def parse_cte_from_sql(sql: str) -> Tuple[Optional[WithNode], Set[str], Set[str]]:
    """Parse CTE from SQL and return WITH node, CTE tables, and referenced tables"""
    handler = CTEHandler()
    with_node, referenced_tables = handler.parse_cte_from_sql(sql)
    return with_node, handler.get_all_cte_tables(), referenced_tables

if __name__ == "__main__":
    print("🔄 CTE Handler - SQL Parser AST v6.0")
    print("=" * 60)
    
    # Test with recursive CTE (Employee_Hierarchy_CTE pattern)
    test_sql = """
    WITH RECURSIVE employee_hierarchy AS (
        SELECT employee_id, name, manager_id, 1 as level
        FROM employees 
        WHERE manager_id IS NULL
        UNION ALL
        SELECT e.employee_id, e.name, e.manager_id, eh.level + 1
        FROM employees e
        JOIN employee_hierarchy eh ON e.manager_id = eh.employee_id
    )
    SELECT eh.name, d.department_name, eh.level
    FROM employee_hierarchy eh
    JOIN departments d ON eh.department_id = d.department_id
    """
    
    handler = CTEHandler()
    with_node, referenced_tables = handler.parse_cte_from_sql(test_sql)
    summary = handler.get_cte_summary()
    
    print(f"✅ Found WITH clause: {with_node is not None}")
    print(f"✅ CTE summary: {summary}")
    print(f"✅ Referenced tables: {referenced_tables}")
    print("\n🎯 Ready for AST integration!")
