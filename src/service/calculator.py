"""表达式计算服务：词法分析 + 递归下降解析求值。

全程不使用 eval/exec 等任意代码执行方式，
用户输入只会被当作数学表达式文本进行解析与求值。

支持的文法（优先级从低到高）：
    expression := term (('+' | '-') term)*
    term       := factor (('*' | '/' | '%') factor)*
    factor     := ('+' | '-') factor | power          # 一元正负号
    power      := primary ('^' factor)?               # 幂，右结合
    primary    := NUMBER | '(' expression ')'
               | 'sqrt' '(' expression ')'
"""

import math
import re

from exceptions import DivisionByZeroError, InvalidExpressionError

# 数字 / sqrt 关键字 / 运算符与括号；忽略空白
_TOKEN_RE = re.compile(
    r"\s*(?:(?P<number>\d+(?:\.\d+)?)|(?P<sqrt>sqrt)|(?P<op>[+\-*/%^()]))",
    re.IGNORECASE,
)


def evaluate(expression):
    """计算表达式字符串，返回 int 或 float 类型的结果。

    解析或求值失败时抛出 InvalidExpressionError / DivisionByZeroError。
    """
    if not isinstance(expression, str) or not expression.strip():
        raise InvalidExpressionError("表达式不能为空")
    tokens = _tokenize(expression)
    result = _Parser(tokens).parse()
    return _normalize(result)


def _tokenize(expression):
    """把表达式字符串切分为 (类型, 值) 记号序列。"""
    tokens = []
    pos = 0
    while pos < len(expression):
        match = _TOKEN_RE.match(expression, pos)
        if match is None:
            rest = expression[pos:].strip()
            if not rest:  # 只剩空白，正常结束
                break
            raise InvalidExpressionError(f"表达式包含非法字符: {rest[0]!r}")
        pos = match.end()
        if match.group("number") is not None:
            tokens.append(("number", float(match.group("number"))))
        elif match.group("sqrt") is not None:
            tokens.append(("sqrt", "sqrt"))
        else:
            tokens.append(("op", match.group("op")))
    return tokens


class _Parser:
    """递归下降解析器：一条文法规则对应一个方法。"""

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def parse(self):
        """入口：解析整个表达式，不允许有剩余记号。"""
        if not self.tokens:
            raise InvalidExpressionError("表达式不能为空")
        value = self._expression()
        if self.pos < len(self.tokens):
            raise InvalidExpressionError("表达式存在多余或错配的内容")
        return value

    # -- 以下方法与文法规则一一对应 ----------------------------------

    def _expression(self):
        value = self._term()
        while self._peek_op() in ("+", "-"):
            op = self._next()[1]
            right = self._term()
            value = value + right if op == "+" else value - right
        return value

    def _term(self):
        value = self._factor()
        while self._peek_op() in ("*", "/", "%"):
            op = self._next()[1]
            right = self._factor()
            if op == "*":
                value = value * right
            elif right == 0:
                raise DivisionByZeroError("除数不能为零")
            else:
                value = value / right if op == "/" else value % right
        return value

    def _factor(self):
        if self._peek_op() in ("+", "-"):
            op = self._next()[1]
            value = self._factor()
            return -value if op == "-" else value
        return self._power()

    def _power(self):
        base = self._primary()
        if self._peek_op() == "^":
            self._next()
            exponent = self._factor()  # 右结合，且允许 2^-3
            return self._safe_pow(base, exponent)
        return base

    def _primary(self):
        if self.pos >= len(self.tokens):
            raise InvalidExpressionError("表达式不完整")
        kind, value = self.tokens[self.pos]
        if kind == "number":
            self._next()
            return value
        if kind == "op" and value == "(":
            self._next()
            inner = self._expression()
            self._expect_close_paren()
            return inner
        if kind == "sqrt":
            self._next()
            if self._peek_op() != "(":
                raise InvalidExpressionError("sqrt 之后必须紧跟左括号")
            self._next()
            inner = self._expression()
            self._expect_close_paren()
            if inner < 0:
                raise InvalidExpressionError("sqrt 的参数不能为负数")
            return math.sqrt(inner)
        raise InvalidExpressionError("表达式语法不正确")

    # -- 工具方法 -----------------------------------------------------

    def _next(self):
        token = self.tokens[self.pos]
        self.pos += 1
        return token

    def _peek_op(self):
        """查看当前记号，若是运算符/括号则返回其值，否则返回 None。"""
        if self.pos < len(self.tokens):
            kind, value = self.tokens[self.pos]
            if kind == "op":
                return value
        return None

    def _expect_close_paren(self):
        if self._peek_op() != ")":
            raise InvalidExpressionError("括号不匹配")
        self._next()

    @staticmethod
    def _safe_pow(base, exponent):
        try:
            return base ** exponent
        except ZeroDivisionError as exc:  # 0 的负次幂
            raise DivisionByZeroError("除数不能为零") from exc
        except (OverflowError, ValueError) as exc:
            raise InvalidExpressionError("幂运算结果超出可表示范围") from exc


def _normalize(value):
    """清理浮点运算误差，并统一结果的显示形式。

    0.30000000000000004 -> 0.3；2.0 -> 2；无穷大/NaN 视为结果超出范围。
    """
    if isinstance(value, float):
        if math.isinf(value) or math.isnan(value):
            raise InvalidExpressionError("计算结果超出可表示范围")
        value = round(value, 12)
        if value.is_integer():
            return int(value)
    return value
