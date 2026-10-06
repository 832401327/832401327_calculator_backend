# Python 代码规范（codestyle.md）

> 本规范来源：**PEP 8 —— The Style Guide for Python Code**（Python 官方风格指南），
> 参考链接：<https://peps.python.org/pep-0008/>。
> 本项目后端代码遵循以下从 PEP 8 中选取并补充的具体规则。

## 1. 缩进与空格

- 统一使用 **4 个空格** 缩进，禁止使用 Tab。
- 运算符两侧、逗号后各留一个空格：`value = a + b`、`f(a, b)`。
- 括号内侧不贴空格：`func(x)` 而不是 `func( x )`。

```python
# 正确
result = base ** exponent

# 错误
result=base**exponent
```

## 2. 行长度

- 每行不超过 **79 个字符**（本项目按 PEP 8 建议执行）。
- 过长的表达式用括号隐式续行，不使用反斜杠。

```python
# 正确
DB_PATH = os.environ.get(
    "CALCULATOR_DB_PATH", os.path.join(DATA_DIR, "calculator.db")
)
```

## 3. 命名规范

| 对象 | 风格 | 示例 |
|---|---|---|
| 模块 / 文件名 | 小写下划线 | `history_service.py` |
| 函数 / 方法 | 小写下划线 | `list_history()` |
| 类 | 大驼峰 | `CalculationHistory` |
| 常量 | 全大写下划线 | `DB_PATH`、`SCHEMA` |
| 私有成员 | 前置单下划线 | `_Parser`、`_normalize()` |

## 4. 导入顺序

按「标准库 → 第三方库 → 本地模块」分组，组间空一行，按字母序排列：

```python
import math
import re

from flask import Blueprint, jsonify

from exceptions import CalculatorError
```

## 5. 文档字符串与注释

- 每个模块、类、公开函数必须有 docstring，说明用途、参数与异常。
- 注释解释"为什么"，而不是复述代码。
- 使用中文注释便于团队阅读，中英文均可，但需保持一致。

## 6. 异常规范

- 项目内只抛出 `src/exceptions.py` 中定义的业务异常，
  不静默吞掉异常；必要时使用 `raise ... from exc` 保留原因链。
- 控制器层统一捕获 `CalculatorError` 并返回标准 JSON 错误响应。

```python
except ZeroDivisionError as exc:
    raise DivisionByZeroError("除数不能为零") from exc
```

## 7. Flask 路由规范

- 一个蓝图专注一个资源（本项目中 `api_bp` 聚合 `/api` 前缀的所有路由）。
- 视图函数保持"校验 → 调用服务 → 返回响应"三段式，不写业务逻辑。
- 所有响应返回统一的 JSON 结构：`{"success": ..., ...}`，并使用
  准确的 HTTP 状态码（200 / 204 / 400 / 404 / 500）。

## 8. 工具建议

- 提交前可用 `flake8` 或 `ruff check` 自查：
  `ruff check src tests --line-length 79`
