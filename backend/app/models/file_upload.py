from nanoid import generate
from sqlalchemy import Column, Integer, String, Text, BigInteger, ForeignKey, Index
from .base import BaseModel

class FileUpload(BaseModel):
    """文件上传记录表"""
    __tablename__ = "file_uploads"
    
    id = Column(String(21), primary_key=True, default=lambda: generate(), comment='记录ID')
    workspace_id = Column(String(21), ForeignKey('workspaces.id'), nullable=False, index=True, comment='所属空间ID')
    uploaded_by_openid = Column(String(64), nullable=False, index=True, comment='上传者OpenID')
    
    file_hash = Column(String(64), nullable=False, index=True, comment='文件SHA256哈希')
    original_filename = Column(String(255), nullable=False, comment='原始文件名')
    saved_path = Column(String(500), nullable=False, comment='source目录相对路径')
    file_size = Column(BigInteger, nullable=False, comment='文件大小(字节)')
    raw_content = Column(Text, nullable=True, comment='原始解析内容')
    refined_content = Column(Text, nullable=True, comment='DeepSeek精炼完整文本')
    bills_count = Column(Integer, default=0, comment='精炼出的账单数量')
    upload_time = Column(BigInteger, nullable=False, comment='上传时间戳')
    status = Column(String(20), nullable=False, default='active', comment='文件状态：active/inactive/processing/completed/failed')
    remark = Column(Text, nullable=True, comment='备注')

    __table_args__ = (
        Index('idx_workspace_file_hash', 'id', 'workspace_id', 'file_hash', 'is_deleted', 'status', unique=True),
    )
    
    __repr_fields__ = ['id', 'original_filename', 'bills_count']