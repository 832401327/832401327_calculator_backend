"""自定义异常：用于区分用户输入错误与服务器内部错误。"""


class CalculatorError(Exception):
    """计算器业务异常基类。"""


class InvalidExpressionError(CalculatorError):
    """表达式非法（空表达式、非法字符、语法错误等）。"""


class DivisionByZeroError(CalculatorError):
    """除数为零（除法或取模）。"""
