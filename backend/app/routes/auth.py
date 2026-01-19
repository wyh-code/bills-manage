"""认证路由"""
import os
from flask import Blueprint, request, jsonify
from app.services import auth_service
from app.config import Config

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
DATASOURCE = Config.DATASOURCE

@auth_bp.route('/wx/config', methods=['GET'])
def wx_config():
    """
    获取微信扫码配置
    GET /api/auth/wx/config
    Headers: datasource
    Response: {success, data: {state, qrCodeUrl, ...}}
    """
    try:
        datasource = DATASOURCE or request.headers.get('datasource', DATASOURCE)
        result = auth_service.config(datasource)
        
        return jsonify({"success": True, "data": result}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@auth_bp.route('/wx/status/<state>', methods=['GET'])
def wx_status(state):
    """
    查询扫码状态
    GET /api/auth/wx/status/:state
    Headers: datasource
    Response: {success, data: {status, code, ...}}
    """
    try:
        datasource = DATASOURCE or request.headers.get('datasource', DATASOURCE)
        result = auth_service.status(datasource, state)
        
        return jsonify({"success": True, "data": result}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@auth_bp.route('/wx/code2info', methods=['GET'])
def wx_code2info():
    """
    code换取用户信息和token
    GET /api/auth/wx/code2info?code=xxx
    Headers: datasource
    Response: {success, data: {user, token}}
    """
    try:
        datasource = DATASOURCE or request.headers.get('datasource', DATASOURCE)
        code = request.args.get("code")
        
        if not code:
            return jsonify({"success": False, "message": "code参数不能为空"}), 400

        result = auth_service.code2info(datasource, code)

        return jsonify({"success": True, "data": result}), 200

    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
