import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base
from app.models import User, Workspace, WorkspaceMember, FileUpload, Bill

def init_database():
    """初始化数据库表"""
    print("=" * 60)
    print("开始初始化数据库...")
    print("=" * 60)
    
    Base.metadata.create_all(bind=engine)
    
    print("\n✅ 数据库初始化完成！")
    print(f"📁 数据库文件位置: {engine.url.database}")
    print("\n已创建表：")
    print("  1. users              - 微信用户表")
    print("  2. workspaces         - 账务空间表")
    print("  3. workspace_members  - 空间成员表（多人协作）")
    print("  4. file_uploads       - 文件上传记录表")
    print("  5. bills              - 账单明细表")
    
    print("\n关键设计：")
    print("  ✓ 所有用户关联使用 openid（String类型）")
    print("  ✓ 所有核心表包含软删除字段（is_deleted + deleted_at）")
    print("  ✓ 空间支持多人协作，成员权限分级")
    
    print("\n索引信息：")
    print("  - users.openid (唯一索引)")
    print("  - workspaces.owner_openid (普通索引)")
    print("  - workspace_members (workspace_id, member_openid, is_deleted) 复合唯一索引")
    print("  - file_uploads (workspace_id, file_hash, is_deleted) 复合唯一索引")
    print("  - bills (workspace_id, trade_date, is_deleted) 复合索引")
    
    print("\n外键关系：")
    print("  - file_uploads.workspace_id → workspaces.id")
    print("  - workspace_members.workspace_id → workspaces.id (CASCADE)")
    print("  - bills.file_upload_id → file_uploads.id (CASCADE)")
    print("  - bills.workspace_id → workspaces.id")
    
    print("\n权限模型：")
    print("  - owner   : 完全控制权（删除空间、管理成员）")
    print("  - editor  : 可编辑数据（上传文件、编辑账单）")
    print("  - viewer  : 只读权限（查看账单）")
    
    print("\n软删除说明：")
    print("  - 删除操作仅标记 is_deleted=True，不物理删除")
    print("  - 查询时需过滤 is_deleted=False")
    print("  - 唯一索引包含 is_deleted 字段，允许同数据恢复")
    
    print("\n⚠️  注意事项：")
    print("  1. 用户关联字段统一使用 openid（非 user_id）")
    print("  2. 空间删除会级联删除成员记录")
    print("  3. 文件删除会级联删除账单记录")
    print("=" * 60)

if __name__ == "__main__":
    init_database()
