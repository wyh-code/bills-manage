"""文件管理路由"""

from flask import Blueprint, request, jsonify, send_file, make_response
from urllib.parse import quote
from app.config import Config
from app.utils import jwt_required, allowed_file, get_logger
from app.services import file_service

logger = get_logger(__name__)
file_bp = Blueprint("file", __name__, url_prefix="/api/files")


@file_bp.route("/upload", methods=["POST"])
@jwt_required
def upload_file():
    """上传文件并解析"""
    try:
        workspace_id = request.args.get("workspace_id")

        if not workspace_id:
            return (
                jsonify({"success": False, "message": "workspace_id参数不能为空"}),
                400,
            )

        if "file" not in request.files:
            return jsonify({"success": False, "message": "未找到上传的文件"}), 400

        file = request.files["file"]

        if file.filename == "":
            return jsonify({"success": False, "message": "文件名不能为空"}), 400

        if not allowed_file(file.filename):
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f"不支持的文件类型,仅支持: {Config.ALLOWED_EXTENSIONS}",
                    }
                ),
                400,
            )

        result = file_service.upload_and_parse_file(
            workspace_id=workspace_id, openid=request.openid, file=file
        )

        return (
            jsonify(
                {"success": True, "status": result["status"], "data": result["data"]}
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 403
    except Exception as e:
        logger.error(f"文件上传接口异常 - error: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


@file_bp.route("/<string:file_id>/progress", methods=["GET"])
@jwt_required
def get_file_progress(file_id):
    """获取文件处理进度"""
    try:
        workspace_id = request.args.get("workspace_id")

        if not workspace_id:
            return (
                jsonify({"success": False, "message": "workspace_id参数不能为空"}),
                400,
            )

        result = file_service.get_file_progress(
            workspace_id=workspace_id, file_id=file_id, openid=request.openid
        )

        return jsonify({"success": True, "data": result}), 200

    except ValueError as e:
        logger.error(f"获取文件进度 - ValueError - file_id: {file_id}, error: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 404
    except Exception as e:
        logger.error(f"获取文件进度异常 - file_id: {file_id}, error: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


@file_bp.route("/<string:file_id>", methods=["GET"])
@jwt_required
def get_file(file_id):
    """文件预览/下载接口"""
    try:
        workspace_id = request.args.get("workspace_id")
        is_download = request.args.get("download", "false").lower() == "true"

        if not workspace_id:
            return (
                jsonify({"success": False, "message": "workspace_id参数不能为空"}),
                400,
            )

        file_path, filename, mime_type = file_service.get_file_for_view(
            workspace_id=workspace_id, file_id=file_id, openid=request.openid
        )

        response = make_response(
            send_file(file_path, mimetype=mime_type, conditional=True)
        )

        encoded_filename = quote(filename)

        if is_download:
            response.headers["Content-Disposition"] = (
                f"attachment; filename*=UTF-8''{encoded_filename}"
            )
        else:
            response.headers["Content-Disposition"] = (
                f"inline; filename*=UTF-8''{encoded_filename}"
            )

        return response

    except ValueError as e:
        logger.error(f"获取文件异常 - file_id: {file_id}, error: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 404
    except Exception as e:
        logger.error(f"获取文件异常 - file_id: {file_id}, error: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


@file_bp.route("/records", methods=["GET"])
@jwt_required
def get_file_records():
    """
    获取文件上传记录
    GET /api/files/records?workspace_ids=xxx
    """
    try:
        workspace_ids = request.args.get("workspace_ids")
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("page_size", 10))

        # 参数校验
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 10
        records, total = file_service.get_file_records(
            openid=request.openid,
            workspace_ids=workspace_ids,
            page=page,
            page_size=page_size,
        )

        return jsonify({"success": True, "data": records, "total": total}), 200

    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 403
    except Exception as e:
        logger.error(f"获取文件记录异常 - error: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500
