from nanoid import generate
from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from datetime import datetime
from .base import BaseModel

class UserPermission(BaseModel):
    """用户权限关联表"""
    __tablename__ = "user_permissions"
    
    id = Column(String(21), primary_key=True, default=lambda: generate(), comment='记录ID')
    user_openid = Column(String(64), ForeignKey('users.openid'), nullable=False, index=True, comment='用户openid')
    permission_id = Column(String(21), ForeignKey('permissions.id'), nullable=False, index=True, comment='权限ID')
    granted_at = Column(DateTime, default=datetime.now, comment='授予时间')
    granted_by = Column(String(64), nullable=True, comment='授予者openid')
    
    __table_args__ = (
        Index('idx_user_permission', 'user_openid', 'permission_id', 'is_deleted', unique=True),
    )
    
    __repr_fields__ = ['user_openid', 'permission_id']