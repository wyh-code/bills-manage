"""账单管理服务"""
from sqlalchemy.orm import Session
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
        Bill.status == 'pending'  # 只更新 pending 状态的
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