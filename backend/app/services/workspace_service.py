# app/services/workspace_service.py
"""账务空间服务"""
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Workspace, WorkspaceMember, User
from app.models.enum import CommonStatus
from app.utils.file_utils import writeLog

def _get_user_info(db: Session, openid: str) -> dict:
    """获取用户信息（内部方法）"""
    user = db.query(User).filter(
        User.openid == openid,
        User.is_deleted == False
    ).first()
    
    if not user:
        return {
            'openid': openid,
            'nickname': None,
            'headimgurl': None
        }
    
    return {
        'openid': user.openid,
        'nickname': user.nickname,
        'headimgurl': user.headimgurl
    }

def _get_workspace_members(db: Session, workspace_id: str) -> list:
    """获取空间所有成员信息（内部方法）"""
    members = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.is_deleted == False
    ).all()
    
    member_list = []
    for member in members:
        user_info = _get_user_info(db, member.member_openid)
        member_list.append({
            'openid': member.member_openid,
            'nickname': user_info['nickname'],
            'headimgurl': user_info['headimgurl'],
            'role': member.role,
            'granted_at': member.granted_at.isoformat() if member.granted_at else None
        })
    
    return member_list

def create_workspace(db: Session, openid: str, name: str, description: str = None) -> dict:
    """创建空间并自动添加创建者为owner"""
    workspace = Workspace(
        name=name,
        description=description,
        status=CommonStatus.ACTIVE,
        owner_openid=openid
    )
    db.add(workspace)
    db.flush()
    
    # 添加owner成员记录
    member = WorkspaceMember(
        workspace_id=workspace.id,
        member_openid=openid,
        role='owner'
    )
    db.add(member)
    db.commit()
    db.refresh(workspace)
    
    writeLog(f"创建空间成功 - workspace_id: {workspace.id}, owner: {openid}")
    return workspace

def get_user_workspaces(db: Session, openid: str, status: str | None) -> list:
    """获取用户有权限的所有空间"""
    members = db.query(WorkspaceMember).filter(
        WorkspaceMember.member_openid == openid,
        WorkspaceMember.is_deleted == False
    ).all()
    
    workspace_ids = [m.workspace_id for m in members]
    query = db.query(Workspace).filter(
        Workspace.id.in_(workspace_ids),
        Workspace.is_deleted == False,
    )

    if status is not None:
        query = query.filter(Workspace.status == status)

    workspaces = query.all()
    
    member_map = {m.workspace_id: m.role for m in members}
    result = []
    
    for ws in workspaces:
        ws_dict = ws.to_dict()
        ws_dict['user_role'] = member_map.get(ws.id)
        
        # 获取创建者信息
        owner_info = _get_user_info(db, ws.owner_openid)
        ws_dict['owner'] = owner_info
      
        # 获取成员列表
        members = _get_workspace_members(db, ws.id)
        ws_dict['members'] = members
       
        result.append(ws_dict)

    return result

def get_workspace_detail(db: Session, workspace_id: int, openid: str) -> dict:
    """获取空间详情（需验证权限）"""
    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id,
        Workspace.is_deleted == False
    ).first()
    
    if not workspace:
        raise ValueError('空间不存在')
    
    # 验证权限
    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.member_openid == openid,
        WorkspaceMember.is_deleted == False
    ).first()
    
    if not member:
        raise ValueError('无权限访问该空间')
    
    # 组装数据
    ws_dict = workspace.to_dict()
    ws_dict['user_role'] = member.role
    
    # 获取创建者信息
    owner_info = _get_user_info(db, workspace.owner_openid)
    ws_dict['owner'] = owner_info
    
    # 获取成员列表
    members = _get_workspace_members(db, workspace.id)
    ws_dict['members'] = members
    
    return ws_dict

def update_workspace(db: Session, workspace_id: int, openid: str, 
                     name: str = None, description: str = None, status:str = None) -> Workspace:
    """更新空间（仅owner）"""
    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id,
        Workspace.is_deleted == False
    ).first()
    
    if not workspace:
        raise ValueError('空间不存在')
    
    if workspace.owner_openid != openid:
        raise ValueError('仅空间所有者可以修改')
    
    if name is not None:
        workspace.name = name
    if description is not None:
        workspace.description = description
    if status is not None:
        workspace.status = status
    
    workspace.updated_at = datetime.now()
    db.commit()
    db.refresh(workspace)
    
    writeLog(f"更新空间成功 - workspace_id: {workspace_id}")
    return workspace

def delete_workspace(db: Session, workspace_id: int, openid: str) -> None:
    """软删除空间（仅owner）"""
    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id,
        Workspace.is_deleted == False
    ).first()
    
    if not workspace:
        raise ValueError('空间不存在')
    
    if workspace.owner_openid != openid:
        raise ValueError('仅空间所有者可以删除')
    
    # 软删除空间
    workspace.is_deleted = True
    workspace.deleted_at = datetime.now()
    
    # 软删除所有成员记录
    db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.is_deleted == False
    ).update({
        'is_deleted': True,
        'deleted_at': datetime.now()
    })
    # 软删除所有账单
    # todo
    
    db.commit()
    writeLog(f"删除空间成功 - workspace_id: {workspace_id}")