# 832401327_calculator_backend — 计算器后端服务

前后端分离计算器系统的后端：负责表达式解析与计算、输入校验、异常处理、
计算历史的数据库持久化（增删查），并通过 REST API 与前端通信。

## 技术栈

- Python 3.10+
- Flask 3.x（Web 框架）
- SQLite 3（内置数据库，无需额外安装）
- flask-cors（跨域支持）

## 运行环境

- Windows / Linux / macOS 均可
- Python 3.10 及以上版本

## 安装方法

```bash
# 进入本项目根目录
cd 832401327_calculator_backend

# （可选）创建并激活虚拟环境
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

## 启动方法

```bash
python src/app.py
```

启动后监听 `http://127.0.0.1:5000`（绑定 0.0.0.0，便于部署时被外部访问）。
验证服务是否正常：

```bash
curl http://127.0.0.1:5000/api/health
# {"message": "backend is running", "success": true}
```

## 配置说明

| 配置项 | 默认值 | 说明 |
|---|---|---|
| 监听地址 / 端口 | `0.0.0.0:5000` | 在 `src/app.py` 最后一行修改 |
| 数据库文件路径 | `data/calculator.db`（项目根目录） | 环境变量 `CALCULATOR_DB_PATH` 可覆盖 |
| CORS | 允许所有来源 | `src/app.py` 中 `CORS(app)`，生产环境建议改为指定来源 |

## 数据库初始化

- 服务启动时会自动执行 `init_db()`：自动创建 `data/` 目录和
  `calculation_history` 表（幂等，可重复执行），**无需手动初始化**。
- 如需重置数据：停止服务后删除 `data/calculator.db` 再启动即可。

表结构：

| 字段 | 类型 | 说明 |
|---|---|---|
| id | INTEGER | 主键，自增 |
| expression | TEXT | 计算表达式，如 `(1+2)*3` |
| result | TEXT | 计算结果（存文本以保证整数/小数显示一致） |
| created_at | TEXT | 计算时间 `YYYY-MM-DD HH:MM:SS` |

## API 说明

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/health` | 健康检查 |
| POST | `/api/calculate` | 计算表达式，成功后写入历史 |
| GET | `/api/history` | 查询历史（倒序），可选 `?search=关键字` |
| DELETE | `/api/history/{id}` | 删除单条历史 |
| DELETE | `/api/history` | 清空全部历史（扩展功能） |

请求示例：

```bash
curl -X POST http://127.0.0.1:5000/api/calculate \
  -H "Content-Type: application/json" \
  -d "{\"expression\": \"(1+2)*3\"}"
```

成功响应（HTTP 200）：

```json
{
  "success": true,
  "expression": "(1+2)*3",
  "result": 9,
  "record_id": 1
}
```

失败响应（HTTP 400，如 `1/0` 或非法表达式）：

```json
{
  "success": false,
  "message": "除数不能为零"
}
```

## 前后端联调方式

1. 按上文启动本服务（默认 `http://127.0.0.1:5000`）。
2. 启动前端项目（见前端仓库 README）。
3. 前端 `src/js/api.js` 顶部的 `API_BASE_URL` 需指向本服务地址：
   ```js
   const API_BASE_URL = 'http://127.0.0.1:5000/api';
   ```
4. 本服务已通过 flask-cors 允许跨域访问，前端页面可位于任意来源。

## 项目结构

```
832401327_calculator_backend/
├── src/
│   ├── app.py                  # 应用入口：创建 Flask 应用、注册路由、初始化数据库
│   ├── exceptions.py           # 自定义异常（非法表达式 / 除零）
│   ├── controller/
│   │   └── api.py              # REST 路由：请求校验与标准化 JSON 响应
│   ├── service/
│   │   ├── calculator.py       # 词法分析 + 递归下降解析求值（不使用 eval/exec）
│   │   └── history_service.py  # 历史记录增删查
│   └── model/
│       ├── database.py         # SQLite 连接管理与建表
│       └── calculation_history.py  # 计算历史实体
├── tests/
│   └── test_calculator.py      # 解析器单元测试
├── requirements.txt
├── README.md
└── codestyle.md
```

## 运行测试

```bash
pip install pytest
pytest tests/ -v
```

## 代码规范

见 [codestyle.md](codestyle.md)，基于 PEP 8 制定。
