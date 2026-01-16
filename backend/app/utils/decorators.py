"""装饰器"""

from functools import wraps
from flask import request, jsonify
from app.utils import verify_token


def jwt_required(f):
    """
    JWT认证装饰器
    支持两种认证方式：
    1. Authorization: Bearer <token> （优先）
    2. URL参数 ?token=xxx
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None

        # 优先从 Authorization 头获取
        auth_header = request.headers.get("Authorization")
        if auth_header:
            parts = auth_header.split()
            if len(parts) != 2 or parts[0] != "Bearer":
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "认证格式错误，应为: Bearer <token>",
                        }
                    ),
                    401,
                )

            token = parts[1]

        # 如果头部没有，尝试从URL参数获取
        if not token:
            token = request.args.get("token")

        if not token:
            return jsonify({"success": False, "message": "未提供认证token"}), 401

        # 验证token
        try:
            payload = verify_token(token)
            request.openid = payload["openid"]
        except ValueError as e:
            return jsonify({"success": False, "message": str(e)}), 401

        return f(*args, **kwargs)

    return decorated_function
