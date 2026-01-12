from nanoid import generate
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Index
from datetime import datetime
from .base import BaseModel
import json

class Notification(BaseModel):
    """系统通知表"""
    __tablename__ = "notifications"

    id = Column(String(21), primary_key=True, default=lambda: generate(), comment="通知ID")
    
    # 接收者信息
    recipient_openid = Column(String(64), nullable=False, index=True, comment="接收者openid")
    workspace_id = Column(String(21), ForeignKey("workspaces.id"), nullable=True, index=True, comment="关联空间ID")
    
    # 通知内容
    type = Column(String(50), nullable=False, comment="通知类型")
    priority = Column(String(20), nullable=False, default="normal", comment="优先级: high/normal/low")
    title = Column(String(200), nullable=False, comment="通知标题")
    content = Column(Text, nullable=True, comment="通知详细内容")
    data = Column(Text, nullable=True, comment="扩展数据JSON字符串")
    
    # 触发者信息
    triggered_by_openid = Column(String(64), nullable=True, comment="触发者openid")
    
    # 状态管理
    status = Column(String(20), nullable=False, default="unread", comment="状态: unread/read")
    read_at = Column(DateTime, nullable=True, comment="阅读时间")
    
    __table_args__ = (
        Index("idx_recipient_status", "recipient_openid", "status", "is_deleted"),
        Index("idx_workspace_recipient", "workspace_id", "recipient_openid", "is_deleted"),
        Index("idx_priority_status", "priority", "status", "created_at"),
    )
    
    def to_dict(self):
        """转换为字典（重写以解析JSON）"""
        result = super().to_dict()
        
        # 解析JSON数据
        if self.data:
            try:
                result["data"] = json.loads(self.data)
            except:
                result["data"] = None
        else:
            result["data"] = None
        
        return result
    
    __repr_fields__ = ['id', 'type', 'recipient_openid']