"""账单管理路由"""
from flask import Blueprint, request, jsonify
from app.utils.decorators import jwt_required
from app.utils.file_utils import writeMessage
from app.utils.logger import get_logger
from app.database import SessionLocal
from app.services import bill_service
import traceback

logger = get_logger(__name__)
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
            return jsonify({'success': False, 'message': 'workspace_id参数不能为空'}), 400
        
        if not file_id:
            return jsonify({'success': False, 'message': 'file_id参数不能为空'}), 400
        
        if not bill_ids or not isinstance(bill_ids, list):
            return jsonify({'success': False, 'message': 'bill_ids必须是非空数组'}), 400
        
        result = bill_service.batch_confirm_bills(
            db=db,
            workspace_id=workspace_id,
            file_id=file_id,
            bill_ids=bill_ids,
            openid=request.openid
        )
        
        return jsonify({'success': True, 'data': result}), 200
        
    except ValueError as e:
        logger.error(writeMessage(f"批量确认账单 - ValueError - error: {str(e)}"))
        return jsonify({'success': False, 'message': str(e)}), 403
    except Exception as e:
        db.rollback()
        logger.error(writeMessage(f"批量确认账单异常 - error: {str(e)}"))
        logger.error(writeMessage(f"错误堆栈: {traceback.format_exc()}"))
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db.close()

@bill_bp.route('', methods=['GET'])
@jwt_required
def get_bills():
    """
    分页查询账单列表
    GET /api/bills?workspace_ids=id1,id2&card_last4_list=1234,5678&start_date=2025-01-01&end_date=2025-12-31&page=1&page_size=20&status=active
    """
    db = SessionLocal()
    try:
        # 获取查询参数
        workspace_ids_str = request.args.get('workspace_ids')
        workspace_ids = workspace_ids_str.split(',') if workspace_ids_str else None
        
        card_last4_str = request.args.get('card_last4_list')
        card_last4_list = card_last4_str.split(',') if card_last4_str else None

        status_str = request.args.get('status_list')
        status_list = status_str.split(',') if status_str else None
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        
        # 参数校验
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20
        
        result = bill_service.get_bills(
            db=db,
            openid=request.openid,
            workspace_ids=workspace_ids,
            card_last4_list=card_last4_list,
            status_list=status_list,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size
        )
        
        return jsonify({'success': True, 'data': result}), 200
        
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        logger.error(writeMessage(f"获取账单列表异常 - error: {str(e)}"))
        logger.error(writeMessage(f"错误堆栈: {traceback.format_exc()}"))
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db.close()

@bill_bp.route('/cards', methods=['GET'])
@jwt_required
def get_card_list():
    """
    获取卡号列表（用于筛选下拉）
    GET /api/bills/cards?workspace_ids=id1,id2
    """
    db = SessionLocal()
    try:
        workspace_ids_str = request.args.get('workspace_ids')
        workspace_ids = workspace_ids_str.split(',') if workspace_ids_str else None
        
        cards = bill_service.get_card_list(
            db=db,
            openid=request.openid,
            workspace_ids=workspace_ids
        )
        
        return jsonify({'success': True, 'data': cards}), 200
        
    except Exception as e:
        logger.error(writeMessage(f"获取卡号列表异常 - error: {str(e)}"))
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db.close()

@bill_bp.route('/<string:bill_id>', methods=['GET'])
@jwt_required
def get_bill(bill_id):
    """获取单个账单详情"""
    db = SessionLocal()
    try:
        workspace_id = request.args.get('workspace_id')
        
        if not workspace_id:
            return jsonify({'success': False, 'message': 'workspace_id参数不能为空'}), 400
        
        bill = bill_service.get_bill_detail(
            db=db,
            workspace_id=workspace_id,
            bill_id=bill_id,
            openid=request.openid
        )
        
        return jsonify({'success': True, 'data': bill}), 200
        
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 404
    except Exception as e:
        logger.error(writeMessage(f"获取账单详情异常 - bill_id: {bill_id}, error: {str(e)}"))
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db.close()

@bill_bp.route('/<string:bill_id>', methods=['PUT'])
@jwt_required
def update_bill(bill_id):
    """更新账单"""
    db = SessionLocal()
    try:
        workspace_id = request.args.get('workspace_id')
        data = request.get_json()
        
        if not workspace_id:
            return jsonify({'success': False, 'message': 'workspace_id参数不能为空'}), 400
        
        bill = bill_service.update_bill(
            db=db,
            workspace_id=workspace_id,
            bill_id=bill_id,
            openid=request.openid,
            update_data=data
        )
        
        return jsonify({'success': True, 'data': bill.to_dict()}), 200
        
    except ValueError as e:
        db.rollback()
        return jsonify({'success': False, 'message': str(e)}), 403
    except Exception as e:
        db.rollback()
        logger.error(writeMessage(f"更新账单异常 - bill_id: {bill_id}, error: {str(e)}"))
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db.close()

@bill_bp.route('/update', methods=['PUT'])
@jwt_required
def batch_update_bills():
    """
    批量更新账单
    PUT /api/bills/batch
    Body: { 
        workspace_id: string,
        updates: bills
    }
    """
    db = SessionLocal()
    try:
        data = request.get_json()
        
        workspace_id = data.get('workspace_id')
        updates = data.get('data', [])
        
        if not workspace_id:
            return jsonify({'success': False, 'message': 'workspace_id参数不能为空'}), 400
        
        if not updates or not isinstance(updates, list):
            return jsonify({'success': False, 'message': 'updates必须是非空数组'}), 400
        
        if len(updates) > 100:
            return jsonify({'success': False, 'message': '单次最多更新100条账单'}), 400
        
        result = bill_service.batch_update_bills(
            db=db,
            workspace_id=workspace_id,
            updates=updates,
            openid=request.openid
        )
        
        return jsonify({'success': True, 'data': result}), 200
        
    except ValueError as e:
        db.rollback()
        logger.error(writeMessage(f"批量更新账单 - ValueError - error: {str(e)}"))
        return jsonify({'success': False, 'message': str(e)}), 403
    except Exception as e:
        db.rollback()
        logger.error(writeMessage(f"批量更新账单异常 - error: {str(e)}"))
        logger.error(writeMessage(f"错误堆栈: {traceback.format_exc()}"))
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db.close()

@bill_bp.route('/create', methods=['POST'])
@jwt_required
def batch_create_bills():
    """
    批量更新账单
    PUT /api/bills/batch
    Body: { 
        workspace_id: string,
        data: bills
    }
    """
    db = SessionLocal()
    try:
        data = request.get_json()
        
        workspace_id = data.get('workspace_id')
        bills_data = data.get('data', [])
        
        if not workspace_id:
            return jsonify({'success': False, 'message': 'workspace_id参数不能为空'}), 400
        
        if not bills_data or not isinstance(bills_data, list):
            return jsonify({'success': False, 'message': 'bills_data必须是非空数组'}), 400
        
        if len(bills_data) > 100:
            return jsonify({'success': False, 'message': '单次最多更新100条账单'}), 400
        
        result = bill_service.batch_create_bills(
            db=db,
            workspace_id=workspace_id,
            bills_data=bills_data,
            openid=request.openid
        )
        
        return jsonify({'success': True, 'data': result}), 200
        
    except ValueError as e:
        db.rollback()
        logger.error(writeMessage(f"批量创建账单 - ValueError - error: {str(e)}"))
        return jsonify({'success': False, 'message': str(e)}), 403
    except Exception as e:
        db.rollback()
        logger.error(writeMessage(f"批量创建账单异常 - error: {str(e)}"))
        logger.error(writeMessage(f"错误堆栈: {traceback.format_exc()}"))
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db.close()

@bill_bp.route('/<string:bill_id>', methods=['DELETE'])
@jwt_required
def delete_bill(bill_id):
    """删除账单"""
    db = SessionLocal()
    try:
        workspace_id = request.args.get('workspace_id')
        
        if not workspace_id:
            return jsonify({'success': False, 'message': 'workspace_id参数不能为空'}), 400
        
        bill_service.delete_bill(
            db=db,
            workspace_id=workspace_id,
            bill_id=bill_id,
            openid=request.openid
        )
        
        return jsonify({'success': True, 'message': '账单已删除'}), 200
        
    except ValueError as e:
        db.rollback()
        logger.error(writeMessage(f"删除账单异常 - bill_id: {bill_id}, error: {str(e)}"))
        return jsonify({'success': False, 'message': str(e)}), 403
    except Exception as e:
        db.rollback()
        logger.error(writeMessage(f"删除账单异常 - bill_id: {bill_id}, error: {str(e)}"))
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db.close()