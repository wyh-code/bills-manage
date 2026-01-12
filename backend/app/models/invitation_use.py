from nanoid import generate
from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from datetime import datetime
from .base import BaseModel

class InvitationUse(BaseModel):
    """邀请使用记录表"""
    __tablename__ = "invitation_uses"
    
    id = Column(String(21), primary_key=True, default=lambda: generate(), comment='记录ID')
    invitation_id = Column(String(21), ForeignKey('invitations.id'), nullable=False, index=True, comment='邀请ID')
    user_openid = Column(String(64), nullable=False, index=True, comment='使用者openid')
    invitation_type = Column(String(20), nullable=False, comment='邀请类型: platform/workspace')
    used_at = Column(DateTime, default=datetime.now, comment='使用时间')
    
    __table_args__ = (
        Index('idx_invitation_user', 'invitation_id', 'user_openid', unique=True),
    )
    
    __repr_fields__ = ['invitation_id', 'user_openid', 'invitation_type']