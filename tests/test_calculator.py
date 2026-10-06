"""calculator.evaluate 的单元测试：覆盖四则、优先级、括号、
一元符号、小数、幂、取模、sqrt 以及各类非法输入。
"""

import os
import sys

import pytest

# 把 src 目录加入模块搜索路径，便于测试直接导入业务代码
sys.path.insert(
    0,
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"),
)

from exceptions import DivisionByZeroError, InvalidExpressionError  # noqa: E402
from service.calculator import evaluate  # noqa: E402


class TestBasicCalculation:
    """功能 1：基础四则运算。"""

    def test_addition(self):
        assert evaluate("12+8") == 20

    def test_subtraction(self):
        assert evaluate("10-4") == 6

    def test_multiplication(self):
        assert evaluate("6*7") == 42

    def test_division(self):
        assert evaluate("10/4") == 2.5

    def test_spaces_ignored(self):
        assert evaluate(" 12 + 8 ") == 20


class TestCompoundExpression:
    """功能 2：复合表达式与数学规则。"""

    def test_operator_precedence(self):
        assert evaluate("1+2*3") == 7

    def test_parentheses(self):
        assert evaluate("(1+2)*3") == 9

    def test_mixed_operations(self):
        assert evaluate("10/2+7") == 12

    def test_unary_minus_at_start(self):
        assert evaluate("-5+8") == 3

    def test_unary_minus_after_operator(self):
        assert evaluate("3*-2") == -6

    def test_double_unary(self):
        assert evaluate("--5") == 5

    def test_decimal_float_error_cleanup(self):
        assert evaluate("0.1+0.2") == 0.3

    def test_nested_parentheses(self):
        assert evaluate("((2+3))*4") == 20

    def test_power_right_associative(self):
        assert evaluate("2^3^2") == 512

    def test_power_binds_tighter_than_unary_minus(self):
        assert evaluate("-2^2") == -4

    def test_power_with_negative_exponent(self):
        assert evaluate("2^-2") == 0.25

    def test_sqrt(self):
        assert evaluate("sqrt(16)+1") == 5

    def test_sqrt_approx(self):
        assert evaluate("sqrt(2)") == pytest.approx(2 ** 0.5)

    def test_modulo(self):
        assert evaluate("10%3") == 1


class TestErrorHandling:
    """异常场景：除零与非法表达式。"""

    def test_division_by_zero(self):
        with pytest.raises(DivisionByZeroError):
            evaluate("1/0")

    def test_modulo_by_zero(self):
        with pytest.raises(DivisionByZeroError):
            evaluate("5%0")

    def test_zero_negative_power(self):
        with pytest.raises(DivisionByZeroError):
            evaluate("0^-1")

    def test_invalid_character(self):
        with pytest.raises(InvalidExpressionError):
            evaluate("1+a")

    def test_missing_right_paren(self):
        with pytest.raises(InvalidExpressionError):
            evaluate("(1+2")

    def test_extra_token(self):
        with pytest.raises(InvalidExpressionError):
            evaluate("1+2)")

    def test_empty_expression(self):
        with pytest.raises(InvalidExpressionError):
            evaluate("   ")

    def test_incomplete_expression(self):
        with pytest.raises(InvalidExpressionError):
            evaluate("1+")

    def test_two_adjacent_numbers(self):
        with pytest.raises(InvalidExpressionError):
            evaluate("1 2")

    def test_sqrt_negative(self):
        with pytest.raises(InvalidExpressionError):
            evaluate("sqrt(-1)")
