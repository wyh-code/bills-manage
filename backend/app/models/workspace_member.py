from nanoid import generate
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, Boolean
from datetime import datetime
from app.database import Base

class WorkspaceMember(Base):
    """空间成员表"""
    __tablename__ = "workspace_members"
    
    id = Column(String(21), primary_key=True, default=lambda: generate(), comment='成员记录ID')
    workspace_id = Column(Integer, ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False, index=True, comment='空间ID')
    member_openid = Column(String(64), nullable=False, index=True, comment='成员OpenID')
    role = Column(String(20), nullable=False, default='viewer', comment='角色: owner/editor/viewer')
    
    # 软删除
    is_deleted = Column(Boolean, default=False, nullable=False, index=True, comment='是否删除')
    deleted_at = Column(DateTime, nullable=True, comment='删除时间')
    status = Column(String(20), nullable=False, default='active', comment='成员状态：active/inactive')
    granted_at = Column(DateTime, default=datetime.now, comment='授权时间')
    
    __table_args__ = (
        Index('idx_workspace_member_unique', 'workspace_id', 'member_openid', 'is_deleted', unique=True),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'workspace_id': self.workspace_id,
            'member_openid': self.member_openid,
            'role': self.role,
            'status': self.status,
            'granted_at': self.granted_at.isoformat() if self.granted_at else None
        }
    
    def __repr__(self):
        return f"<WorkspaceMember(workspace={self.workspace_id}, member={self.member_openid}, role={self.role})>"
