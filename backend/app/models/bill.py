from nanoid import generate
from sqlalchemy import Column, String, Text, Date, DECIMAL, ForeignKey, Index
from .base import BaseModel

class Bill(BaseModel):
    """账单明细表"""
    __tablename__ = "bills"
    
    id = Column(String(21), primary_key=True, default=lambda: generate(), comment='账单ID')
    file_upload_id = Column(String(21), ForeignKey('file_uploads.id', ondelete='CASCADE'), nullable=False, index=True, comment='关联文件ID')
    workspace_id = Column(String(21), ForeignKey('workspaces.id'), nullable=False, index=True, comment='所属空间ID')
    
    bank = Column(String(50), nullable=True, comment='发卡行')
    trade_date = Column(Date, nullable=True, comment='交易日')
    record_date = Column(Date, nullable=True, comment='记账日')
    description = Column(Text, nullable=True, comment='交易摘要')
    amount_cny = Column(DECIMAL(15, 2), nullable=True, comment='人民币金额')
    card_last4 = Column(String(4), nullable=True, comment='卡号末四位')
    amount_foreign = Column(DECIMAL(15, 2), nullable=True, comment='交易地金额')
    currency = Column(String(10), nullable=True, comment='记账币种')
    status = Column(String(20), nullable=False, default='active', comment='账单状态：active/inactive/pending/modified/payed')
    
    raw_line = Column(Text, nullable=False, comment='原始精炼字符串单行')
    
    __table_args__ = (
        Index('idx_workspace_trade_date', 'workspace_id', 'trade_date', 'is_deleted'),
    )
    
    __repr_fields__ = ['id', 'bank', 'amount_foreign']