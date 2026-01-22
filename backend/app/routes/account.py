"""账户管理路由"""

from io import BytesIO
from flask import Blueprint, request, jsonify, send_file
from app.utils import jwt_required, get_logger
from app.services import account_service, billing_service

logger = get_logger(__name__)
account_bp = Blueprint("account", __name__, url_prefix="/api/accounts")


@account_bp.route("/balance", methods=["GET"])
@jwt_required
def get_balance():
    """
    查询账户余额
    GET /api/accounts/balance
    """
    try:
        balance_info = account_service.get_balance(openid=request.openid)
        return jsonify({"success": True, "data": balance_info}), 200

    except Exception as e:
        logger.error(f"查询余额异常 - error: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


@account_bp.route("/usage/monthly", methods=["GET"])
@jwt_required
def get_monthly_usage():
    """
    查询月度用量
    GET /api/accounts/usage/monthly?month=2025-01
    """
    try:
        month = request.args.get("month")

        if not month:
            return jsonify({"success": False, "message": "月份参数不能为空"}), 400

        # 验证月份格式
        import re

        if not re.match(r"^\d{4}-\d{2}$", month):
            return (
                jsonify(
                    {"success": False, "message": "月份格式错误，请使用 YYYY-MM 格式"}
                ),
                400,
            )

        result = account_service.get_monthly_usage(openid=request.openid, month=month)

        return jsonify({"success": True, "data": result}), 200

    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception as e:
        logger.error(f"查询月度用量异常 - error: {str(e)}")
        return jsonify({"success": False, "message": "查询失败"}), 500


@account_bp.route("/usage/export", methods=["GET"])
@jwt_required
def export_monthly_usage():
    """
    导出月度用量Excel
    GET /api/accounts/usage/export?month=2025-01
    """
    try:
        month = request.args.get("month")

        if not month:
            return jsonify({"success": False, "message": "月份参数不能为空"}), 400

        # 验证月份格式
        import re

        if not re.match(r"^\d{4}-\d{2}$", month):
            return (
                jsonify(
                    {"success": False, "message": "月份格式错误，请使用 YYYY-MM 格式"}
                ),
                400,
            )

        excel_bytes = account_service.export_monthly_usage(
            openid=request.openid, month=month
        )

        filename = f"用量报表_{month}.xlsx"

        return send_file(
            BytesIO(excel_bytes),
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name=filename,
        )

    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception as e:
        logger.error(f"导出月度用量异常 - error: {str(e)}")
        return jsonify({"success": False, "message": "导出失败"}), 500


@account_bp.route("/billing/records", methods=["GET"])
@jwt_required
def get_billing_records():
    """
    获取扣费记录(含文件信息)
    GET /api/accounts/billing/records?month=2025-01&page=1&page_size=20
    """
    try:
        month = request.args.get("month")
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("page_size", 20))

        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20

        result = billing_service.get_billing_records_with_file(
            openid=request.openid, month=month, page=page, page_size=page_size
        )

        return jsonify({"success": True, "data": result}), 200

    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception as e:
        logger.error(f"获取扣费记录异常 - error: {str(e)}")
        return jsonify({"success": False, "message": "查询失败"}), 500

