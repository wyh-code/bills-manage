from nanoid import generate
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Index
from datetime import datetime
from app.database import Base
import json


class Notification(Base):
    """系统通知表"""

    __tablename__ = "notifications"

    id = Column(
        String(21), primary_key=True, default=lambda: generate(), comment="通知ID"
    )

    # 接收者信息
    recipient_openid = Column(
        String(64), nullable=False, index=True, comment="接收者openid"
    )
    workspace_id = Column(
        String(21),
        ForeignKey("workspaces.id"),
        nullable=True,
        index=True,
        comment="关联空间ID",
    )

    # 通知内容
    type = Column(String(50), nullable=False, comment="通知类型")
    priority = Column(
        String(20), nullable=False, default="normal", comment="优先级: high/normal/low"
    )
    title = Column(String(200), nullable=False, comment="通知标题")
    content = Column(Text, nullable=True, comment="通知详细内容")
    data = Column(Text, nullable=True, comment="扩展数据JSON字符串")

    # 触发者信息
    triggered_by_openid = Column(String(64), nullable=True, comment="触发者openid")

    # 状态管理
    status = Column(
        String(20), nullable=False, default="unread", comment="状态: unread/read"
    )
    read_at = Column(DateTime, nullable=True, comment="阅读时间")

    # 软删除
    is_deleted = Column(
        Boolean, default=False, nullable=False, index=True, comment="是否删除"
    )
    deleted_at = Column(DateTime, nullable=True, comment="删除时间")

    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    __table_args__ = (
        Index("idx_recipient_status", "recipient_openid", "status", "is_deleted"),
        Index(
            "idx_workspace_recipient", "workspace_id", "recipient_openid", "is_deleted"
        ),
        Index("idx_priority_status", "priority", "status", "created_at"),
    )

    def to_dict(self):
        """转换为字典"""
        result = {
            "id": self.id,
            "recipient_openid": self.recipient_openid,
            "workspace_id": self.workspace_id,
            "type": self.type,
            "priority": self.priority,
            "title": self.title,
            "content": self.content,
            "triggered_by_openid": self.triggered_by_openid,
            "status": self.status,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

        # 解析JSON数据
        if self.data:
            try:
                result["data"] = json.loads(self.data)
            except:
                result["data"] = None
        else:
            result["data"] = None

        return result

    def __repr__(self):
        return f"<Notification(id={self.id}, type={self.type}, recipient={self.recipient_openid})>"
