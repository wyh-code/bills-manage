"""账单管理路由"""
from flask import Blueprint, request, jsonify
from app.utils.decorators import jwt_required
from app.utils.file_utils import writeLog
from app.database import SessionLocal
from app.services import bill_service

bill_bp = Blueprint('bill', __name__, url_prefix='/api/bills')

@bill_bp.route('/batch', methods=['POST'])
@jwt_required
def batch_confirm_bills():
    """
    批量确认账单（pending → active）
    POST /api/bills/batch
    Headers: Authorization: Bearer <token>
    Body: { workspace_id, file_id, bill_ids }
    """
    db = SessionLocal()
    try:
        data = request.get_json()
        
        workspace_id = data.get('workspace_id')
        file_id = data.get('file_id')
        bill_ids = data.get('bill_ids', [])
        
        if not workspace_id:
            return jsonify({
                'success': False,
                'message': 'workspace_id参数不能为空'
            }), 400
        
        if not file_id:
            return jsonify({
                'success': False,
                'message': 'file_id参数不能为空'
            }), 400
        
        if not bill_ids or not isinstance(bill_ids, list):
            return jsonify({
                'success': False,
                'message': 'bill_ids必须是非空数组'
            }), 400
        
        result = bill_service.batch_confirm_bills(
            db=db,
            workspace_id=workspace_id,
            file_id=file_id,
            bill_ids=bill_ids,
            openid=request.openid
        )
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except ValueError as e:
        writeLog(f"批量确认账单 - ValueError - error: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 403
    except Exception as e:
        db.rollback()
        writeLog(f"批量确认账单异常 - workspace_id: {data.get('workspace_id')}, error: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
    finally:
        db.close()

