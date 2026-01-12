import os
from pathlib import Path
from sqlalchemy import create_engine
from contextlib import contextmanager
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app.config import Config
from app.utils.logger import get_logger

logger = get_logger(__name__)

# 数据库文件路径
db_path = Config.DB_DIR / Config.DB_PATH
os.makedirs(os.path.dirname(db_path), exist_ok=True)

# 数据库连接URL
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"

# 创建数据库引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

# 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def db_session():
    # 创建会话的实例
    session = SessionLocal()
    try:
        # 将session交给调用方使用
        yield session
    except Exception as e:
        logger.error(f"数据库会话错误:{e}")
        raise
    finally:
        session.close()


@contextmanager
def db_transaction():
    # 创建会话的实例
    session = SessionLocal()
    try:
        # 将session交给调用方使用
        yield session
        # 事务正常结束可以自动提交
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"数据库事务错误:{e}")
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"数据库会话错误:{e}")
        raise
    finally:
        session.close()


def init_db():
    try:
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
        print("  6. invitations                 - 统一邀请表（平台/工作空间）")
        print("  7. invitation_uses             - 邀请使用记录表")
        print("  8. permissions                 - 权限表")
        print("  9. user_permissions            - 用户权限关联表")
        print("  10. notifications              - 系统通知表")
        
        print("\n核心设计：")
        print("  ✓ 所有用户关联使用 openid（String类型）")
        print("  ✓ 所有表继承 BaseModel（自动包含软删除和时间戳字段）")
        print("  ✓ 双邀请系统：平台邀请激活用户 + 工作空间邀请加入空间")
        print("  ✓ 颗粒化权限控制：route/api/feature 三级权限")
        print("  ✓ 用户默认状态 inactive，需平台邀请码激活")
        
        print("\n表结构详情：")
        print("  【users】")
        print("    - status: 默认 'inactive'，需邀请码激活")
        print("    - platform_invitation_token: 激活时使用的平台邀请token")
        print("    - activated_at: 激活时间")
        
        print("  【invitations】")
        print("    - type: 'platform'（平台邀请）/ 'workspace'（工作空间邀请）")
        print("    - workspace_id + role: workspace类型时使用")
        print("    - permissions: platform类型时使用（JSON数组）")
        print("    - 统一管理两类邀请，简化表结构")
        
        print("  【permissions】")
        print("    - code: 权限代码（如 route.dashboard, api.bill.create）")
        print("    - type: route/api/feature")
        print("    - resource: 资源标识（路由路径/API端点/功能代码）")
        
        print("  【user_permissions】")
        print("    - 用户与权限的多对多关联")
        print("    - granted_by: 授予者openid（系统授予时为空）")
        
        print("\n索引信息：")
        print("  - users.openid (唯一索引)")
        print("  - workspaces.owner_openid (普通索引)")
        print("  - workspace_members (workspace_id, member_openid, is_deleted) 复合唯一索引")
        print("  - file_uploads (workspace_id, file_hash, is_deleted, status) 复合唯一索引")
        print("  - bills (workspace_id, trade_date, is_deleted) 复合索引")
        print("  - invitations.token (唯一索引)")
        print("  - invitations (workspace_id, token, is_deleted) 复合索引")
        print("  - invitations.type (普通索引)")
        print("  - invitation_uses (invitation_id, user_openid) 复合唯一索引")
        print("  - permissions.code (唯一索引)")
        print("  - permissions (type, status, is_deleted) 复合索引")
        print("  - user_permissions (user_openid, permission_id, is_deleted) 复合唯一索引")
        
        print("\n外键关系：")
        print("  - file_uploads.workspace_id → workspaces.id")
        print("  - workspace_members.workspace_id → workspaces.id (CASCADE)")
        print("  - bills.file_upload_id → file_uploads.id (CASCADE)")
        print("  - bills.workspace_id → workspaces.id")
        print("  - invitations.workspace_id → workspaces.id")
        print("  - invitation_uses.invitation_id → invitations.id")
        print("  - user_permissions.user_openid → users.openid")
        print("  - user_permissions.permission_id → permissions.id")
        
        print("\n权限模型：")
        print("  【工作空间角色权限】")
        print("    - owner   : 完全控制权（删除空间、管理成员、创建任意角色邀请）")
        print("    - editor  : 可编辑数据（上传文件、编辑账单、创建editor/viewer邀请）")
        print("    - viewer  : 只读权限（查看账单）")
        
        print("  【系统权限（通过 permissions 表管理）】")
        print("    - route.*     : 页面路由访问权限")
        print("    - api.*       : API接口调用权限")
        print("    - feature.*   : 功能开关权限")
        
        print("\n邀请系统：")
        print("  【平台邀请（type='platform'）】")
        print("    - 用途：激活新用户（inactive → active）")
        print("    - 可配置默认授予的权限列表（permissions字段）")
        print("    - 独立于工作空间，系统级别管理")
        
        print("  【工作空间邀请（type='workspace'）】")
        print("    - 用途：邀请已激活用户加入工作空间")
        print("    - viewer 角色无法创建邀请")
        print("    - editor 可创建 editor/viewer 邀请")
        print("    - owner 可创建任意角色邀请")
        print("    - 邀请角色不能高于创建者自身角色")
        
        print("  【通用规则】")
        print("    - 默认有效期：7天")
        print("    - 默认使用次数限制：10次")
        print("    - token 使用 secrets.token_urlsafe(32) 生成（43字符）")
        print("    - 撤销工作空间邀请会自动移除通过该邀请加入的成员（软删除）")
        
        print("\n用户激活流程：")
        print("  1. 新用户微信登录 → 创建 users 记录（status='inactive'）")
        print("  2. 种子用户自动激活 → status='active'（从 .env 读取 SEED_USERS）")
        print("  3. 普通用户需输入平台邀请码")
        print("  4. 校验平台邀请（type='platform'）→ 更新 status='active'")
        print("  5. 自动授予邀请预设权限 → 写入 user_permissions 表")
        print("  6. 记录激活信息 → platform_invitation_token + activated_at")
        
        print("\n软删除说明：")
        print("  - 所有表继承 BaseModel，自动包含：")
        print("    • is_deleted (Boolean, default=False, indexed)")
        print("    • deleted_at (DateTime, nullable)")
        print("    • created_at (DateTime, auto)")
        print("  - 删除操作仅标记 is_deleted=True，不物理删除")
        print("  - 查询时需过滤 is_deleted=False")
        print("  - 唯一索引包含 is_deleted 字段，允许同数据恢复")
        print("  - 空间删除会级联软删除：成员、文件、账单")
        print("  - 工作空间邀请撤销会级联软删除：通过该邀请加入的成员")
        
        print("\n⚠️  注意事项：")
        print("  1. 用户关联字段统一使用 openid（非 user_id）")
        print("  2. 用户默认状态为 inactive，必须通过平台邀请或种子用户身份激活")
        print("  3. 种子用户列表在 .env 中配置（SEED_USERS=openid1,openid2,openid3）")
        print("  4. 平台邀请和工作空间邀请共用 invitations 表，通过 type 字段区分")
        print("  5. 权限系统需在首次启动时初始化权限数据（运行 init_permissions.py）")
        print("  6. BaseModel 自动处理 to_dict() 的日期和 Decimal 类型转换")
        print("  7. 空间删除会级联软删除成员、文件、账单记录")
        print("  8. 文件删除会级联软删除账单记录")
        
        print("\n环境变量配置：")
        print("  必需配置：")
        print("    - JWT_SECRET_KEY: JWT签名密钥")
        print("    - DEEPSEEK_API_KEY: DeepSeek API密钥")
        print("  可选配置：")
        print("    - SEED_USERS: 种子用户列表（逗号分隔的openid）")
        print("    - JWT_ALGORITHM: JWT算法（默认 HS256）")
        print("    - JWT_ACCESS_TOKEN_EXPIRE_HOURS: token过期时间（默认 24小时）")
        
        print("=" * 60)
    except Exception as e:
        logger.error(f"初始化数据库失败:{e}")
        raise