"""计算历史服务：负责历史的查询、新增、删除（对接数据库层）。"""

import time
from contextlib import closing

from model import database
from model.calculation_history import CalculationHistory


def list_history(search=None):
    """按时间倒序查询历史；search 非空时按表达式关键字模糊过滤。"""
    sql = "SELECT * FROM calculation_history"
    params = []
    if search:
        # 转义 LIKE 通配符，防止用户输入 % 或 _ 影响过滤结果
        escaped = (
            search.replace("\\", "\\\\")
            .replace("%", "\\%")
            .replace("_", "\\_")
        )
        sql += " WHERE expression LIKE ? ESCAPE '\\'"
        params.append(f"%{escaped}%")
    sql += " ORDER BY id DESC"
    with closing(database.connect()) as conn:
        rows = conn.execute(sql, params).fetchall()
    return [CalculationHistory.from_row(row).to_dict() for row in rows]


def add_history(expression, result):
    """插入一条计算记录并返回新记录（含自增 ID 与时间）。"""
    created_at = time.strftime("%Y-%m-%d %H:%M:%S")
    with closing(database.connect()) as conn:
        cursor = conn.execute(
            "INSERT INTO calculation_history (expression, result, created_at)"
            " VALUES (?, ?, ?)",
            (expression, str(result), created_at),
        )
        conn.commit()
        record_id = cursor.lastrowid
    return {
        "id": record_id,
        "expression": expression,
        "result": result,
        "created_at": created_at,
    }


def delete_history(record_id):
    """删除指定 ID 的记录，返回是否确实删除了数据。"""
    with closing(database.connect()) as conn:
        cursor = conn.execute(
            "DELETE FROM calculation_history WHERE id = ?", (record_id,)
        )
        conn.commit()
        return cursor.rowcount > 0


def clear_history():
    """清空全部历史记录，返回被删除的条数。"""
    with closing(database.connect()) as conn:
        cursor = conn.execute("DELETE FROM calculation_history")
        conn.commit()
        return cursor.rowcount
