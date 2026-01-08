from nanoid import generate
from sqlalchemy import Column, String, Text, Date, DECIMAL, DateTime, ForeignKey, Index, Boolean
from datetime import datetime
from app.database import Base

class Bill(Base):
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
    status = Column(String(20), nullable=False, default='active', comment='账单状态：active/inactive/pending/payed')
    
    raw_line = Column(Text, nullable=False, comment='原始精炼字符串单行')
    
    is_deleted = Column(Boolean, default=False, nullable=False, index=True, comment='是否删除')
    deleted_at = Column(DateTime, nullable=True, comment='删除时间')
    created_at = Column(DateTime, default=datetime.now, comment='记录创建时间')
    
    __table_args__ = (
        Index('idx_workspace_trade_date', 'workspace_id', 'trade_date', 'is_deleted'),
    )
    
    def to_dict(self):
        """转换为字典 - 统一安全转换"""
        def safe_float(value):
            """安全转换为float"""
            if value is None:
                return None
            try:
                # SQLite 可能返回 str、float、int
                return float(value)
            except (ValueError, TypeError) as e:
                from app.utils.file_utils import writeLog
                writeLog(f"Bill.to_dict() 转换失败 - id: {self.id}, value: {value}, type: {type(value)}, error: {str(e)}")
                return None
        
        return {
            'id': self.id,
            'file_upload_id': self.file_upload_id,
            'workspace_id': self.workspace_id,
            'bank': self.bank,
            'trade_date': self.trade_date.isoformat() if self.trade_date else None,
            'record_date': self.record_date.isoformat() if self.record_date else None,
            'description': self.description,
            'amount_cny': safe_float(self.amount_cny),      # ✅ 安全转换
            'card_last4': self.card_last4,
            'amount_foreign': safe_float(self.amount_foreign),  # ✅ 安全转换
            'currency': self.currency,
            'raw_line': self.raw_line,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f"<Bill(id={self.id}, bank={self.bank}, amount={self.amount_foreign})>"