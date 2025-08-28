#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SQL Parser 包装器模块

提供简单易用的接口来使用 sql-parser-final-patch-v5-4.py
"""

import importlib.util
import json
import os

class SQLParserWrapper:
    """SQL解析器包装器"""

    def __init__(self, parser_file="sql-parser-final-patch-v5-4.py"):
        """初始化SQL解析器"""
        if not os.path.exists(parser_file):
            raise FileNotFoundError(f"找不到解析器文件: {parser_file}")

        spec = importlib.util.spec_from_file_location("sql_parser", parser_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        self.parser = module.SQLSplitParser()
        self.version = getattr(self.parser, 'version', 'unknown')

    def parse(self, sql):
        """解析SQL并返回完整结果"""
        return self.parser.parse(sql)

    def parse_to_json(self, sql, indent=2):
        """解析SQL并返回JSON字符串"""
        return self.parser.parse_to_json(sql, indent)

    def get_tables(self, sql):
        """只获取表格列表"""
        result = self.parse(sql)
        return result.get('tables', []) if result['success'] else []

    def get_joins(self, sql):
        """只获取JOIN信息"""
        result = self.parse(sql)
        return result.get('joins', []) if result['success'] else []

    def get_fields(self, sql):
        """只获取字段信息"""
        result = self.parse(sql)
        return result.get('fields', []) if result['success'] else []

    def get_where_conditions(self, sql):
        """只获取WHERE条件"""
        result = self.parse(sql)
        return result.get('whereConditions', []) if result['success'] else []

    def validate_sql(self, sql):
        """验证SQL是否可以解析"""
        result = self.parse(sql)
        return result['success'], result.get('error', None)

    def get_summary(self, sql):
        """获取SQL解析摘要"""
        result = self.parse(sql)

        if not result['success']:
            return {"error": result.get('error'), "success": False}

        return {
            "success": True,
            "tables_count": len(result['tables']),
            "fields_count": len(result['fields']),
            "joins_count": len(result['joins']),
            "where_conditions_count": len(result['whereConditions']),
            "tables": result['tables'],
            "join_types": [join['type'] for join in result['joins']]
        }

# 便捷函数
def create_parser(parser_file="sql-parser-final-patch-v5-4.py"):
    """创建解析器实例"""
    return SQLParserWrapper(parser_file)

def quick_parse(sql, parser_file="sql-parser-final-patch-v5-4.py"):
    """快速解析SQL"""
    parser = SQLParserWrapper(parser_file)
    return parser.parse(sql)

def get_tables_from_sql(sql, parser_file="sql-parser-final-patch-v5-4.py"):
    """从SQL中快速提取表格"""
    parser = SQLParserWrapper(parser_file)
    return parser.get_tables(sql)

# 使用示例
if __name__ == "__main__":
    print("🎯 SQL Parser 包装器测试")
    print("=" * 40)

    try:
        # 创建解析器
        parser = SQLParserWrapper()
        print(f"✅ SQL Parser 版本: {parser.version}")

        # 测试SQL
        test_sql = """SELECT `u`.`name`, COUNT(`o`.`id`) AS `order_count`
                      FROM `users` `u`
                      LEFT JOIN `orders` `o` ON `u`.`id` = `o`.`user_id`
                      GROUP BY `u`.`name`"""

        print("\n📋 测试SQL解析:")
        print(test_sql[:50] + "...")

        # 获取摘要
        summary = parser.get_summary(test_sql)

        if summary['success']:
            print("\n✅ 解析摘要:")
            print(f"  📋 表格数量: {summary['tables_count']}")
            print(f"  📄 字段数量: {summary['fields_count']}")
            print(f"  🔗 JOIN数量: {summary['joins_count']}")
            print(f"  🔍 WHERE条件: {summary['where_conditions_count']}")
            print(f"  📋 涉及表格: {', '.join(summary['tables'])}")
            if summary['join_types']:
                print(f"  🔗 JOIN类型: {', '.join(summary['join_types'])}")
        else:
            print(f"❌ 解析失败: {summary['error']}")

        print("\n🎊 测试完成!")

    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        print("💡 请确保 sql-parser-final-patch-v5-4.py 文件存在")
