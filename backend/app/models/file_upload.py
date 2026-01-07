from nanoid import generate
from sqlalchemy import Column, Integer, String, Text, BigInteger, DateTime, ForeignKey, Index, Boolean
from datetime import datetime
from app.database import Base

class FileUpload(Base):
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

    # 软删除
    is_deleted = Column(Boolean, default=False, nullable=False, index=True, comment='是否删除')
    deleted_at = Column(DateTime, nullable=True, comment='删除时间')
    
    created_at = Column(DateTime, default=datetime.now, comment='记录创建时间')
    
    __table_args__ = (
        Index('idx_workspace_file_hash', 'workspace_id', 'file_hash', 'is_deleted', unique=True),
    )
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'workspace_id': self.workspace_id,
            'uploaded_by_openid': self.uploaded_by_openid,
            'file_hash': self.file_hash,
            'original_filename': self.original_filename,
            'saved_path': self.saved_path,
            'file_size': self.file_size,
            'bills_count': self.bills_count,
            'status': self.status,
            'upload_time': self.upload_time,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f"<FileUpload(id={self.id}, filename={self.original_filename}, bills={self.bills_count})>"
