from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from app.database import Base

class User(Base):
    """微信用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, comment='用户ID')
    openid = Column(String(64), unique=True, nullable=False, index=True, comment='微信OpenID')
    unionid = Column(String(64), nullable=True, comment='微信UnionID')
    nickname = Column(String(100), nullable=True, comment='昵称')
    headimgurl = Column(String(255), nullable=True, comment='头像URL')
    
    # 软删除
    is_deleted = Column(Boolean, default=False, nullable=False, index=True, comment='是否删除')
    deleted_at = Column(DateTime, nullable=True, comment='删除时间')
    
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'openid': self.openid,
            'unionid': self.unionid,
            'nickname': self.nickname,
            'headimgurl': self.headimgurl,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f"<User(id={self.id}, openid={self.openid}, nickname={self.nickname})>"
