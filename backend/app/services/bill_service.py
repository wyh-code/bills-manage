"""账单管理服务"""
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from app.models import Bill, FileUpload, WorkspaceMember
from app.utils.file_utils import writeLog

def _check_workspace_permission(db: Session, workspace_id: str, openid: str, required_role: str = None) -> tuple:
    """
    检查用户是否为空间成员及权限等级
    :param required_role: 'owner', 'editor', 'viewer' 或 None
    :return: (has_permission: bool, user_role: str)
    """
    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.member_openid == openid,
        WorkspaceMember.is_deleted == False
    ).first()
    
    if not member:
        return False, None
    
    if required_role is None:
        return True, member.role
    
    role_levels = {'owner': 3, 'editor': 2, 'viewer': 1}
    user_level = role_levels.get(member.role, 0)
    required_level = role_levels.get(required_role, 0)
    
    return user_level >= required_level, member.role

def get_bills(
    db: Session, 
    openid: str, 
    workspace_ids: list = None,
    card_last4_list: list = None,
    status_list: str = None,
    start_date: str = None, 
    end_date: str = None,
    page: int = 1,
    page_size: int = 20
) -> dict:
    """
    分页查询账单列表
    :param workspace_ids: 空间ID列表（多选）
    :param card_last4_list: 卡号末四位列表（多选）
    :param status_list: 账单状态
    :param start_date: 开始日期 YYYY-MM-DD（基于trade_date）
    :param end_date: 结束日期 YYYY-MM-DD（基于trade_date）
    :param page: 页码（从1开始）
    :param page_size: 每页数量
    :return: {total, page, page_size, items}
    """
    # 获取用户有权限的所有空间
    members = db.query(WorkspaceMember).filter(
        WorkspaceMember.member_openid == openid,
        WorkspaceMember.is_deleted == False
    ).all()
    
    accessible_workspace_ids = [m.workspace_id for m in members]
    
    # 构建基础查询
    query = db.query(Bill).filter(
        Bill.workspace_id.in_(accessible_workspace_ids),
        Bill.is_deleted == False
    )
    
    # 筛选：指定空间
    if workspace_ids:
        # 确保只查询用户有权限的空间
        filtered_ids = [wid for wid in workspace_ids if wid in accessible_workspace_ids]
        if not filtered_ids:
            return {'total': 0, 'page': page, 'page_size': page_size, 'items': []}
        query = query.filter(Bill.workspace_id.in_(filtered_ids))
    
    # 筛选：卡号
    if card_last4_list:
        query = query.filter(Bill.card_last4.in_(card_last4_list))

    # 筛选：状态
    if status_list:
        query = query.filter(Bill.status.in_(status_list))
    
    # 筛选：日期范围
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Bill.trade_date >= start_dt)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Bill.trade_date <= end_dt)
        except ValueError:
            pass
    
    # 统计总数
    total = query.count()
    
    # 分页查询
    offset = (page - 1) * page_size
    bills = query.order_by(
        Bill.trade_date.desc(), 
        Bill.created_at.desc()
    ).limit(page_size).offset(offset).all()
    
    return {
        'total': total,
        'page': page,
        'page_size': page_size,
        'items': [bill.to_dict() for bill in bills]
    }

def get_card_list(db: Session, openid: str, workspace_ids: list = None) -> list:
    """
    获取卡号列表（用于筛选下拉）
    :param workspace_ids: 可选，指定空间ID列表
    :return: [{'card_last4': '1234', 'count': 10}, ...]
    """
    # 获取用户有权限的所有空间
    members = db.query(WorkspaceMember).filter(
        WorkspaceMember.member_openid == openid,
        WorkspaceMember.is_deleted == False
    ).all()
    
    accessible_workspace_ids = [m.workspace_id for m in members]
    
    # 构建查询
    query = db.query(
        Bill.card_last4,
        func.count(Bill.id).label('count')
    ).filter(
        Bill.workspace_id.in_(accessible_workspace_ids),
        Bill.is_deleted == False,
        Bill.card_last4.isnot(None)  # 排除 null
    )
    
    # 可选：按指定空间筛选
    if workspace_ids:
        filtered_ids = [wid for wid in workspace_ids if wid in accessible_workspace_ids]
        if filtered_ids:
            query = query.filter(Bill.workspace_id.in_(filtered_ids))
    
    # 分组统计
    results = query.group_by(Bill.card_last4).order_by(Bill.card_last4).all()
    
    return [
        {'card_last4': card, 'count': count}
        for card, count in results
    ]

def batch_confirm_bills(db: Session, workspace_id: str, file_id: str, bill_ids: list, openid: str) -> dict:
    """
    批量确认账单（pending → active）
    :param bill_ids: 要确认的账单ID列表
    """
    # 校验权限（需要editor及以上）
    has_permission, user_role = _check_workspace_permission(db, workspace_id, openid, required_role='editor')
    if not has_permission:
        raise ValueError('无权限执行此操作，需要editor或owner角色')
    
    # 获取文件记录
    file_record = db.query(FileUpload).filter(
        FileUpload.id == file_id,
        FileUpload.workspace_id == workspace_id,
        FileUpload.is_deleted == False
    ).first()
    
    if not file_record:
        raise ValueError('文件记录不存在')
    
    # 批量更新账单状态
    updated_count = db.query(Bill).filter(
        Bill.id.in_(bill_ids),
        Bill.file_upload_id == file_id,
        Bill.workspace_id == workspace_id,
        Bill.is_deleted == False,
        Bill.status == 'pending'    # 只更新 pending 状态的
    ).update(
        {'status': 'active'},
        synchronize_session=False
    )
    
    db.commit()
    
    # 获取更新后的账单列表
    bills = db.query(Bill).filter(
        Bill.id.in_(bill_ids),
        Bill.is_deleted == False
    ).all()
    
    writeLog(f"批量确认账单成功 - file_id: {file_id}, updated: {updated_count}, total: {len(bills)}")
    
    return {
        'file_id': file_id,
        'bills_count': len(bills),
        'updated_count': updated_count,
        'bills': [bill.to_dict() for bill in bills]
    }

def get_bill_detail(db: Session, workspace_id: str, bill_id: str, openid: str) -> dict:
    """获取单条账单详情"""
    has_permission, _ = _check_workspace_permission(db, workspace_id, openid)
    if not has_permission:
        raise ValueError('无权限访问该空间')
    
    bill = db.query(Bill).filter(
        Bill.id == bill_id,
        Bill.workspace_id == workspace_id,
        Bill.is_deleted == False
    ).first()
    
    if not bill:
        raise ValueError('账单不存在')
    
    return bill.to_dict()

def update_bill(db: Session, workspace_id: str, bill_id: str, openid: str, update_data: dict) -> Bill:
    """更新账单"""
    has_permission, _ = _check_workspace_permission(db, workspace_id, openid, required_role='editor')
    if not has_permission:
        raise ValueError('无权限执行此操作，需要editor或owner角色')
    
    bill = db.query(Bill).filter(
        Bill.id == bill_id,
        Bill.workspace_id == workspace_id,
        Bill.is_deleted == False
    ).first()
    
    if not bill:
        raise ValueError('账单不存在')
    
    # 更新字段
    if 'bank' in update_data:
        bill.bank = update_data['bank']
    
    if 'trade_date' in update_data and update_data['trade_date']:
        try:
            bill.trade_date = datetime.strptime(update_data['trade_date'], '%Y-%m-%d').date()
        except ValueError:
            pass
    
    if 'record_date' in update_data and update_data['record_date']:
        try:
            bill.record_date = datetime.strptime(update_data['record_date'], '%Y-%m-%d').date()
        except ValueError:
            pass
    
    if 'description' in update_data:
        bill.description = update_data['description']
    
    if 'amount_cny' in update_data:
        bill.amount_cny = update_data['amount_cny']
    
    if 'card_last4' in update_data:
        bill.card_last4 = update_data['card_last4']
    
    if 'amount_foreign' in update_data:
        bill.amount_foreign = update_data['amount_foreign']
    
    if 'currency' in update_data:
        bill.currency = update_data['currency']
    
    if 'status' in update_data:
        bill.status = update_data['status']
    
    db.commit()
    db.refresh(bill)
    
    writeLog(f"账单更新成功 - bill_id: {bill_id}")
    
    return bill

def batch_update_bills(db: Session, workspace_id: str, updates: list, openid: str) -> dict:
    """
    批量更新账单
    :param updates: [{'bill_id': 'xxx', 'data': {...}}, ...]
    :return: {updated_count, failed_count, results}
    """
    # 校验权限（需要editor及以上）
    has_permission, user_role = _check_workspace_permission(db, workspace_id, openid, required_role='editor')
    if not has_permission:
        raise ValueError('无权限执行此操作，需要editor或owner角色')
    
    updated_count = 0
    failed_count = 0
    results = []
    
    for item in updates:
        id = item.get('id')
        
        if not id:
            failed_count += 1
            results.append({'id': None, 'success': False, 'message': 'id不能为空'})
            continue
        
        try:
            # 获取账单
            bill = db.query(Bill).filter(
                Bill.id == id,
                Bill.workspace_id == workspace_id,
                Bill.is_deleted == False
            ).first()
            
            if not bill:
                failed_count += 1
                results.append({'id': id, 'success': False, 'message': '账单不存在'})
                continue
            
            # 更新字段
            if 'bank' in item:
                bill.bank = item['bank']
            
            if 'trade_date' in item and item['trade_date']:
                try:
                    bill.trade_date = datetime.strptime(item['trade_date'], '%Y-%m-%d').date()
                except ValueError:
                    pass
            
            if 'record_date' in item and item['record_date']:
                try:
                    bill.record_date = datetime.strptime(item['record_date'], '%Y-%m-%d').date()
                except ValueError:
                    pass
            
            if 'description' in item:
                bill.description = item['description']
            
            if 'amount_cny' in item:
                bill.amount_cny = item['amount_cny']
            
            if 'card_last4' in item:
                bill.card_last4 = item['card_last4']
            
            if 'amount_foreign' in item:
                bill.amount_foreign = item['amount_foreign']
            
            if 'currency' in item:
                bill.currency = item['currency']
            
            if 'status' in item:
                bill.status = item['status']
            
            updated_count += 1
            results.append({'bill_id': id, 'success': True})
            
        except Exception as e:
            failed_count += 1
            results.append({'bill_id': id, 'success': False, 'message': str(e)})
    
    db.commit()
    
    writeLog(f"批量更新账单 - workspace_id: {workspace_id}, updated: {updated_count}, failed: {failed_count}")
    
    return {
        'updated_count': updated_count,
        'failed_count': failed_count,
        'results': results
    }

def batch_create_bills(db: Session, workspace_id: str, bills_data: list, openid: str) -> dict:
    """
    批量更新账单
    :param bills_data: [{'bill_id': 'xxx', 'data': {...}}, ...]
    :return: {updated_count, failed_count, results}
    """
    # 校验权限（需要editor及以上）
    has_permission, user_role = _check_workspace_permission(db, workspace_id, openid, required_role='editor')
    if not has_permission:
        raise ValueError('无权限执行此操作，需要editor或owner角色')
    
    created_count = 0
    failed_count = 0
    results = []
    
    # 创建账单
    for bill_item in bills_data:
        try:
            if bill_item['trade_date']:
                try:
                    bill_item['trade_date'] = datetime.strptime(bill_item['trade_date'], '%Y-%m-%d').date()
                except ValueError:
                    pass
            
            if bill_item['record_date']:
                try:
                    bill_item['record_date'] = datetime.strptime(bill_item['record_date'], '%Y-%m-%d').date()
                except ValueError:
                    pass

            bill = Bill(
                file_upload_id=bill_item.get('file_upload_id'),
                workspace_id=workspace_id,
                bank=bill_item.get('bank'),
                trade_date=bill_item.get('trade_date'),
                record_date=bill_item.get('record_date'),
                description=bill_item.get('description'),
                amount_cny=bill_item.get('amount_cny'),
                card_last4=bill_item.get('card_last4'),
                amount_foreign=bill_item.get('amount_foreign'),
                currency=bill_item.get('currency'),
                raw_line=bill_item.get('raw_line', ''),
                status=bill_item.get('status')
            )
            db.add(bill)
            created_count += 1
            results.append({'bill_id': bill_item.get('id', ''), 'success': True})
        except Exception as e:
            failed_count += 1
            results.append({'bill_id': bill_item.get('id', ''), 'success': False, 'message': str(e)})
    
    db.commit()
    
    writeLog(f"批量创建账单 - workspace_id: {workspace_id}, updated: {created_count}, failed: {failed_count}")
    
    return {
        'created_count': created_count,
        'failed_count': failed_count,
        'results': results
    }

def delete_bill(db: Session, workspace_id: str, bill_id: str, openid: str) -> None:
    """删除账单（软删除）"""
    has_permission, _ = _check_workspace_permission(db, workspace_id, openid, required_role='editor')
    if not has_permission:
        raise ValueError('无权限执行此操作，需要editor或owner角色')
    
    bill = db.query(Bill).filter(
        Bill.id == bill_id,
        Bill.workspace_id == workspace_id,
        Bill.is_deleted == False
    ).first()
    
    if not bill:
        raise ValueError('账单不存在')
    
    bill.is_deleted = True
    bill.deleted_at = datetime.now()
    
    # 更新关联文件的账单数量
    file_record = db.query(FileUpload).filter(
        FileUpload.id == bill.file_upload_id,
        FileUpload.is_deleted == False
    ).first()
    
    if file_record:
        valid_bills_count = db.query(Bill).filter(
            Bill.file_upload_id == file_record.id,
            Bill.is_deleted == False
        ).count()
        file_record.bills_count = valid_bills_count
    
    db.commit()
    
    writeLog(f"账单删除成功 - bill_id: {bill_id}")