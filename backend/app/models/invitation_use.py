from nanoid import generate
from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from datetime import datetime
from app.database import Base

class InvitationUse(Base):
    """邀请使用记录表"""
    __tablename__ = "invitation_uses"
    
    id = Column(String(21), primary_key=True, default=lambda: generate(), comment='记录ID')
    invitation_id = Column(String(21), ForeignKey('workspace_invitations.id'), nullable=False, index=True, comment='邀请ID')
    member_openid = Column(String(64), nullable=False, index=True, comment='加入成员openid')
    
    joined_at = Column(DateTime, default=datetime.now, comment='加入时间')
    
    __table_args__ = (
        Index('idx_invitation_member', 'invitation_id', 'member_openid', unique=True),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'invitation_id': self.invitation_id,
            'member_openid': self.member_openid,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None
        }
    
    def __repr__(self):
        return f"<InvitationUse(invitation={self.invitation_id}, member={self.member_openid})>"