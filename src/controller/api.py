"""API 控制器：定义 REST 路由，负责请求校验与标准化 JSON 响应。"""

from flask import Blueprint, jsonify, request

from exceptions import CalculatorError
from service import calculator, history_service

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.get("/health")
def health():
    """健康检查接口，用于部署后的连通性验证。"""
    return jsonify({"success": True, "message": "backend is running"}), 200


@api_bp.post("/calculate")
def calculate():
    """计算接口：后端解析并求值，成功时把记录写入数据库。"""
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or "expression" not in data:
        return (
            jsonify(
                {
                    "success": False,
                    "message": '请求体必须为 JSON，例如 {"expression": "1+2"}',
                }
            ),
            400,
        )
    expression = data["expression"]
    if not isinstance(expression, str):
        return (
            jsonify({"success": False, "message": "expression 必须是字符串"}),
            400,
        )
    try:
        result = calculator.evaluate(expression)
    except CalculatorError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400
    record = history_service.add_history(expression.strip(), result)
    return (
        jsonify(
            {
                "success": True,
                "expression": record["expression"],
                "result": result,
                "record_id": record["id"],
            }
        ),
        200,
    )


@api_bp.get("/history")
def get_history():
    """历史查询接口：返回全部记录，支持 ?search= 关键字过滤。"""
    search = request.args.get("search", "").strip()
    history = history_service.list_history(search or None)
    return (
        jsonify({"success": True, "count": len(history), "history": history}),
        200,
    )


@api_bp.delete("/history/<int:record_id>")
def delete_history(record_id):
    """删除单条历史记录；记录不存在时返回 404。

    返回 200 + JSON 响应体（而非 204），便于前端确认删除结果，
    也避免部分浏览器对 204 空响应体在控制台记录 net::ERR_ABORTED。
    """
    if history_service.delete_history(record_id):
        return jsonify({"success": True, "message": f"记录 {record_id} 已删除"}), 200
    return (
        jsonify({"success": False, "message": f"记录 {record_id} 不存在"}),
        404,
    )


@api_bp.delete("/history")
def clear_history():
    """清空全部历史记录（扩展功能）。"""
    cleared = history_service.clear_history()
    return jsonify({"success": True, "cleared": cleared}), 200
