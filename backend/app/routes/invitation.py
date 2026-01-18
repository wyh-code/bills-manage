"""邀请管理路由"""

from flask import Blueprint, request, jsonify
from app.services import invitation_service
from app.utils import get_logger, writeMessage, jwt_required

logger = get_logger(__name__)
invitation_bp = Blueprint("invitation", __name__, url_prefix="/api/invitations")


@invitation_bp.route("", methods=["POST"])
@jwt_required
def create_invitation():
    """
    创建邀请码(统一接口)
    POST /api/invitations
    Body: {
        type: 'platform' | 'workspace',
        workspace_id?: string,  # workspace类型必填
        role?: 'editor' | 'viewer'  # workspace类型必填
    }
    """
    try:
        data = request.get_json()
        invitation_type = data.get("type", "").strip()

        if not invitation_type:
            return jsonify({"success": False, "message": "type参数不能为空"}), 400

        if invitation_type not in ["platform", "workspace"]:
            return (
                jsonify({"success": False, "message": "type只能是platform或workspace"}),
                400,
            )

        workspace_id = (
            data.get("workspace_id", "").strip() if data.get("workspace_id") else None
        )

        role = data.get("role", "").strip() if data.get("role") else None

        # 获取前端域名
        base_url = request.headers.get("Origin") or request.host_url.rstrip("/")

        result = invitation_service.create_invitation(
            openid=request.openid,
            invitation_type=invitation_type,
            workspace_id=workspace_id,
            role=role,
            base_url=base_url,
        )

        return jsonify({"success": True, "data": result}), 200

    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 403
    except Exception as e:
        logger.error(writeMessage(f"创建邀请异常 - error: {str(e)}"))
        return jsonify({"success": False, "message": str(e)}), 500


@invitation_bp.route("/join", methods=["POST"])
@jwt_required
def join_by_invitation():
    """
    通过邀请码加入
    POST /api/invitations/join
    Body: { token: 'xxx' }
    """
    try:
        data = request.get_json()
        token = data.get("token", "").strip()

        if not token:
            return jsonify({"success": False, "message": "token参数不能为空"}), 400

        result = invitation_service.join_by_invitation(
            token=token, openid=request.openid
        )

        return jsonify({"success": True, "data": result}), 200

    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception as e:
        logger.error(writeMessage(f"加入邀请异常 - error: {str(e)}"))
        return jsonify({"success": False, "message": str(e)}), 500


@invitation_bp.route("", methods=["GET"])
@jwt_required
def get_invitations():
    """
    获取邀请列表
    GET /api/invitations?type=platform&workspace_id=xxx
    """
    try:
        invitation_type = request.args.get("type")
        workspace_id = request.args.get("workspace_id")

        invitations = invitation_service.get_invitations(
            openid=request.openid,
            invitation_type=invitation_type,
            workspace_id=workspace_id,
        )

        return jsonify({"success": True, "data": invitations}), 200

    except Exception as e:
        logger.error(writeMessage(f"获取邀请列表异常 - error: {str(e)}"))
        return jsonify({"success": False, "message": str(e)}), 500

@invitation_bp.route("/uses", methods=["GET"])
@jwt_required
def get_invitation_uses():
    """
    获取邀请使用记录
    GET /api/invitations/uses?limit=5
    """
    try:
        limit = request.args.get("limit", type=int)

        uses = invitation_service.get_invitation_uses(
            openid=request.openid, limit=limit
        )

        return jsonify({"success": True, "data": uses}), 200

    except Exception as e:
        logger.error(writeMessage(f"获取邀请使用记录异常 - error: {str(e)}"))
        return jsonify({"success": False, "message": str(e)}), 500
