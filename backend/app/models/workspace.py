from nanoid import generate
from sqlalchemy import Column, String, Text
from .base import BaseModel

class Workspace(BaseModel):
    """账务空间表"""
    __tablename__ = "workspaces"
    
    id = Column(String(21), primary_key=True, default=lambda: generate(), comment='空间ID')
    name = Column(String(100), nullable=False, comment='空间名称')
    description = Column(Text, nullable=True, comment='空间描述')
    status = Column(String(20), nullable=False, default='active', comment='空间状态：active/inactive')
    owner_openid = Column(String(64), nullable=False, index=True, comment='所有者OpenID')
    
    __repr_fields__ = ['id', 'name', 'owner_openid']