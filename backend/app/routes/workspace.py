"""账务空间路由"""
from flask import Blueprint, request, jsonify
from app.utils.decorators import jwt_required
from app.database import SessionLocal
from app.services import workspace_service

workspace_bp = Blueprint('workspace', __name__, url_prefix='/api/workspaces')

@workspace_bp.route('', methods=['POST'])
@jwt_required
def create_workspace():
    """
    创建空间
    POST /api/workspaces
    Headers: Authorization: Bearer <token>
    Body: { name, description? }
    """
    db = SessionLocal()
    try:
        data = request.get_json()
        
        name = data.get('name', '').strip()
        if not name:
            return jsonify({
                'success': False,
                'message': '空间名称不能为空'
            }), 400
        
        description = data.get('description', '').strip() if data.get('description') else None
        
        workspace = workspace_service.create_workspace(
            db=db,
            openid=request.openid,
            name=name,
            description=description
        )
        
        return jsonify({
            'success': True,
            'data': workspace.to_dict()
        }), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
    finally:
        db.close()

@workspace_bp.route('', methods=['GET'])
@jwt_required
def get_workspaces():
    """
    获取用户空间列表
    GET /api/workspaces?status=active&role=editor
    Headers: Authorization: Bearer <token>
    
    Query参数:
    - status: 可选，过滤空间状态 (active/inactive)
    - role: 可选，过滤用户角色 (owner/editor/viewer)，返回权限>=该角色的空间
    """
    db = SessionLocal()
    try:
        status = request.args.get('status')
        role = request.args.get('role')
        
        # 角色参数校验
        if role and role not in ['owner', 'editor', 'viewer']:
            return jsonify({
                'success': False,
                'message': 'role参数只能是 owner、editor 或 viewer'
            }), 400
        
        workspaces = workspace_service.get_user_workspaces(
            db=db,
            openid=request.openid,
            status=status,
            role=role
        )
        
        return jsonify({
            'success': True,
            'data': workspaces
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
    finally:
        db.close()

@workspace_bp.route('/<string:workspace_id>', methods=['GET'])
@jwt_required
def get_workspace(workspace_id):
    """
    获取空间详情
    GET /api/workspaces/:id
    Headers: Authorization: Bearer <token>
    """
    db = SessionLocal()
    try:
        workspace = workspace_service.get_workspace_detail(
            db=db,
            workspace_id=workspace_id,
            openid=request.openid
        )
        
        return jsonify({
            'success': True,
            'data': workspace
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
    finally:
        db.close()

@workspace_bp.route('/<string:workspace_id>', methods=['PUT'])
@jwt_required
def update_workspace(workspace_id):
    """
    更新空间
    PUT /api/workspaces/:id
    Headers: Authorization: Bearer <token>
    Body: { name?, description? }
    """
    db = SessionLocal()
    try:
        data = request.get_json()
        
        name = data.get('name', '').strip() if data.get('name') else None
        description = data.get('description', '').strip() if data.get('description') else None
        status = data.get('status', '').strip() if data.get('status') else None
        
        if name == '':
            return jsonify({
                'success': False,
                'message': '空间名称不能为空'
            }), 400
        
        workspace = workspace_service.update_workspace(
            db=db,
            workspace_id=workspace_id,
            openid=request.openid,
            name=name,
            description=description,
            status=status
        )
        
        return jsonify({
            'success': True,
            'data': workspace.to_dict()
        }), 200
        
    except ValueError as e:
        db.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 403
    except Exception as e:
        db.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
    finally:
        db.close()

@workspace_bp.route('/<string:workspace_id>', methods=['DELETE'])
@jwt_required
def delete_workspace(workspace_id):
    """
    删除空间（软删除）
    DELETE /api/workspaces/:id
    Headers: Authorization: Bearer <token>
    """
    db = SessionLocal()
    try:
        workspace_service.delete_workspace(
            db=db,
            workspace_id=workspace_id,
            openid=request.openid
        )
        
        return jsonify({
            'success': True,
            'message': '空间已删除'
        }), 200
        
    except ValueError as e:
        db.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 403
    except Exception as e:
        db.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
    finally:
        db.close()