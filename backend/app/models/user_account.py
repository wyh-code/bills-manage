from nanoid import generate
from sqlalchemy import Column, String, DECIMAL, ForeignKey, Index
from .base import BaseModel


class UserAccount(BaseModel):
    """用户账户表"""

    __tablename__ = "user_accounts"

    id = Column(
        String(21), primary_key=True, default=lambda: generate(), comment="账户ID"
    )
    user_openid = Column(
        String(64),
        ForeignKey("users.openid"),
        unique=True,
        nullable=False,
        index=True,
        comment="用户openid",
    )

    # 余额字段
    balance = Column(
        DECIMAL(10, 2), default=0.00, nullable=False, comment="账户余额(元)"
    )
    total_recharged = Column(
        DECIMAL(10, 2), default=0.00, nullable=False, comment="累计充值(元)"
    )
    total_consumed = Column(
        DECIMAL(10, 2), default=0.00, nullable=False, comment="累计消费(元)"
    )

    # 状态
    status = Column(
        String(20), default="active", nullable=False, comment="账户状态: active/frozen"
    )

    __table_args__ = (Index("idx_user_status", "user_openid", "status", "is_deleted"),)

    __repr_fields__ = ["id", "user_openid", "balance"]
