"""空间邀请服务"""
import secrets
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import Invitation, InvitationUse, WorkspaceMember, User
from app.services.workspace_service import get_workspace_detail
from app.utils.file_utils import writeMessage
from app.utils.logger import get_logger

logger = get_logger(__name__)

def _check_workspace_permission(db: Session, workspace_id: str, openid: str, required_role: str = None) -> tuple:
    """检查用户空间权限"""
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

def create_invitation(
    db: Session, 
    workspace_id: str, 
    openid: str, 
    role: str,
    base_url: str
) -> dict:
    """
    创建工作空间邀请链接
    :param role: 邀请角色 (editor/viewer)
    :param base_url: 前端域名 (如: https://yourdomain.com)
    """
    # 权限校验
    has_permission, user_role = _check_workspace_permission(db, workspace_id, openid)
    if not has_permission:
        raise ValueError('无权限访问该空间')
    
    if user_role == 'viewer':
        raise ValueError('viewer 角色无法创建邀请')
    
    # 角色权限校验：不能授予高于自己的角色
    role_levels = {'owner': 3, 'editor': 2, 'viewer': 1}
    
    if role_levels.get(role, 0) > role_levels.get(user_role, 0):
        raise ValueError(f'无法创建高于自身权限的邀请,您的角色为: {user_role}')
    
    # 角色有效性校验
    if role not in ['editor', 'viewer']:
        raise ValueError('邀请角色只能是 editor 或 viewer')
    
    # 生成token
    token = secrets.token_urlsafe(32)
    
    # 设置过期时间（7天）
    expires_at = datetime.now() + timedelta(days=7)
    
    # 创建邀请记录（type='workspace'）
    invitation = Invitation(
        token=token,
        type='workspace',
        workspace_id=workspace_id,
        role=role,
        created_by_openid=openid,
        expires_at=expires_at,
        max_uses=10,
        used_count=0,
        status='active'
    )
    
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    
    # 生成分享链接
    share_url = f"{base_url}/dashboard?join={token}"
    
    logger.info(writeMessage(f"创建工作空间邀请成功 - workspace_id: {workspace_id}, role: {role}, creator: {openid}"))
    
    result = invitation.to_dict()
    result['share_url'] = share_url
    
    return result

def join_by_invitation(db: Session, token: str, openid: str) -> dict:
    """通过邀请链接加入空间"""
    # 查询邀请记录（只处理workspace类型）
    invitation = db.query(Invitation).filter(
        Invitation.token == token,
        Invitation.type == 'workspace',
        Invitation.is_deleted == False
    ).first()
    
    if not invitation:
        raise ValueError('邀请链接无效')
    
    # 校验状态
    if invitation.status != 'active':
        raise ValueError('邀请已失效')
    
    # 校验过期时间
    if invitation.expires_at < datetime.now():
        raise ValueError('邀请已过期')
    
    # 校验使用次数
    if invitation.used_count >= invitation.max_uses:
        raise ValueError('邀请已达使用上限')
    
    # 检查用户是否已是成员
    existing_member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == invitation.workspace_id,
        WorkspaceMember.member_openid == openid,
        WorkspaceMember.is_deleted == False
    ).first()
    
    if existing_member:
        # 幂等性：已是成员，直接返回空间信息
        workspace_detail = get_workspace_detail(db, invitation.workspace_id, openid)
        return {
            'workspace_id': invitation.workspace_id,
            'workspace_name': workspace_detail['name'],
            'role': existing_member.role,
            'message': '您已是该空间成员'
        }
    
    # 添加为成员
    member = WorkspaceMember(
        workspace_id=invitation.workspace_id,
        member_openid=openid,
        role=invitation.role,
        status='active'
    )
    db.add(member)
    
    # 记录邀请使用（type='workspace'）
    use_record = InvitationUse(
        invitation_id=invitation.id,
        user_openid=openid,
        invitation_type='workspace'
    )
    db.add(use_record)
    
    # 更新邀请使用次数
    invitation.used_count += 1
    
    db.commit()
    
    # 获取空间信息
    workspace_detail = get_workspace_detail(db, invitation.workspace_id, openid)
    
    logger.info(writeMessage(f"用户通过邀请加入空间 - workspace_id: {invitation.workspace_id}, user: {openid}, role: {invitation.role}"))
    
    return {
        'workspace_id': invitation.workspace_id,
        'workspace_name': workspace_detail['name'],
        'role': invitation.role,
        'joined_at': datetime.now().isoformat()
    }

def get_invitations(db: Session, workspace_id: str, openid: str, status: str = None) -> list:
    """获取空间的邀请列表（仅workspace类型）"""
    # 权限校验（任何成员都可查看）
    has_permission, _ = _check_workspace_permission(db, workspace_id, openid)
    if not has_permission:
        raise ValueError('无权限访问该空间')
    
    # 构建查询（只查询workspace类型）
    query = db.query(Invitation).filter(
        Invitation.workspace_id == workspace_id,
        Invitation.type == 'workspace',
        Invitation.is_deleted == False
    )
    
    if status:
        query = query.filter(Invitation.status == status)
    
    invitations = query.order_by(Invitation.created_at.desc()).all()
    
    result = []
    for inv in invitations:
        inv_dict = inv.to_dict()
        
        # 获取创建者信息
        creator = db.query(User).filter(User.openid == inv.created_by_openid).first()
        inv_dict['creator'] = {
            'openid': inv.created_by_openid,
            'nickname': creator.nickname if creator else None
        }
        
        # 获取通过该邀请加入的成员列表
        uses = db.query(InvitationUse).filter(
            InvitationUse.invitation_id == inv.id
        ).all()
        
        members_info = []
        for use in uses:
            user = db.query(User).filter(User.openid == use.user_openid).first()
            member = db.query(WorkspaceMember).filter(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.member_openid == use.user_openid,
                WorkspaceMember.is_deleted == False
            ).first()
            
            members_info.append({
                'openid': use.user_openid,
                'nickname': user.nickname if user else None,
                'joined_at': use.used_at.isoformat() if use.used_at else None,
                'is_active': member is not None  # 成员是否仍在空间中
            })
        
        inv_dict['joined_members'] = members_info
        
        result.append(inv_dict)
    
    return result

def revoke_invitation(db: Session, workspace_id: str, invitation_id: str, openid: str) -> None:
    """撤销邀请"""
    # 权限校验（需要editor及以上）
    has_permission, _ = _check_workspace_permission(db, workspace_id, openid, required_role='editor')
    if not has_permission:
        raise ValueError('无权限执行此操作，需要editor或owner角色')
    
    # 查询邀请（校验workspace类型）
    invitation = db.query(Invitation).filter(
        Invitation.id == invitation_id,
        Invitation.workspace_id == workspace_id,
        Invitation.type == 'workspace',
        Invitation.is_deleted == False
    ).first()
    
    if not invitation:
        raise ValueError('邀请不存在')
    
    # 更新邀请状态
    invitation.status = 'revoked'
    
    # 软删除通过该邀请加入的成员
    uses = db.query(InvitationUse).filter(
        InvitationUse.invitation_id == invitation_id
    ).all()
    
    removed_count = 0
    for use in uses:
        member = db.query(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.member_openid == use.user_openid,
            WorkspaceMember.is_deleted == False
        ).first()
        
        if member:
            member.is_deleted = True
            member.deleted_at = datetime.now()
            removed_count += 1
    
    db.commit()
    
    logger.info(writeMessage(f"撤销邀请成功 - invitation_id: {invitation_id}, removed_members: {removed_count}"))