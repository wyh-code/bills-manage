"""邀请管理路由"""
from flask import Blueprint, request, jsonify
from app.utils.decorators import jwt_required
from app.database import SessionLocal
from app.services import invitation_service
from app.utils.file_utils import writeMessage
from app.utils.logger import get_logger
import traceback

logger = get_logger(__name__)
invitation_bp = Blueprint('invitation', __name__, url_prefix='/api/workspaces')

@invitation_bp.route('/<string:workspace_id>/invitations', methods=['POST'])
@jwt_required
def create_invitation(workspace_id):
    """
    创建邀请链接
    POST /api/workspaces/:workspace_id/invitations
    Body: { role: 'editor' }
    """
    db = SessionLocal()
    try:
        data = request.get_json()
        role = data.get('role', '').strip()
        
        if not role:
            return jsonify({'success': False, 'message': 'role参数不能为空'}), 400
        
        if role not in ['editor', 'viewer']:
            return jsonify({'success': False, 'message': 'role只能是editor或viewer'}), 400
        
        # 获取前端域名（从请求头或配置）
        base_url = request.headers.get('Origin') or request.host_url.rstrip('/')
        
        result = invitation_service.create_invitation(
            db=db,
            workspace_id=workspace_id,
            openid=request.openid,
            role=role,
            base_url=base_url
        )
        
        return jsonify({'success': True, 'data': result}), 200
        
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 403
    except Exception as e:
        db.rollback()
        logger.error(writeMessage(f"创建邀请异常 - workspace_id: {workspace_id}, error: {str(e)}"))
        logger.error(writeMessage(f"错误堆栈: {traceback.format_exc()}"))
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db.close()

@invitation_bp.route('/join', methods=['POST'])
@jwt_required
def join_by_invitation():
    """
    通过邀请加入空间
    POST /api/workspaces/join
    Body: { invitation_token: 'xxx' }
    """
    db = SessionLocal()
    try:
        data = request.get_json()
        token = data.get('invitation_token', '').strip()
        
        if not token:
            return jsonify({'success': False, 'message': 'invitation_token参数不能为空'}), 400
        
        result = invitation_service.join_by_invitation(
            db=db,
            token=token,
            openid=request.openid
        )
        
        return jsonify({'success': True, 'data': result}), 200
        
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        db.rollback()
        logger.error(writeMessage(f"加入空间异常 - error: {str(e)}"))
        logger.error(writeMessage(f"错误堆栈: {traceback.format_exc()}"))
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db.close()

@invitation_bp.route('/<string:workspace_id>/invitations', methods=['GET'])
@jwt_required
def get_invitations(workspace_id):
    """
    获取空间邀请列表
    GET /api/workspaces/:workspace_id/invitations?status=active
    """
    db = SessionLocal()
    try:
        status = request.args.get('status')
        
        invitations = invitation_service.get_invitations(
            db=db,
            workspace_id=workspace_id,
            openid=request.openid,
            status=status
        )
        
        return jsonify({'success': True, 'data': invitations}), 200
        
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 403
    except Exception as e:
        logger.error(writeMessage(f"获取邀请列表异常 - workspace_id: {workspace_id}, error: {str(e)}"))
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db.close()

@invitation_bp.route('/<string:workspace_id>/invitations/<string:invitation_id>', methods=['DELETE'])
@jwt_required
def revoke_invitation(workspace_id, invitation_id):
    """
    撤销邀请
    DELETE /api/workspaces/:workspace_id/invitations/:invitation_id
    """
    db = SessionLocal()
    try:
        invitation_service.revoke_invitation(
            db=db,
            workspace_id=workspace_id,
            invitation_id=invitation_id,
            openid=request.openid
        )
        
        return jsonify({'success': True, 'message': '邀请已撤销'}), 200
        
    except ValueError as e:
        db.rollback()
        logger.error(writeMessage(f"撤销邀请异常 - invitation_id: {invitation_id}, error: {str(e)}"))
        return jsonify({'success': False, 'message': str(e)}), 403
    except Exception as e:
        db.rollback()
        logger.error(writeMessage(f"撤销邀请异常 - invitation_id: {invitation_id}, error: {str(e)}"))
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db.close()