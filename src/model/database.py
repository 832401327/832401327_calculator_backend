"""SQLite 数据库访问层：负责连接管理与建表初始化。

数据库文件默认位于项目根目录 data/calculator.db，
可通过环境变量 CALCULATOR_DB_PATH 覆盖。
"""

import os
import sqlite3

# src/model/database.py -> 上溯两级得到项目根目录
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.environ.get(
    "CALCULATOR_DB_PATH", os.path.join(DATA_DIR, "calculator.db")
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS calculation_history (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    expression  TEXT    NOT NULL,
    result      TEXT    NOT NULL,
    created_at  TEXT    NOT NULL
);
"""


def connect():
    """返回一个新的数据库连接（调用方负责关闭）。"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库：确保目录与表结构存在（幂等，可重复执行）。"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()
