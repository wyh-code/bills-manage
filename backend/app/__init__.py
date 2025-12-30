# 确保models被导入，以便Base能识别所有表
from app.models import User, Workspace, WorkspaceMember, FileUpload, Bill

__all__ = ['User', 'Workspace', 'WorkspaceMember', 'FileUpload', 'Bill']

