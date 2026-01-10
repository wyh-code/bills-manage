from nanoid import generate
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Index, Boolean
from datetime import datetime
from app.database import Base

class WorkspaceInvitation(Base):
    """空间邀请记录表"""
    __tablename__ = "workspace_invitations"
    
    id = Column(String(21), primary_key=True, default=lambda: generate(), comment='邀请ID')
    workspace_id = Column(String(21), ForeignKey('workspaces.id'), nullable=False, index=True, comment='空间ID')
    
    token = Column(String(64), unique=True, nullable=False, index=True, comment='邀请token')
    role = Column(String(20), nullable=False, comment='授权角色: editor/viewer')
    created_by_openid = Column(String(64), nullable=False, index=True, comment='创建者openid')
    
    expires_at = Column(DateTime, nullable=False, comment='过期时间')
    max_uses = Column(Integer, nullable=False, default=10, comment='最大使用次数')
    used_count = Column(Integer, default=0, nullable=False, comment='已使用次数')
    
    status = Column(String(20), nullable=False, default='active', comment='状态: active/revoked')
    
    is_deleted = Column(Boolean, default=False, nullable=False, index=True, comment='是否删除')
    deleted_at = Column(DateTime, nullable=True, comment='删除时间')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    
    __table_args__ = (
        Index('idx_workspace_token', 'workspace_id', 'token', 'is_deleted'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'workspace_id': self.workspace_id,
            'token': self.token,
            'role': self.role,
            'created_by_openid': self.created_by_openid,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'max_uses': self.max_uses,
            'used_count': self.used_count,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f"<WorkspaceInvitation(id={self.id}, workspace={self.workspace_id}, role={self.role})>"