"""
AST Node Definitions - SQL Parser AST v6.0

🏗️ Core AST node classes for SQL structure representation

Author: AI Assistant
Version: 6.0 AST Modular
Date: 2025-08-26
Status: ✅ Core AST node definitions for 100% expect.md compliance
"""

from typing import List, Dict, Any, Optional

class ASTNode:
    """Base AST node class"""
    def __init__(self, node_type: str, value: Any = None):
        self.node_type = node_type
        self.value = value
        self.children = []
        self.parent = None
        self.attributes = {}

    def add_child(self, child):
        """Add child node"""
        child.parent = self
        self.children.append(child)

    def get_attribute(self, key: str, default=None):
        """Get node attribute"""
        return self.attributes.get(key, default)

    def set_attribute(self, key: str, value: Any):
        """Set node attribute"""
        self.attributes[key] = value

    def find_children_by_type(self, node_type: str) -> List['ASTNode']:
        """Find all children of specific type"""
        return [child for child in self.children if child.node_type == node_type]

    def find_first_child_by_type(self, node_type: str) -> Optional['ASTNode']:
        """Find first child of specific type"""
        for child in self.children:
            if child.node_type == node_type:
                return child
        return None

    def __repr__(self):
        return f"{self.node_type}({self.value})"

class SelectNode(ASTNode):
    """SELECT statement node"""
    def __init__(self):
        super().__init__("SELECT")
        self.fields = []
        self.distinct = False

    def add_field(self, field_node):
        """Add field to SELECT"""
        self.fields.append(field_node)
        self.add_child(field_node)

class FieldNode(ASTNode):
    """Field/Column node"""
    def __init__(self, expression: str, alias: str = None, table: str = None):
        super().__init__("FIELD")
        self.expression = expression
        self.alias = alias
        self.table = table
        self.is_function = "(" in expression
        self.is_aggregated = any(func in expression.upper() for func in ['COUNT', 'SUM', 'AVG', 'MAX', 'MIN'])

class FromNode(ASTNode):
    """FROM clause node"""
    def __init__(self):
        super().__init__("FROM")
        self.table_references = []

    def add_table_reference(self, table_ref):
        """Add table reference"""
        self.table_references.append(table_ref)
        self.add_child(table_ref)

class TableReferenceNode(ASTNode):
    """Table reference node (table name + alias)"""
    def __init__(self, table_name: str, alias: str = None, schema: str = None):
        super().__init__("TABLE_REFERENCE")
        self.table_name = table_name
        self.alias = alias
        self.schema = schema

class JoinNode(ASTNode):
    """JOIN node"""
    def __init__(self, join_type: str, table_ref: TableReferenceNode, condition: 'ConditionNode'):
        super().__init__("JOIN")
        self.join_type = join_type.upper()  # INNER, LEFT, RIGHT, FULL
        self.table_reference = table_ref
        self.condition = condition
        self.add_child(table_ref)
        self.add_child(condition)

class ConditionNode(ASTNode):
    """Condition node (ON clause, WHERE clause)"""
    def __init__(self, condition_text: str):
        super().__init__("CONDITION")
        self.condition_text = condition_text
        self.left_table = None
        self.left_field = None
        self.right_table = None
        self.right_field = None
        self.operator = "="  # Default to equality

    def set_join_fields(self, left_table: str, left_field: str, right_table: str, right_field: str):
        """Set JOIN field information"""
        self.left_table = left_table
        self.left_field = left_field
        self.right_table = right_table
        self.right_field = right_field

class WhereNode(ASTNode):
    """WHERE clause node"""
    def __init__(self):
        super().__init__("WHERE")
        self.conditions = []

    def add_condition(self, condition: ConditionNode):
        """Add condition to WHERE"""
        self.conditions.append(condition)
        self.add_child(condition)

class GroupByNode(ASTNode):
    """GROUP BY clause node"""
    def __init__(self):
        super().__init__("GROUP_BY")
        self.fields = []

    def add_field(self, field: str):
        """Add field to GROUP BY"""
        self.fields.append(field)

class OrderByNode(ASTNode):
    """ORDER BY clause node"""
    def __init__(self):
        super().__init__("ORDER_BY")
        self.fields = []

class CTENode(ASTNode):
    """CTE (Common Table Expression) node"""
    def __init__(self, name: str, query_node: 'QueryNode', recursive: bool = False):
        super().__init__("CTE")
        self.name = name
        self.query_node = query_node
        self.recursive = recursive
        self.add_child(query_node)

class WithNode(ASTNode):
    """WITH clause node"""
    def __init__(self):
        super().__init__("WITH")
        self.ctes = []

    def add_cte(self, cte: CTENode):
        """Add CTE to WITH clause"""
        self.ctes.append(cte)
        self.add_child(cte)

class QueryNode(ASTNode):
    """Complete query node (can contain subqueries)"""
    def __init__(self):
        super().__init__("QUERY")
        self.with_clause = None
        self.select_clause = None
        self.from_clause = None
        self.where_clause = None
        self.group_by_clause = None
        self.order_by_clause = None
        self.joins = []

    def set_with_clause(self, with_clause: WithNode):
        """Set WITH clause"""
        self.with_clause = with_clause
        self.add_child(with_clause)

    def set_select_clause(self, select_clause: SelectNode):
        """Set SELECT clause"""
        self.select_clause = select_clause
        self.add_child(select_clause)

    def set_from_clause(self, from_clause: FromNode):
        """Set FROM clause"""
        self.from_clause = from_clause
        self.add_child(from_clause)

    def set_where_clause(self, where_clause: WhereNode):
        """Set WHERE clause"""
        self.where_clause = where_clause
        self.add_child(where_clause)

    def add_join(self, join: JoinNode):
        """Add JOIN to query"""
        self.joins.append(join)
        self.add_child(join)

    def set_group_by_clause(self, group_by: GroupByNode):
        """Set GROUP BY clause"""
        self.group_by_clause = group_by
        self.add_child(group_by)

class SubqueryNode(ASTNode):
    """Subquery node"""
    def __init__(self, query: QueryNode, alias: str = None):
        super().__init__("SUBQUERY")
        self.query = query
        self.alias = alias
        self.add_child(query)

# Factory functions for easy node creation
def create_field_node(expression: str, alias: str = None, table: str = None) -> FieldNode:
    """Create field node with automatic table detection"""
    # Extract table from expression like `table`.`field`
    if '.' in expression and not table:
        parts = expression.split('.', 1)
        if len(parts) == 2:
            table = parts[0].strip('`')
    
    return FieldNode(expression, alias, table)

def create_table_reference(table_name: str, alias: str = None) -> TableReferenceNode:
    """Create table reference node"""
    return TableReferenceNode(table_name.strip('`'), alias.strip('`') if alias else None)

def create_join_condition(condition_text: str) -> ConditionNode:
    """🚀 ENHANCED: Create join condition with support for both backtick and backtick-free SQL"""
    condition = ConditionNode(condition_text)
    
    import re
    
    # 🎯 Pattern 1: Backtick format - `table1`.`field1` = `table2`.`field2`
    backtick_match = re.search(r'`([^`]+)`\.`([^`]+)`\s*=\s*`([^`]+)`\.`([^`]+)`', condition_text)
    if backtick_match:
        condition.set_join_fields(
            backtick_match.group(1), backtick_match.group(2),
            backtick_match.group(3), backtick_match.group(4)
        )
        return condition
    
    # 🎯 Pattern 2: Backtick-free format - table1.field1 = table2.field2 (normalized SQL)
    normal_match = re.search(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\\.([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*([a-zA-Z_][a-zA-Z0-9_]*)\\.([a-zA-Z_][a-zA-Z0-9_]*)\b', condition_text)
    if normal_match:
        condition.set_join_fields(
            normal_match.group(1), normal_match.group(2),
            normal_match.group(3), normal_match.group(4)
        )
        return condition
    
    # 🎯 Pattern 3: Database-prefixed format - db.table1.field1 = db.table2.field2
    db_match = re.search(r'\b[a-zA-Z_][a-zA-Z0-9_]*\\.([a-zA-Z_][a-zA-Z0-9_]*)\\.([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*[a-zA-Z_][a-zA-Z0-9_]*\\.([a-zA-Z_][a-zA-Z0-9_]*)\\.([a-zA-Z_][a-zA-Z0-9_]*)\b', condition_text)
    if db_match:
        condition.set_join_fields(
            db_match.group(1), db_match.group(2),
            db_match.group(3), db_match.group(4)
        )
        return condition
    
    return condition

# Node type constants
NODE_TYPES = {
    'QUERY': 'QUERY',
    'SELECT': 'SELECT', 
    'FROM': 'FROM',
    'WHERE': 'WHERE',
    'JOIN': 'JOIN',
    'FIELD': 'FIELD',
    'TABLE_REFERENCE': 'TABLE_REFERENCE',
    'CONDITION': 'CONDITION',
    'CTE': 'CTE',
    'WITH': 'WITH',
    'SUBQUERY': 'SUBQUERY',
    'GROUP_BY': 'GROUP_BY',
    'ORDER_BY': 'ORDER_BY'
}

if __name__ == "__main__":
    print("🏗️ AST Node Definitions - SQL Parser AST v6.0")
    print("=" * 60)
    print("✅ Core AST node classes loaded")
    print(f"✅ {len(NODE_TYPES)} node types defined")
    print("✅ Factory functions available")
    print("\n🎯 Ready for AST parser integration!")
