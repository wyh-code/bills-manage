from nanoid import generate
from sqlalchemy import Column, String, Integer, DECIMAL, Text, ForeignKey, Index
from .base import BaseModel


class TokenUsageRecord(BaseModel):
    """Token使用记录表"""

    __tablename__ = "token_usage_records"

    id = Column(
        String(21), primary_key=True, default=lambda: generate(), comment="记录ID"
    )

    # 关联信息
    user_openid = Column(String(64), nullable=False, index=True, comment="用户openid")
    workspace_id = Column(
        String(21),
        ForeignKey("workspaces.id"),
        nullable=True,
        index=True,
        comment="工作空间ID",
    )
    file_upload_id = Column(
        String(21),
        ForeignKey("file_uploads.id"),
        nullable=True,
        index=True,
        comment="文件ID",
    )

    # Token消耗明细
    api_type = Column(String(20), nullable=False, comment="API类型: refine/convert")
    model = Column(String(50), comment="模型名称")
    prompt_tokens = Column(Integer, default=0, comment="输入token数")
    completion_tokens = Column(Integer, default=0, comment="输出token数")
    total_tokens = Column(Integer, default=0, comment="总token数")

    # 计费信息
    unit_price = Column(DECIMAL(10, 2), comment="单价(元/千token)")
    cost = Column(DECIMAL(10, 2), comment="本次费用(元)")

    # 请求上下文
    request_id = Column(String(64), comment="API请求ID")
    response_time = Column(Integer, comment="响应时间(ms)")
    status = Column(
        String(20), default="success", nullable=False, comment="状态: success/failed"
    )
    error_message = Column(Text, comment="错误信息")

    __table_args__ = (
        Index("idx_user_workspace", "user_openid", "workspace_id", "is_deleted"),
        Index("idx_file_upload", "file_upload_id", "is_deleted"),
        Index("idx_user_created", "user_openid", "created_at", "is_deleted"),
        Index("idx_workspace_created", "workspace_id", "created_at", "is_deleted"),
    )

    __repr_fields__ = ["id", "api_type", "total_tokens", "cost"]
