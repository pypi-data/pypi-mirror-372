"""
SQL Tokenizer - SQL Parser AST v6.0

🔪 Advanced SQL tokenization with context awareness

Author: AI Assistant
Version: 6.0 AST Modular  
Date: 2025-08-26
Status: ✅ Context-aware SQL tokenization for AST parsing
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class TokenType(Enum):
    """SQL token types"""
    KEYWORD = "KEYWORD"
    IDENTIFIER = "IDENTIFIER"
    QUOTED_IDENTIFIER = "QUOTED_IDENTIFIER"
    STRING_LITERAL = "STRING_LITERAL"
    NUMBER = "NUMBER"
    OPERATOR = "OPERATOR"
    PUNCTUATION = "PUNCTUATION"
    WHITESPACE = "WHITESPACE"
    COMMENT = "COMMENT"
    FUNCTION = "FUNCTION"
    PAREN_OPEN = "PAREN_OPEN"
    PAREN_CLOSE = "PAREN_CLOSE"
    COMMA = "COMMA"

@dataclass
class Token:
    """SQL token with position and context"""
    type: TokenType
    value: str
    position: int
    line: int
    column: int
    context: str = ""

    def __repr__(self):
        return f"Token({self.type.name}, '{self.value}', {self.position})"

class SQLTokenizer:
    """Advanced SQL tokenizer with context awareness"""

    # SQL Keywords (MySQL specific)
    KEYWORDS = {
        'SELECT', 'FROM', 'WHERE', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL', 'OUTER',
        'ON', 'AS', 'AND', 'OR', 'NOT', 'IN', 'BETWEEN', 'LIKE', 'IS', 'NULL',
        'GROUP', 'BY', 'ORDER', 'HAVING', 'LIMIT', 'UNION', 'ALL', 'DISTINCT',
        'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER', 'TABLE', 'INDEX',
        'WITH', 'RECURSIVE', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'IF',
        'EXISTS', 'OVER', 'PARTITION', 'WINDOW', 'ROW_NUMBER', 'RANK', 'DENSE_RANK'
    }

    # SQL Functions (MySQL specific)
    FUNCTIONS = {
        'COUNT', 'SUM', 'AVG', 'MAX', 'MIN', 'CONCAT', 'LENGTH', 'SUBSTRING',
        'DATE_FORMAT', 'NOW', 'CURDATE', 'CURTIME', 'YEAR', 'MONTH', 'DAY',
        'UPPER', 'LOWER', 'TRIM', 'COALESCE', 'IFNULL', 'CAST', 'CONVERT'
    }

    # SQL Operators
    OPERATORS = {
        '=', '!=', '<>', '<', '>', '<=', '>=', '+', '-', '*', '/', '%',
        'AND', 'OR', 'NOT', 'LIKE', 'IN', 'BETWEEN', 'IS', 'EXISTS'
    }

    def __init__(self):
        self.tokens = []
        self.position = 0
        self.line = 1
        self.column = 1

    def tokenize(self, sql: str) -> List[Token]:
        """Tokenize SQL string into tokens"""
        self.tokens = []
        self.position = 0
        self.line = 1
        self.column = 1

        sql = self._normalize_sql(sql)
        i = 0

        while i < len(sql):
            char = sql[i]

            # Skip whitespace but track position
            if char.isspace():
                if char == '\n':
                    self.line += 1
                    self.column = 1
                else:
                    self.column += 1
                i += 1
                continue

            # Handle comments
            if char == '-' and i + 1 < len(sql) and sql[i + 1] == '-':
                comment_start = i
                while i < len(sql) and sql[i] != '\n':
                    i += 1
                self._add_token(TokenType.COMMENT, sql[comment_start:i], comment_start)
                continue

            # Handle multi-line comments
            if char == '/' and i + 1 < len(sql) and sql[i + 1] == '*':
                comment_start = i
                i += 2
                while i + 1 < len(sql) and not (sql[i] == '*' and sql[i + 1] == '/'):
                    if sql[i] == '\n':
                        self.line += 1
                        self.column = 1
                    i += 1
                i += 2  # Skip closing */
                self._add_token(TokenType.COMMENT, sql[comment_start:i], comment_start)
                continue

            # Handle quoted identifiers (backticks)
            if char == '`':
                quoted_start = i
                i += 1
                while i < len(sql) and sql[i] != '`':
                    i += 1
                i += 1  # Skip closing backtick
                self._add_token(TokenType.QUOTED_IDENTIFIER, sql[quoted_start:i], quoted_start)
                continue

            # Handle string literals
            if char in ('"', "'"):
                string_start = i
                quote_char = char
                i += 1
                while i < len(sql):
                    if sql[i] == quote_char:
                        if i + 1 < len(sql) and sql[i + 1] == quote_char:
                            i += 2  # Escaped quote
                            continue
                        else:
                            i += 1  # End of string
                            break
                    i += 1
                self._add_token(TokenType.STRING_LITERAL, sql[string_start:i], string_start)
                continue

            # Handle numbers
            if char.isdigit():
                num_start = i
                while i < len(sql) and (sql[i].isdigit() or sql[i] == '.'):
                    i += 1
                self._add_token(TokenType.NUMBER, sql[num_start:i], num_start)
                continue

            # Handle parentheses
            if char == '(':
                self._add_token(TokenType.PAREN_OPEN, char, i)
                i += 1
                continue

            if char == ')':
                self._add_token(TokenType.PAREN_CLOSE, char, i)
                i += 1
                continue

            # Handle comma
            if char == ',':
                self._add_token(TokenType.COMMA, char, i)
                i += 1
                continue

            # Handle operators and punctuation
            if char in '=!<>+-*/%':
                op_start = i
                # Handle multi-character operators
                if char in '=!<>' and i + 1 < len(sql) and sql[i + 1] in '=<>':
                    i += 2
                else:
                    i += 1
                operator = sql[op_start:i]
                self._add_token(TokenType.OPERATOR, operator, op_start)
                continue

            # Handle other punctuation
            if char in '.,;':
                self._add_token(TokenType.PUNCTUATION, char, i)
                i += 1
                continue

            # Handle identifiers and keywords
            if char.isalpha() or char == '_':
                ident_start = i
                while i < len(sql) and (sql[i].isalnum() or sql[i] == '_'):
                    i += 1
                
                identifier = sql[ident_start:i].upper()
                
                # Check if it's followed by parentheses (function)
                next_non_space = self._skip_whitespace(sql, i)
                if next_non_space < len(sql) and sql[next_non_space] == '(':
                    if identifier in self.FUNCTIONS:
                        self._add_token(TokenType.FUNCTION, identifier, ident_start)
                    else:
                        self._add_token(TokenType.IDENTIFIER, sql[ident_start:i], ident_start)
                # Check if it's a keyword
                elif identifier in self.KEYWORDS:
                    self._add_token(TokenType.KEYWORD, identifier, ident_start)
                # Regular identifier
                else:
                    self._add_token(TokenType.IDENTIFIER, sql[ident_start:i], ident_start)
                continue

            # Unknown character - treat as punctuation
            self._add_token(TokenType.PUNCTUATION, char, i)
            i += 1

        return self.tokens

    def _normalize_sql(self, sql: str) -> str:
        """Normalize SQL for tokenization"""
        sql = sql.strip()
        # Replace HTML entities
        sql = sql.replace('&lt;', '<').replace('&gt;', '>')
        return sql

    def _skip_whitespace(self, sql: str, start: int) -> int:
        """Skip whitespace and return next non-space position"""
        i = start
        while i < len(sql) and sql[i].isspace():
            i += 1
        return i

    def _add_token(self, token_type: TokenType, value: str, position: int):
        """Add token to list"""
        token = Token(
            type=token_type,
            value=value,
            position=position,
            line=self.line,
            column=self.column
        )
        self.tokens.append(token)
        self.column += len(value)

    def get_tokens_by_type(self, token_type: TokenType) -> List[Token]:
        """Get all tokens of specific type"""
        return [token for token in self.tokens if token.type == token_type]

    def get_keywords(self) -> List[Token]:
        """Get all keyword tokens"""
        return self.get_tokens_by_type(TokenType.KEYWORD)

    def get_identifiers(self) -> List[Token]:
        """Get all identifier tokens"""
        return self.get_tokens_by_type(TokenType.IDENTIFIER)

    def get_quoted_identifiers(self) -> List[Token]:
        """Get all quoted identifier tokens"""
        return self.get_tokens_by_type(TokenType.QUOTED_IDENTIFIER)

    def get_functions(self) -> List[Token]:
        """Get all function tokens"""
        return self.get_tokens_by_type(TokenType.FUNCTION)

    def find_keyword_positions(self, keyword: str) -> List[int]:
        """Find positions of specific keyword"""
        positions = []
        for token in self.tokens:
            if token.type == TokenType.KEYWORD and token.value.upper() == keyword.upper():
                positions.append(token.position)
        return positions

    def get_context_around_token(self, token_index: int, context_size: int = 5) -> List[Token]:
        """Get context tokens around specified token"""
        start = max(0, token_index - context_size)
        end = min(len(self.tokens), token_index + context_size + 1)
        return self.tokens[start:end]

    def tokens_to_string(self, start_index: int = 0, end_index: int = None) -> str:
        """Convert tokens back to string"""
        if end_index is None:
            end_index = len(self.tokens)
        
        result = ""
        for i in range(start_index, min(end_index, len(self.tokens))):
            token = self.tokens[i]
            if token.type != TokenType.WHITESPACE:
                if result and not result.endswith('(') and token.value != ',' and token.value != ')':
                    result += " "
                result += token.value
        
        return result

class TokenStream:
    """Token stream for easy parsing"""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = [t for t in tokens if t.type != TokenType.WHITESPACE and t.type != TokenType.COMMENT]
        self.position = 0

    def current(self) -> Optional[Token]:
        """Get current token"""
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None

    def peek(self, offset: int = 1) -> Optional[Token]:
        """Peek ahead at token"""
        pos = self.position + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None

    def advance(self) -> Optional[Token]:
        """Advance to next token and return current"""
        token = self.current()
        self.position += 1
        return token

    def consume(self, expected_value: str = None, expected_type: TokenType = None) -> Optional[Token]:
        """Consume token with optional validation"""
        token = self.current()
        if not token:
            return None
            
        if expected_value and token.value.upper() != expected_value.upper():
            return None
            
        if expected_type and token.type != expected_type:
            return None
            
        self.position += 1
        return token

    def match(self, *values: str) -> bool:
        """Check if current token matches any of the values"""
        token = self.current()
        if not token:
            return False
        return token.value.upper() in [v.upper() for v in values]

    def has_more(self) -> bool:
        """Check if more tokens available"""
        return self.position < len(self.tokens)

    def reset(self):
        """Reset stream to beginning"""
        self.position = 0

if __name__ == "__main__":
    print("🔪 SQL Tokenizer - SQL Parser AST v6.0")
    print("=" * 60)
    
    # Test tokenizer
    tokenizer = SQLTokenizer()
    test_sql = "SELECT `table1`.`field1`, COUNT(*) AS `count` FROM `table1` LEFT JOIN `table2` ON `table1`.`id` = `table2`.`table1_id`"
    
    tokens = tokenizer.tokenize(test_sql)
    print(f"✅ Tokenized SQL into {len(tokens)} tokens")
    
    keywords = tokenizer.get_keywords()
    identifiers = tokenizer.get_quoted_identifiers()
    functions = tokenizer.get_functions()
    
    print(f"✅ Found {len(keywords)} keywords")
    print(f"✅ Found {len(identifiers)} quoted identifiers") 
    print(f"✅ Found {len(functions)} functions")
    print("\n🎯 Ready for AST parsing!")
