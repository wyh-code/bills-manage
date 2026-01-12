from nanoid import generate
from sqlalchemy import Column, String, Text, Index
from .base import BaseModel

class Permission(BaseModel):
    """权限表"""
    __tablename__ = "permissions"
    
    id = Column(String(21), primary_key=True, default=lambda: generate(), comment='权限ID')
    code = Column(String(100), unique=True, nullable=False, index=True, comment='权限代码')
    name = Column(String(100), nullable=False, comment='权限名称')
    type = Column(String(20), nullable=False, comment='类型: route/api/feature')
    resource = Column(String(200), nullable=False, comment='资源标识')
    description = Column(Text, nullable=True, comment='描述')
    status = Column(String(20), nullable=False, default='active', comment='状态: active/inactive')
    
    __table_args__ = (
        Index('idx_type_status', 'type', 'status', 'is_deleted'),
    )
    
    __repr_fields__ = ['id', 'code', 'type']