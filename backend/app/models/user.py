from nanoid import generate
from sqlalchemy import Column, String, DateTime
from .base import BaseModel

class User(BaseModel):
    """微信用户表"""
    __tablename__ = "users"
    
    id = Column(String(21), primary_key=True, default=lambda: generate(), comment='用户记录ID')
    openid = Column(String(64), unique=True, nullable=False, index=True, comment='微信OpenID')
    unionid = Column(String(64), nullable=True, comment='微信UnionID')
    nickname = Column(String(100), nullable=True, comment='昵称')
    headimgurl = Column(String(255), nullable=True, comment='头像URL')
    status = Column(String(20), nullable=False, default='inactive', comment='用户状态：active/inactive')
    
    # 平台激活相关
    platform_invitation_token = Column(String(64), nullable=True, comment='激活使用的平台邀请token')
    activated_at = Column(DateTime, nullable=True, comment='激活时间')
    
    __repr_fields__ = ['id', 'openid', 'status']