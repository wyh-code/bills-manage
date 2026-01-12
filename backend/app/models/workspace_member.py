from nanoid import generate
from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from datetime import datetime
from .base import BaseModel

class WorkspaceMember(BaseModel):
    """空间成员表"""
    __tablename__ = "workspace_members"
    
    id = Column(String(21), primary_key=True, default=lambda: generate(), comment='成员记录ID')
    workspace_id = Column(String(21), ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False, index=True, comment='空间ID')
    member_openid = Column(String(64), nullable=False, index=True, comment='成员OpenID')
    role = Column(String(20), nullable=False, default='viewer', comment='角色: owner/editor/viewer')
    status = Column(String(20), nullable=False, default='active', comment='成员状态：active/inactive')
    granted_at = Column(DateTime, default=datetime.now, comment='授权时间')
    
    __table_args__ = (
        Index('idx_workspace_member_unique', 'workspace_id', 'member_openid', 'is_deleted', unique=True),
    )
    
    __repr_fields__ = ['workspace_id', 'member_openid', 'role']