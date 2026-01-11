import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base
from app.models import (
    User, 
    Workspace, 
    WorkspaceMember, 
    FileUpload, 
    Bill,
    WorkspaceInvitation,
    InvitationUse,
    Notification
)

def init_database():
    """初始化数据库表"""
    print("=" * 60)
    print("开始初始化数据库...")
    print("=" * 60)
    
    Base.metadata.create_all(bind=engine)
    
    print("\n✅ 数据库初始化完成！")
    print(f"📁 数据库文件位置: {engine.url.database}")
    print("\n已创建表：")
    print("  1. users                       - 微信用户表")
    print("  2. workspaces                  - 账务空间表")
    print("  3. workspace_members           - 空间成员表（多人协作）")
    print("  4. file_uploads                - 文件上传记录表")
    print("  5. bills                       - 账单明细表")
    print("  6. workspace_invitations       - 空间邀请记录表")
    print("  7. invitation_uses             - 邀请使用记录表")
    print("  8. notifications               - 系统通知表")
    
    print("\n关键设计：")
    print("  ✓ 所有用户关联使用 openid（String类型）")
    print("  ✓ 所有核心表包含软删除字段（is_deleted + deleted_at）")
    print("  ✓ 空间支持多人协作，成员权限分级")
    print("  ✓ 空间支持邀请链接分享，可追踪加入来源")
    
    print("\n索引信息：")
    print("  - users.openid (唯一索引)")
    print("  - workspaces.owner_openid (普通索引)")
    print("  - workspace_members (workspace_id, member_openid, is_deleted) 复合唯一索引")
    print("  - file_uploads (workspace_id, file_hash, is_deleted, status) 复合唯一索引")
    print("  - bills (workspace_id, trade_date, is_deleted) 复合索引")
    print("  - workspace_invitations.token (唯一索引)")
    print("  - workspace_invitations (workspace_id, token, is_deleted) 复合索引")
    print("  - invitation_uses (invitation_id, member_openid) 复合唯一索引")
    
    print("\n外键关系：")
    print("  - file_uploads.workspace_id → workspaces.id")
    print("  - workspace_members.workspace_id → workspaces.id (CASCADE)")
    print("  - bills.file_upload_id → file_uploads.id (CASCADE)")
    print("  - bills.workspace_id → workspaces.id")
    print("  - workspace_invitations.workspace_id → workspaces.id")
    print("  - invitation_uses.invitation_id → workspace_invitations.id")

    print("\n权限模型：")
    print("  - owner   : 完全控制权（删除空间、管理成员、创建任意角色邀请）")
    print("  - editor  : 可编辑数据（上传文件、编辑账单、创建editor/viewer邀请）")
    print("  - viewer  : 只读权限（查看账单）") 

    print("\n邀请分享功能：")
    print("  - viewer 角色无法创建邀请")
    print("  - editor 可创建 editor/viewer 邀请")
    print("  - owner 可创建任意角色邀请")
    print("  - 默认有效期：7天")
    print("  - 默认使用次数限制：10次")
    print("  - 撤销邀请会自动移除通过该邀请加入的成员（软删除）")
    
    print("\n邀请分享功能：")
    print("  - 默认有效期：7天")
    print("  - 默认使用次数限制：10次")
    print("  - 撤销邀请会自动移除通过该邀请加入的成员（软删除）")
    print("  - 邀请角色不能高于创建者自身角色")
    
    print("\n软删除说明：")
    print("  - 删除操作仅标记 is_deleted=True，不物理删除")
    print("  - 查询时需过滤 is_deleted=False")
    print("  - 唯一索引包含 is_deleted 字段，允许同数据恢复")
    print("  - 空间删除会级联软删除：成员、文件、账单")
    print("  - 邀请撤销会级联软删除：通过该邀请加入的成员")
    
    print("\n⚠️  注意事项：")
    print("  1. 用户关联字段统一使用 openid（非 user_id）")
    print("  2. 空间删除会级联软删除成员、文件、账单记录")
    print("  3. 文件删除会级联软删除账单记录")
    print("  4. 邀请token使用secrets.token_urlsafe(32)生成，长度43字符")
    print("  5. 邀请链接格式：/dashboard?join=<token>")
    print("=" * 60)

if __name__ == "__main__":
    init_database()