from nanoid import generate
from sqlalchemy import Column, String, DECIMAL, Text, ForeignKey, Index
from .base import BaseModel


class BillingRecord(BaseModel):
    """扣费记录表"""

    __tablename__ = "billing_records"

    id = Column(
        String(21), primary_key=True, default=lambda: generate(), comment="扣费记录ID"
    )
    user_openid = Column(String(64), nullable=False, index=True, comment="用户openid")
    
    # 关联记录
    token_usage_id = Column(
        String(21),
        ForeignKey("token_usage_records.id"),
        index=True,
        comment="Token使用记录ID",
    )

    # 扣费信息
    amount = Column(DECIMAL(10, 2), nullable=False, comment="扣费金额(元)")
    balance_before = Column(DECIMAL(10, 2), comment="扣费前余额")
    balance_after = Column(DECIMAL(10, 2), comment="扣费后余额")
    billing_type = Column(String(20), default="token_usage", comment="扣费类型")
    description = Column(Text, comment="扣费说明")

    __table_args__ = (
        Index("idx_user_type", "user_openid", "billing_type", "is_deleted"),
        Index("idx_user_created", "user_openid", "created_at", "is_deleted"),
    )

    __repr_fields__ = ["id", "user_openid", "amount"]
