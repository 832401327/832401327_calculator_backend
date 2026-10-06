"""计算历史记录实体：对应数据库表 calculation_history 的一行。"""


class CalculationHistory:
    """一条计算记录（表达式、结果、时间）。"""

    def __init__(self, record_id, expression, result, created_at):
        self.id = record_id
        self.expression = expression
        self.result = result
        self.created_at = created_at

    @classmethod
    def from_row(cls, row):
        """从数据库查询行构造实体。"""
        return cls(row["id"], row["expression"], row["result"], row["created_at"])

    def to_dict(self):
        """转为 API 响应字典，结果统一转为数字类型。"""
        return {
            "id": self.id,
            "expression": self.expression,
            "result": _to_number(self.result),
            "created_at": self.created_at,
        }


def _to_number(value):
    """把存储层的结果字符串还原为 int/float，便于前端直接展示。"""
    try:
        number = float(value)
        return int(number) if number.is_integer() else number
    except (TypeError, ValueError):
        return value
