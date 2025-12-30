"""装饰器"""
from functools import wraps
from flask import request, jsonify
from app.utils.jwt_util import verify_token

def jwt_required(f):
    """
    JWT认证装饰器
    验证请求头中的Authorization: Bearer <token>
    验证成功后将openid注入request对象
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 获取Authorization头
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({
                'success': False,
                'message': '未提供认证token'
            }), 401
        
        # 提取token
        parts = auth_header.split()
        if len(parts) != 2 or parts[0] != 'Bearer':
            return jsonify({
                'success': False,
                'message': '认证格式错误，应为: Bearer <token>'
            }), 401
        
        token = parts[1]
        
        # 验证token
        try:
            payload = verify_token(token)
            request.openid = payload['openid']
        except ValueError as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated_function
