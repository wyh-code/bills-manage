from nanoid import generate
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Index
from .base import BaseModel

class Invitation(BaseModel):
    """统一邀请表(平台邀请/工作空间邀请)"""
    __tablename__ = "invitations"
    
    id = Column(String(21), primary_key=True, default=lambda: generate(), comment='邀请ID')
    token = Column(String(64), unique=True, nullable=False, index=True, comment='邀请token')
    name = Column(String(100), nullable=True, comment='邀请名称/备注')
    type = Column(String(20), nullable=False, comment='类型: platform/workspace')
    
    # 工作空间相关(type=workspace时使用)
    workspace_id = Column(String(21), ForeignKey('workspaces.id'), nullable=True, index=True, comment='关联空间ID')
    role = Column(String(20), nullable=True, comment='授权角色: editor/viewer')
    
    # 平台权限相关(type=platform时使用)
    permissions = Column(Text, nullable=True, comment='权限ID列表(JSON数组)')
    
    # 通用字段
    created_by_openid = Column(String(64), nullable=True, index=True, comment='创建者openid')
    max_uses = Column(Integer, nullable=False, default=10, comment='最大使用次数')
    used_count = Column(Integer, default=0, nullable=False, comment='已使用次数')
    expires_at = Column(DateTime, nullable=False, comment='过期时间')
    status = Column(String(20), nullable=False, default='active', comment='状态: active/revoked')
    
    __table_args__ = (
        Index('idx_workspace_token', 'workspace_id', 'token', 'is_deleted'),
        Index('idx_type', 'type'),
    )
    
    def to_dict(self):
        """转换为字典（重写以支持类型特定字段）"""
        result = super().to_dict()
        
        # 根据类型清理无关字段
        if self.type == 'workspace':
            result.pop('permissions', None)
        elif self.type == 'platform':
            result.pop('workspace_id', None)
            result.pop('role', None)
        
        return result
    
    __repr_fields__ = ['id', 'type', 'token']