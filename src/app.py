"""应用入口：创建 Flask 应用、注册蓝图与全局错误处理、初始化数据库。

启动方式（在项目根目录执行）：
    python src/app.py
默认监听 http://127.0.0.1:5000，供前端通过 HTTP API 访问。
"""

import logging

from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from controller.api import api_bp
from model import database


def create_app():
    """应用工厂模式：便于单元测试与部署时复用。"""
    app = Flask(__name__)
    CORS(app)  # 前后端分离：允许前端页面跨域访问本 API
    app.register_blueprint(api_bp)

    @app.errorhandler(HTTPException)
    def handle_http_exception(exc):
        """把 404/405 等 HTTP 异常也统一为 JSON 格式。"""
        return jsonify({"success": False, "message": exc.description}), exc.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(exc):
        """兜底处理未预期异常，避免向前端暴露堆栈信息。"""
        logging.exception("服务器内部错误: %s", exc)
        return jsonify({"success": False, "message": "服务器内部错误"}), 500

    database.init_db()
    return app


app = create_app()

if __name__ == "__main__":
    # 0.0.0.0 便于部署到服务器后可被外部访问；本地调试可用 127.0.0.1
    app.run(host="0.0.0.0", port=5000)
