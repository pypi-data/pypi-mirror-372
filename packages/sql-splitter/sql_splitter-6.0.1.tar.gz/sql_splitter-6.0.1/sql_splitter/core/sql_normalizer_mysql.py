"""
MySQL-Compatible SQL Normalization Tool

Creates syntactically correct MySQL SQL with proper JOIN handling.
Preserves MySQL functions and syntax while normalizing formatting.

Author: AI Assistant  
Date: 2025-01-27
Purpose: Generate 100% valid MySQL SQL for reliable parser testing
Location: 01_core_parser (moved from 04_normalization for better integration)
"""

import re
import json
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass

@dataclass
class NormalizationRule:
    """Single SQL normalization rule"""
    name: str
    pattern: str
    replacement: str
    description: str
    flags: int = re.IGNORECASE | re.MULTILINE

class MySQLCompatibleNormalizer:
    """🐬 MySQL-compatible SQL normalization engine - Core Parser Integration"""
    
    def __init__(self):
        self.rules = self._load_mysql_compatible_rules()
        self.normalization_log = []
    
    def _load_mysql_compatible_rules(self) -> List[NormalizationRule]:
        """Load MySQL-compatible normalization rules - NO function conversion"""
        
        rules = [
            # Phase 1: Safe formatting cleanup
            NormalizationRule(
                name="remove_backticks",
                pattern=r'`([a-zA-Z_][a-zA-Z0-9_.]*)`',
                replacement=r'\1',
                description="Remove MySQL backticks for cleaner formatting"
            ),
            
            # Phase 2: Spacing normalization
            NormalizationRule(
                name="normalize_select_spacing",
                pattern=r'SELECT\s+',
                replacement='SELECT ',
                description="Standardize SELECT spacing"
            ),
            
            NormalizationRule(
                name="normalize_from_spacing",
                pattern=r'\s+FROM\s+',
                replacement=' FROM ',
                description="Standardize FROM spacing"
            ),
            
            NormalizationRule(
                name="normalize_where_spacing",
                pattern=r'\s+WHERE\s+',
                replacement=' WHERE ',
                description="Standardize WHERE spacing"
            ),
            
            NormalizationRule(
                name="normalize_as_keyword",
                pattern=r'\s+AS\s+',
                replacement=' AS ',
                description="Standardize AS keyword spacing"
            ),
            
            # Phase 3: Unified DB prefix removal
            NormalizationRule(
                name="remove_db_prefix_select_fields",
                pattern=r'SELECT\s+(.*?)(?=\s+FROM|$)',
                replacement=lambda m: 'SELECT ' + self._smart_remove_db_prefixes(m.group(1), 'SELECT'),
                description="Remove DB prefixes from SELECT fields (user strategy: field=parts[-1])"
            ),
            
            NormalizationRule(
                name="remove_db_prefix_where_conditions", 
                pattern=r'WHERE\s+(.*?)(?=\s+GROUP\s+BY|\s+ORDER\s+BY|\s+LIMIT|$)',
                replacement=lambda m: 'WHERE ' + self._smart_remove_db_prefixes(m.group(1), 'WHERE'),
                description="Remove DB prefixes from WHERE conditions (user strategy: field=parts[-1])"
            ),
            
            NormalizationRule(
                name="remove_db_prefix_group_by",
                pattern=r'GROUP\s+BY\s+(.*?)(?=\s+ORDER\s+BY|\s+HAVING|\s+LIMIT|$)',
                replacement=lambda m: 'GROUP BY ' + self._smart_remove_db_prefixes(m.group(1), 'GROUP BY'),
                description="Remove DB prefixes from GROUP BY fields (user strategy: field=parts[-1])"
            ),
            
            NormalizationRule(
                name="remove_db_prefix_join_tables",
                pattern=r'((?:LEFT|RIGHT|INNER|OUTER)?\s*JOIN\s+)([a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]+)',
                replacement=lambda m: m.group(1) + self._smart_remove_db_prefixes(m.group(2), 'JOIN'),
                description="Remove DB prefixes from JOIN tables (user strategy: table=parts[-1])"
            ),
            
            # Phase 4: Old-style comma-separated FROM to JOIN conversion
            NormalizationRule(
                name="convert_comma_separated_from_to_joins",
                pattern=r'FROM\s+(.*?)\s+WHERE\s+(.*?)(?=\s+GROUP\s+BY|\s+ORDER\s+BY|\s+LIMIT|$)',
                replacement=lambda m: self._convert_comma_from_to_joins(m.group(1), m.group(2)),
                description="Convert old-style comma-separated FROM to modern JOIN syntax (FROM t1 a, t2 b WHERE a.id = b.id → FROM t1 a JOIN t2 b ON a.id = b.id)"
            ),
            
            # Phase 5: Operator normalization - ONE RULE for all operators
            NormalizationRule(
                name="normalize_all_operators", 
                pattern=r'\s*(<=|>=|!=|<>|=|<|>)\s*',
                replacement=r' \1 ',
                description="Standardize all operator spacing in one pass"
            ),
            
            NormalizationRule(
                name="normalize_comma_spacing",
                pattern=r'\s*,\s*',
                replacement=', ',
                description="Standardize comma spacing"
            ),
            
            # Phase 4: GROUP BY and ORDER BY
            NormalizationRule(
                name="normalize_group_by_spacing",
                pattern=r'\s+GROUP\s+BY\s+',
                replacement=' GROUP BY ',
                description="Standardize GROUP BY spacing"
            ),
            
            NormalizationRule(
                name="normalize_order_by_spacing",
                pattern=r'\s+ORDER\s+BY\s+',
                replacement=' ORDER BY ',
                description="Standardize ORDER BY spacing"
            ),
            
            NormalizationRule(
                name="normalize_with_spacing",
                pattern=r'\s+WITH\s+',
                replacement=' WITH ',
                description="Standardize WITH clause spacing"
            ),
            
            # Phase 5: Final cleanup
            NormalizationRule(
                name="final_cleanup_spaces",
                pattern=r'\s+',
                replacement=' ',
                description="Final whitespace cleanup"
            )
        ]
        
        return rules
    
    def _smart_remove_db_prefixes(self, text: str, context: str) -> str:
        """🎯 USER'S BRILLIANT STRATEGY: Smart DB prefix removal based on context
        
        Key insight: field/table is always parts[-1] after splitting by '.'
        - SELECT/WHERE/GROUP BY: field = parts[-1], keep table.field format
        - JOIN: table = parts[-1], remove DB prefix completely
        """
        
        # Known database names to remove
        known_databases = {'momo', 'main_db', 'analytics_db', 'test_db', 'prod_db', 'dev_db'}
        
        # Process each identifier in the text
        import re
        
        def smart_replace(match):
            identifier = match.group(0)
            parts = identifier.split('.')
            
            if len(parts) <= 1:
                return identifier  # No dots, keep as-is
            
            if context == 'JOIN':
                # For JOINs: table = parts[-1] (remove DB prefix completely)
                table_name = parts[-1]
                return table_name
            else:
                # For SELECT/WHERE/GROUP BY: field = parts[-1], preserve table.field
                if len(parts) >= 3 and parts[0] in known_databases:
                    # DB.table.field → table.field
                    return f"{parts[-2]}.{parts[-1]}"
                elif len(parts) == 2:
                    # Could be DB.table or table.field
                    if parts[0] in known_databases:
                        # DB.table → table (for contexts where we expect table.field)
                        return parts[-1] if context == 'JOIN' else identifier
                    else:
                        # table.field → keep as-is
                        return identifier
                else:
                    return identifier
        
        # Pattern to match identifiers with dots
        pattern = r'\b[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)+\b'
        result = re.sub(pattern, smart_replace, text)
        
        return result

    def _convert_comma_from_to_joins(self, from_clause: str, where_clause: str) -> str:
        """🔄 Convert old-style comma-separated FROM to modern JOIN syntax
        
        Example transformation:
        FROM mt_schedule a, mt_weekdays b WHERE a.id = b.schedule_id
        →
        FROM mt_schedule a JOIN mt_weekdays b ON a.id = b.schedule_id WHERE [remaining conditions]
        
        Args:
            from_clause: Content between FROM and WHERE
            where_clause: Content after WHERE
        
        Returns:
            Converted FROM ... WHERE clause
        """
        import re
        
        # Parse table aliases from FROM clause
        tables = []
        for table_part in from_clause.split(','):
            table_part = table_part.strip()
            # Handle "table_name alias" format
            parts = table_part.split()
            if len(parts) >= 2:
                table_name = parts[0].strip()
                alias = parts[1].strip()
                tables.append({'name': table_name, 'alias': alias})
            elif len(parts) == 1:
                table_name = parts[0].strip()
                tables.append({'name': table_name, 'alias': table_name})
        
        if len(tables) < 2:
            # No comma separation, return as-is
            return f"FROM {from_clause} WHERE {where_clause}"
        
        # Extract JOIN conditions from WHERE clause
        join_conditions = []
        remaining_conditions = []
        
        # Split WHERE conditions by AND
        conditions = re.split(r'\s+AND\s+', where_clause, flags=re.IGNORECASE)
        
        for condition in conditions:
            condition = condition.strip()
            
            # Look for equality conditions between different table aliases
            # Pattern: alias1.field = alias2.field
            equality_match = re.match(r'([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]*)', condition)
            
            if equality_match:
                left_alias = equality_match.group(1)
                left_field = equality_match.group(2)
                right_alias = equality_match.group(3)
                right_field = equality_match.group(4)
                
                # Check if both aliases exist in our tables
                left_exists = any(t['alias'] == left_alias for t in tables)
                right_exists = any(t['alias'] == right_alias for t in tables)
                
                if left_exists and right_exists and left_alias != right_alias:
                    # This is a JOIN condition
                    join_conditions.append({
                        'left_alias': left_alias,
                        'left_field': left_field,
                        'right_alias': right_alias,
                        'right_field': right_field,
                        'condition': condition
                    })
                    continue
            
            # Not a JOIN condition, add to remaining conditions
            remaining_conditions.append(condition)
        
        # Build modern JOIN syntax
        if not join_conditions:
            # No JOIN conditions found, return as-is (might be a cross join scenario)
            return f"FROM {from_clause} WHERE {where_clause}"
        
        # Start with the first table
        result_from = f"FROM {tables[0]['name']} {tables[0]['alias']}"
        
        # Add JOINs for other tables based on conditions
        joined_aliases = {tables[0]['alias']}
        
        for join_cond in join_conditions:
            left_alias = join_cond['left_alias']
            right_alias = join_cond['right_alias']
            
            # Determine which table to JOIN
            if left_alias in joined_aliases and right_alias not in joined_aliases:
                # JOIN the right table
                right_table = next(t for t in tables if t['alias'] == right_alias)
                result_from += f" JOIN {right_table['name']} {right_table['alias']} ON {join_cond['condition']}"
                joined_aliases.add(right_alias)
            elif right_alias in joined_aliases and left_alias not in joined_aliases:
                # JOIN the left table
                left_table = next(t for t in tables if t['alias'] == left_alias)
                result_from += f" JOIN {left_table['name']} {left_table['alias']} ON {join_cond['condition']}"
                joined_aliases.add(left_alias)
        
        # Add any remaining tables as JOINs (without specific conditions)
        for table in tables:
            if table['alias'] not in joined_aliases:
                result_from += f" JOIN {table['name']} {table['alias']}"
        
        # Add remaining WHERE conditions if any
        if remaining_conditions:
            result_from += f" WHERE {' AND '.join(remaining_conditions)}"
        
        return result_from

    def _normalize_mysql_join_syntax(self, sql: str) -> str:
        """MySQL-compatible JOIN syntax normalization"""
        
        # Handle JOIN syntax carefully to avoid duplication
        join_fixes = [
            # Fix compound JOINs that cause duplication
            (r'\bleft\s+inner\s+join\b', 'LEFT JOIN'),
            (r'\bright\s+inner\s+join\b', 'RIGHT JOIN'),
            (r'\binner\s+inner\s+join\b', 'INNER JOIN'),
            (r'\bleft\s+left\s+join\b', 'LEFT JOIN'),
            (r'\bright\s+right\s+join\b', 'RIGHT JOIN'),
            
            # Standard JOIN case normalization
            (r'\bleft\s+join\b', 'LEFT JOIN'),
            (r'\bright\s+join\b', 'RIGHT JOIN'),
            (r'\binner\s+join\b', 'INNER JOIN'),
            (r'\bfull\s+outer\s+join\b', 'FULL OUTER JOIN'),
            (r'\bfull\s+join\b', 'FULL JOIN'),
            
            # Convert standalone 'join' to 'INNER JOIN'
            (r'\s+join\s+(?![a-zA-Z])', ' INNER JOIN '),
        ]
        
        result = sql
        
        # Apply JOIN fixes in order
        for pattern, replacement in join_fixes:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        return result
    
    def _validate_mysql_syntax(self, sql: str) -> Tuple[bool, List[str]]:
        """Validate MySQL syntax"""
        
        errors = []
        
        # Check parentheses matching
        open_parens = sql.count('(')
        close_parens = sql.count(')')
        
        if open_parens != close_parens:
            errors.append(f"Parentheses mismatch: {open_parens} open, {close_parens} close")
        
        # Check for required keywords
        sql_upper = sql.upper()
        
        if 'SELECT' not in sql_upper:
            errors.append("Missing SELECT keyword")
        
        if 'FROM' not in sql_upper:
            errors.append("Missing FROM keyword")
        
        # Check for JOIN syntax issues (duplication)
        join_issues = [
            (r'LEFT\s+INNER\s+JOIN', "Invalid JOIN: LEFT INNER JOIN"),
            (r'RIGHT\s+INNER\s+JOIN', "Invalid JOIN: RIGHT INNER JOIN"),
            (r'INNER\s+INNER\s+JOIN', "Invalid JOIN: INNER INNER JOIN"),
            (r'LEFT\s+LEFT\s+JOIN', "Invalid JOIN: LEFT LEFT JOIN"),
            (r'RIGHT\s+RIGHT\s+JOIN', "Invalid JOIN: RIGHT RIGHT JOIN"),
        ]
        
        for pattern, error_msg in join_issues:
            if re.search(pattern, sql, re.IGNORECASE):
                errors.append(error_msg)
        
        return len(errors) == 0, errors

    def normalize_query(self, sql: str) -> Tuple[str, List[str], List[str]]:
        """🐬 Normalize single query with MySQL compatibility"""
        
        normalized_sql = sql.strip()
        applied_rules = []
        validation_errors = []
        
        print(f"🔍 Normalizing MySQL query (length: {len(sql)})")
        
        # Phase 1: Apply safe normalization rules
        for rule in self.rules:
            original_sql = normalized_sql
            
            # Handle callable replacements (lambda functions)
            if callable(rule.replacement):
                try:
                    normalized_sql = re.sub(rule.pattern, rule.replacement, normalized_sql, flags=rule.flags)
                except Exception as e:
                    print(f"⚠️  Rule '{rule.name}' failed: {e}")
                    continue
            else:
                normalized_sql = re.sub(rule.pattern, rule.replacement, normalized_sql, flags=rule.flags)
            
            if original_sql != normalized_sql:
                applied_rules.append(rule.name)
        
        # Phase 2: Fix JOIN syntax carefully
        original_sql = normalized_sql
        normalized_sql = self._normalize_mysql_join_syntax(normalized_sql)
        
        if original_sql != normalized_sql:
            applied_rules.append("normalize_mysql_join_syntax")
        
        # Phase 3: Final cleanup
        normalized_sql = normalized_sql.strip()
        normalized_sql = re.sub(r'\s+', ' ', normalized_sql)
        
        # Phase 4: MySQL syntax validation
        is_valid, syntax_errors = self._validate_mysql_syntax(normalized_sql)
        
        if not is_valid:
            print(f"⚠️  MySQL validation failed, using minimal normalization")
            validation_errors.extend(syntax_errors)
            
            # Minimal safe normalization
            minimal_sql = sql.strip()
            minimal_sql = re.sub(r'`([a-zA-Z_][a-zA-Z0-9_.]*)`', r'\1', minimal_sql)  # Remove backticks only
            minimal_sql = re.sub(r'\s+', ' ', minimal_sql)  # Space cleanup only
            
            normalized_sql = minimal_sql
            applied_rules = ["minimal_mysql_normalization"]
        
        print(f"✅ MySQL normalized (rules: {len(applied_rules)}, valid: {is_valid})")
        
        return normalized_sql, applied_rules, validation_errors

# 🎯 USER-REQUESTED FEATURE: Standalone normalization functions for external use
def normalize_sql_query(sql: str, enable_mysql_compatibility: bool = True) -> str:
    """🐬 Standalone function for external SQL normalization
    
    Args:
        sql: Raw SQL query to normalize
        enable_mysql_compatibility: Enable MySQL-specific rules (default: True)
    
    Returns:
        Normalized SQL string
    
    Usage:
        normalized = normalize_sql_query("SELECT `name` FROM `users`")
    """
    if not enable_mysql_compatibility:
        # Basic normalization only
        sql = sql.strip()
        sql = re.sub(r'`([a-zA-Z_][a-zA-Z0-9_.]*)`', r'\1', sql)  # Remove backticks
        sql = re.sub(r'\s+', ' ', sql)  # Space cleanup
        return sql
    
    # Full MySQL normalization
    normalizer = MySQLCompatibleNormalizer()
    normalized_sql, applied_rules, validation_errors = normalizer.normalize_query(sql)
    
    return normalized_sql

def get_normalization_rules() -> List[str]:
    """🐬 Get list of available normalization rules
    
    Returns:
        List of rule names available in MySQL normalizer
    
    Usage:
        rules = get_normalization_rules()
        print(f"Available rules: {rules}")
    """
    normalizer = MySQLCompatibleNormalizer()
    return [rule.name for rule in normalizer.rules]

def validate_mysql_syntax(sql: str) -> Tuple[bool, List[str]]:
    """🐬 Validate MySQL syntax without normalization
    
    Args:
        sql: SQL query to validate
    
    Returns:
        Tuple of (is_valid, error_list)
    
    Usage:
        valid, errors = validate_mysql_syntax("SELECT * FROM users")
    """
    normalizer = MySQLCompatibleNormalizer()
    return normalizer._validate_mysql_syntax(sql)

# 🎯 Export key functions for external use
__all__ = [
    'MySQLCompatibleNormalizer',
    'normalize_sql_query',
    'get_normalization_rules', 
    'validate_mysql_syntax',
    'NormalizationRule'
]
