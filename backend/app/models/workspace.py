from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from datetime import datetime
from app.database import Base

class Workspace(Base):
    """账务空间表"""
    __tablename__ = "workspaces"
    
    id = Column(Integer, primary_key=True, index=True, comment='空间ID')
    name = Column(String(100), nullable=False, comment='空间名称')
    description = Column(Text, nullable=True, comment='空间描述')
    owner_openid = Column(String(64), nullable=False, index=True, comment='所有者OpenID')
    
    # 软删除
    is_deleted = Column(Boolean, default=False, nullable=False, index=True, comment='是否删除')
    deleted_at = Column(DateTime, nullable=True, comment='删除时间')
    
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'owner_openid': self.owner_openid,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f"<Workspace(id={self.id}, name={self.name}, owner={self.owner_openid})>"
