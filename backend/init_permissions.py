"""权限数据初始化脚本"""

import sys
import os
import argparse
from datetime import datetime
import traceback

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from app.models import Permission
from app.utils import get_logger

logger = get_logger(__name__)

# 权限定义
PERMISSIONS = [
    # ==================== 路由权限 (route) ====================
    {
        "code": "route.dashboard",
        "name": "访问工作台",
        "type": "route",
        "resource": "/dashboard",
        "description": "访问工作台页面",
    },
    {
        "code": "route.upload",
        "name": "访问上传页",
        "type": "route",
        "resource": "/upload",
        "description": "访问账单上传页面",
    },
    {
        "code": "route.bills",
        "name": "访问账单查询",
        "type": "route",
        "resource": "/bills",
        "description": "访问账单查询页面",
    },
    {
        "code": "route.summary",
        "name": "访问汇总页",
        "type": "route",
        "resource": "/summary",
        "description": "访问账单汇总页面",
    },
    # ==================== 工作空间 API 权限 ====================
    {
        "code": "api.workspace.create",
        "name": "创建工作空间",
        "type": "api",
        "resource": "POST /api/workspaces",
        "description": "创建新的工作空间",
    },
    {
        "code": "api.workspace.view",
        "name": "查看工作空间",
        "type": "api",
        "resource": "GET /api/workspaces",
        "description": "查看工作空间列表和详情",
    },
    {
        "code": "api.workspace.update",
        "name": "更新工作空间",
        "type": "api",
        "resource": "PUT /api/workspaces/:id",
        "description": "更新工作空间信息（仅owner）",
    },
    {
        "code": "api.workspace.delete",
        "name": "删除工作空间",
        "type": "api",
        "resource": "DELETE /api/workspaces/:id",
        "description": "删除工作空间（仅owner）",
    },
    {
        "code": "api.workspace.invite",
        "name": "创建工作空间邀请",
        "type": "api",
        "resource": "POST /api/workspaces/:id/invitations",
        "description": "创建工作空间邀请链接",
    },
    # ==================== 文件 API 权限 ====================
    {
        "code": "api.file.upload",
        "name": "上传文件",
        "type": "api",
        "resource": "POST /api/files/upload",
        "description": "上传账单文件",
    },
    {
        "code": "api.file.view",
        "name": "查看文件",
        "type": "api",
        "resource": "GET /api/files/:id",
        "description": "查看文件详情和进度",
    },
    {
        "code": "api.file.download",
        "name": "下载文件",
        "type": "api",
        "resource": "GET /api/files/:id?download=true",
        "description": "下载原始文件",
    },
    # ==================== 账单 API 权限 ====================
    {
        "code": "api.bill.view",
        "name": "查看账单",
        "type": "api",
        "resource": "GET /api/bills",
        "description": "查看账单列表和详情",
    },
    {
        "code": "api.bill.create",
        "name": "创建账单",
        "type": "api",
        "resource": "POST /api/bills/create",
        "description": "手动创建账单",
    },
    {
        "code": "api.bill.update",
        "name": "更新账单",
        "type": "api",
        "resource": "PUT /api/bills/:id",
        "description": "更新账单信息",
    },
    {
        "code": "api.bill.delete",
        "name": "删除账单",
        "type": "api",
        "resource": "DELETE /api/bills/:id",
        "description": "删除账单记录",
    },
    {
        "code": "api.bill.confirm",
        "name": "确认账单",
        "type": "api",
        "resource": "POST /api/bills/batch",
        "description": "批量确认账单状态",
    },
    {
        "code": "api.bill.pay",
        "name": "结算账单",
        "type": "api",
        "resource": "PUT /api/bills/update",
        "description": "标记账单为已支付",
    },
    # ==================== 功能权限 (feature) ====================
    {
        "code": "feature.batch_operation",
        "name": "批量操作",
        "type": "feature",
        "resource": "batch_operations",
        "description": "批量确认、批量结算等操作",
    },
    {
        "code": "feature.export_data",
        "name": "导出数据",
        "type": "feature",
        "resource": "data_export",
        "description": "导出账单数据为Excel/CSV",
    },
    {
        "code": "feature.view_statistics",
        "name": "查看统计",
        "type": "feature",
        "resource": "statistics_view",
        "description": "查看账单统计和汇总数据",
    },
    {
        "code": "feature.advanced_search",
        "name": "高级搜索",
        "type": "feature",
        "resource": "advanced_search",
        "description": "使用高级搜索功能",
    },
]


def init_permissions():
    """初始化权限数据"""
    db = SessionLocal()

    try:
        print("=" * 60)
        print("开始初始化权限数据...")
        print("=" * 60)

        # 统计
        created_count = 0
        skipped_count = 0
        updated_count = 0

        for perm_data in PERMISSIONS:
            # 检查权限是否已存在
            existing = (
                db.query(Permission)
                .filter(
                    Permission.code == perm_data["code"], Permission.is_deleted == False
                )
                .first()
            )

            if existing:
                # 权限已存在，检查是否需要更新
                need_update = False

                if existing.name != perm_data["name"]:
                    existing.name = perm_data["name"]
                    need_update = True

                if existing.type != perm_data["type"]:
                    existing.type = perm_data["type"]
                    need_update = True

                if existing.resource != perm_data["resource"]:
                    existing.resource = perm_data["resource"]
                    need_update = True

                if existing.description != perm_data["description"]:
                    existing.description = perm_data["description"]
                    need_update = True

                if need_update:
                    db.add(existing) 
                    updated_count += 1
                    logger.info(f"更新权限: {perm_data['code']}")
                else:
                    skipped_count += 1
            else:
                # 创建新权限
                permission = Permission(**perm_data)
                db.add(permission)
                created_count += 1
                logger.info(f"创建权限: {perm_data['code']}")

        # 提交事务
        db.commit()

        print("\n✅ 权限数据初始化完成！")
        print(f"📊 统计信息:")
        print(f"   - 新创建: {created_count} 条")
        print(f"   - 已更新: {updated_count} 条")
        print(f"   - 已存在: {skipped_count} 条")
        print(f"   - 总计: {len(PERMISSIONS)} 条权限")

        print("\n权限分类统计:")
        route_perms = [p for p in PERMISSIONS if p["type"] == "route"]
        api_perms = [p for p in PERMISSIONS if p["type"] == "api"]
        feature_perms = [p for p in PERMISSIONS if p["type"] == "feature"]

        print(f"   - 路由权限 (route): {len(route_perms)} 条")
        print(f"   - API权限 (api): {len(api_perms)} 条")
        print(f"   - 功能权限 (feature): {len(feature_perms)} 条")

        print("\n💡 提示:")
        print("   1. 可通过平台邀请码的 permissions 字段预设用户权限")
        print("   2. 可在管理后台动态授予/撤销用户权限")
        print("   3. 工作空间角色权限(owner/editor/viewer)独立于系统权限")
        print("=" * 60)

        return True

    except Exception as e:
        db.rollback()
        logger.error(f"❌ 权限数据初始化失败: {e}")

        logger.error(traceback.format_exc())
        return False

    finally:
        db.close()


def list_permissions():
    """列出所有权限"""
    db = SessionLocal()

    try:
        permissions = (
            db.query(Permission)
            .filter(Permission.is_deleted == False)
            .order_by(Permission.type, Permission.code)
            .all()
        )

        print("\n" + "=" * 60)
        print("当前系统权限列表")
        print("=" * 60)

        current_type = None
        for perm in permissions:
            if perm.type != current_type:
                current_type = perm.type
                print(f"\n【{perm.type.upper()}】")

            print(f"  • {perm.code}")
            print(f"    名称: {perm.name}")
            print(f"    资源: {perm.resource}")
            print(f"    状态: {perm.status}")

        print("\n" + "=" * 60)
        print(f"共 {len(permissions)} 条权限")
        print("=" * 60)

    except Exception as e:
        logger.error(f"查询权限失败: {e}")
    finally:
        db.close()


def clear_permissions():
    """清空所有权限（软删除）"""
    db = SessionLocal()

    try:
        count = (
            db.query(Permission)
            .filter(Permission.is_deleted == False)
            .update({"is_deleted": True, "deleted_at": datetime.now()})
        )

        db.commit()

        print(f"✅ 已软删除 {count} 条权限")
        logger.info(f"清空权限数据: {count} 条")

    except Exception as e:
        db.rollback()
        logger.error(f"清空权限失败: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    

    parser = argparse.ArgumentParser(description="权限数据管理工具")
    parser.add_argument(
        "action",
        choices=["init", "list", "clear"],
        help="操作类型: init(初始化), list(列表), clear(清空)",
    )

    args = parser.parse_args()

    if args.action == "init":
        success = init_permissions()
        sys.exit(0 if success else 1)
    elif args.action == "list":
        list_permissions()
    elif args.action == "clear":
        confirm = input("⚠️  确认要清空所有权限吗？(yes/no): ")
        if confirm.lower() == "yes":
            clear_permissions()
        else:
            print("已取消操作")
