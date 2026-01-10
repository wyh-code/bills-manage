"""文件管理路由"""
from flask import Blueprint, request, jsonify, send_file, make_response
from urllib.parse import quote
from app.database import SessionLocal
from app.utils.decorators import jwt_required
from app.utils.file_utils import allowed_file, writeLog
from app.services import file_service

file_bp = Blueprint("file", __name__, url_prefix="/api/files")

@file_bp.route("/upload", methods=["POST"])
@jwt_required
def upload_file():
    """上传文件并解析"""
    db = SessionLocal()
    try:
        workspace_id = request.args.get("workspace_id")

        if not workspace_id:
            return (
                jsonify({"success": False, "message": "workspace_id参数不能为空"}),
                400,
            )

        # 校验权限
        has_permission, user_role = file_service.check_workspace_permission(
            db, workspace_id, request.openid, required_role="editor"
        )
        if not has_permission:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "无权限执行此操作，需要editor或owner角色",
                    }
                ),
                403,
            )

        # 检查文件
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
                        "message": "不支持的文件类型，仅支持: pdf, png, ecxml",
                    }
                ),
                400,
            )

        result = file_service.upload_and_parse_file(
            db=db,
            workspace_id=workspace_id,
            openid=request.openid,
            file=file
        )

        return (
            jsonify(
                {"success": True, "status": result["status"], "data": result["data"]}
            ),
            200,
        )

    except Exception as e:
        db.rollback()
        writeLog(f"文件上传接口异常 - workspace_id: {workspace_id}, error: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        db.close()

@file_bp.route('/<string:file_id>/progress', methods=['GET'])
@jwt_required
def get_file_progress(file_id):
    """获取文件处理进度"""
    db = SessionLocal()
    try:
        workspace_id = request.args.get('workspace_id')
        
        if not workspace_id:
            return jsonify({
                'success': False,
                'message': 'workspace_id参数不能为空'
            }), 400
        
        result = file_service.get_file_progress(
            db=db,
            workspace_id=workspace_id,
            file_id=file_id,
            openid=request.openid
        )
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except ValueError as e:
        writeLog(f"获取文件进度 - ValueError - file_id: {file_id}, error: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 404
    except Exception as e:
        writeLog(f"获取文件进度异常 - file_id: {file_id}, workspace_id: {workspace_id}, error: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
    finally:
        db.close() 

@file_bp.route('/<string:file_id>', methods=['GET'])
@jwt_required
def get_file(file_id):
    """
    文件预览/下载接口
    支持两种认证方式：
    1. Authorization: Bearer <token> （优先）
    2. URL参数 ?token=xxx （用于浏览器直接访问）
    """
    db = SessionLocal()
    try:
        workspace_id = request.args.get('workspace_id')
        is_download = request.args.get('download', 'false').lower() == 'true'
        
        if not workspace_id:
            return jsonify({'success': False, 'message': 'workspace_id参数不能为空'}), 400
        
        # openid 已由 @jwt_required 注入到 request.openid
        file_path, filename, mime_type = file_service.get_file_for_view(
            db=db,
            workspace_id=workspace_id,
            file_id=file_id,
            openid=request.openid
        )
        
        response = make_response(
            send_file(
                file_path,
                mimetype=mime_type,
                conditional=True
            )
        )
        
        # 使用 RFC 5987 编码支持中文文件名
        from urllib.parse import quote
        encoded_filename = quote(filename)
        
        if is_download:
            response.headers['Content-Disposition'] = f"attachment; filename*=UTF-8''{encoded_filename}"
        else:
            response.headers['Content-Disposition'] = f"inline; filename*=UTF-8''{encoded_filename}"
        
        return response
        
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 404
    except Exception as e:
        writeLog(f"获取文件异常 - file_id: {file_id}, error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db.close()
