from nanoid import generate
from sqlalchemy import Column, String, DECIMAL, DateTime, Text, Index
from .base import BaseModel


class RechargeRecord(BaseModel):
    """充值记录表"""

    __tablename__ = "recharge_records"

    id = Column(
        String(21), primary_key=True, default=lambda: generate(), comment="充值记录ID"
    )
    user_openid = Column(String(64), nullable=False, index=True, comment="用户openid")

    # 充值信息
    amount = Column(DECIMAL(10, 2), nullable=False, comment="充值金额(元)")
    payment_method = Column(
        String(20), default="manual", comment="支付方式: manual/alipay"
    )

    # 支付宝相关
    trade_no = Column(String(64), unique=True, comment="支付宝交易号")
    out_trade_no = Column(String(64), unique=True, comment="商户订单号")

    # 状态管理
    status = Column(
        String(20),
        default="pending",
        nullable=False,
        comment="状态: pending/completed/failed/closed",
    )
    completed_at = Column(DateTime, comment="完成时间")
    remark = Column(Text, comment="备注")

    __table_args__ = (
        Index("idx_user_status", "user_openid", "status", "is_deleted"),
        Index("idx_out_trade_no", "out_trade_no"),
    )

    __repr_fields__ = ["id", "user_openid", "amount", "status"]
