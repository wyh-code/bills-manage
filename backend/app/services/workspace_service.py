"""账务空间服务"""

from datetime import datetime
from app.models import Workspace, WorkspaceMember, User, FileUpload, Bill
from app.database import db_session, db_transaction
from app.utils import get_logger

logger = get_logger(__name__)


def _get_user_info(openid: str) -> dict:
    """获取用户信息(独立创建session)"""
    with db_session() as db:
        user = (
            db.query(User)
            .filter(User.openid == openid, User.is_deleted == False)
            .first()
        )

        if not user:
            return {"openid": openid, "nickname": None, "headimgurl": None}

        return {
            "openid": user.openid,
            "nickname": user.nickname,
            "headimgurl": user.headimgurl,
        }


def _get_workspace_members(workspace_id: str) -> list:
    """获取空间所有成员信息"""
    with db_session() as db:
        # 一次性查询所有成员和用户信息
        members_with_users = (
            db.query(WorkspaceMember, User)
            .outerjoin(User, WorkspaceMember.member_openid == User.openid)
            .filter(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.is_deleted == False,
            )
            .all()
        )

        member_list = []
        for member, user in members_with_users:
            member_list.append(
                {
                    "openid": member.member_openid,
                    "nickname": user.nickname if user else None,
                    "headimgurl": user.headimgurl if user else None,
                    "role": member.role,
                    "granted_at": (
                        member.granted_at.isoformat() if member.granted_at else None
                    ),
                }
            )

        return member_list


def create_workspace(openid: str, name: str, description: str = None) -> dict:
    """创建空间并自动添加创建者为owner"""
    with db_transaction() as db:
        workspace = Workspace(
            name=name, description=description, status="active", owner_openid=openid
        )
        db.add(workspace)
        db.flush()
        db.refresh(workspace)

        # 添加owner成员记录
        member = WorkspaceMember(
            workspace_id=workspace.id, member_openid=openid, role="owner"
        )
        db.add(member)

        logger.info(f"创建空间成功 - workspace_id: {workspace.id}, owner: {openid}")
        return workspace.to_dict()


def get_user_workspaces(openid: str, status: str = None, role: str = None) -> list:
    """
    获取用户有权限的所有空间(优化版 - 批量查询)

    Args:
        openid: 用户openid
        status: 可选,过滤空间状态 (active/inactive)
        role: 可选,过滤用户角色 (owner/editor/viewer),返回大于等于该角色权限的空间

    Returns:
        空间列表(包含用户角色、成员、创建者信息)
    """
    with db_session() as db:
        members = (
            db.query(WorkspaceMember)
            .filter(
                WorkspaceMember.member_openid == openid,
                WorkspaceMember.is_deleted == False,
            )
            .all()
        )

        # 角色权限过滤
        if role:
            role_levels = {"owner": 3, "editor": 2, "viewer": 1}
            required_level = role_levels.get(role, 0)

            members = [
                m for m in members if role_levels.get(m.role, 0) >= required_level
            ]

        workspace_ids = [m.workspace_id for m in members]

        if not workspace_ids:
            return []

        # 构建空间查询
        query = db.query(Workspace).filter(
            Workspace.id.in_(workspace_ids),
            Workspace.is_deleted == False,
        )

        if status is not None:
            query = query.filter(Workspace.status == status)

        workspaces = query.all()

        # 1. 批量查询所有空间的创建者信息
        owner_openids = list(set(ws.owner_openid for ws in workspaces))
        owners = db.query(User).filter(User.openid.in_(owner_openids)).all()
        owner_map = {
            owner.openid: {
                "openid": owner.openid,
                "nickname": owner.nickname,
                "headimgurl": owner.headimgurl,
            }
            for owner in owners
        }

        # 2. 批量查询所有空间的成员信息
        all_members_with_users = (
            db.query(WorkspaceMember, User)
            .outerjoin(User, WorkspaceMember.member_openid == User.openid)
            .filter(
                WorkspaceMember.workspace_id.in_(workspace_ids),
                WorkspaceMember.is_deleted == False,
            )
            .all()
        )

        # 按 workspace_id 组织成员数据
        members_by_workspace = {}
        for member, user in all_members_with_users:
            if member.workspace_id not in members_by_workspace:
                members_by_workspace[member.workspace_id] = []

            members_by_workspace[member.workspace_id].append(
                {
                    "openid": member.member_openid,
                    "nickname": user.nickname if user else None,
                    "headimgurl": user.headimgurl if user else None,
                    "role": member.role,
                    "granted_at": (
                        member.granted_at.isoformat() if member.granted_at else None
                    ),
                }
            )

        # 3. 组装结果
        member_map = {m.workspace_id: m.role for m in members}
        result = []

        for ws in workspaces:
            ws_dict = ws.to_dict()
            ws_dict["user_role"] = member_map.get(ws.id)

            # 从预加载的数据中获取(避免额外查询)
            ws_dict["owner"] = owner_map.get(
                ws.owner_openid,
                {"openid": ws.owner_openid, "nickname": None, "headimgurl": None},
            )
            ws_dict["members"] = members_by_workspace.get(ws.id, [])

            result.append(ws_dict)

        return result


def get_workspace_detail(workspace_id: str, openid: str) -> dict:
    """获取空间详情(需验证权限)"""
    with db_session() as db:
        workspace = (
            db.query(Workspace)
            .filter(Workspace.id == workspace_id, Workspace.is_deleted == False)
            .first()
        )

        if not workspace:
            raise ValueError("空间不存在")

        # 验证权限
        member = (
            db.query(WorkspaceMember)
            .filter(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.member_openid == openid,
                WorkspaceMember.is_deleted == False,
            )
            .first()
        )

        if not member:
            raise ValueError("无权限访问该空间")

        # 组装数据
        ws_dict = workspace.to_dict()
        ws_dict["user_role"] = member.role

        # 获取创建者信息
        owner_info = _get_user_info(workspace.owner_openid)
        ws_dict["owner"] = owner_info

        # 获取成员列表
        members_list = _get_workspace_members(workspace.id)
        ws_dict["members"] = members_list

        return ws_dict


def update_workspace(
    workspace_id: str,
    openid: str,
    name: str = None,
    description: str = None,
    status: str = None,
):
    """更新空间(仅owner)"""
    with db_transaction() as db:
        workspace = (
            db.query(Workspace)
            .filter(Workspace.id == workspace_id, Workspace.is_deleted == False)
            .first()
        )

        if not workspace:
            raise ValueError("空间不存在")

        if workspace.owner_openid != openid:
            raise ValueError("仅空间所有者可以修改")

        if name is not None:
            workspace.name = name
        if description is not None:
            workspace.description = description
        if status is not None:
            workspace.status = status

        workspace.updated_at = datetime.now()

        logger.info(f"更新空间成功 - workspace_id: {workspace_id}")
        return workspace.to_dict()


def delete_workspace(workspace_id: str, openid: str) -> dict:
    """软删除空间(仅owner)"""
    with db_transaction() as db:
        workspace = (
            db.query(Workspace)
            .filter(Workspace.id == workspace_id, Workspace.is_deleted == False)
            .first()
        )

        if not workspace:
            raise ValueError("空间不存在")

        if workspace.owner_openid != openid:
            raise ValueError("仅空间所有者可以删除")

        now = datetime.now()

        # 软删除空间
        workspace.is_deleted = True
        workspace.deleted_at = now
        workspace.updated_at = now

        # 软删除成员记录
        member_count = (
            db.query(WorkspaceMember)
            .filter(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.is_deleted == False,
            )
            .update(
                {"is_deleted": True, "deleted_at": now, "updated_at": now},
                synchronize_session=False,
            )
        )

        # 软删除文件记录
        file_count = (
            db.query(FileUpload)
            .filter(
                FileUpload.workspace_id == workspace_id, FileUpload.is_deleted == False
            )
            .update(
                {"is_deleted": True, "deleted_at": now, "updated_at": now},
                synchronize_session=False,
            )
        )

        # 软删除账单
        bill_count = (
            db.query(Bill)
            .filter(Bill.workspace_id == workspace_id, Bill.is_deleted == False)
            .update(
                {"is_deleted": True, "deleted_at": now, "updated_at": now},
                synchronize_session=False,
            )
        )

        logger.info(
            f"删除空间成功 - workspace_id: {workspace_id}, "
            f"成员: {member_count}, 文件: {file_count}, 账单: {bill_count}"
        )

        return {
            "workspace_id": workspace_id,
            "deleted_members": member_count,
            "deleted_files": file_count,
            "deleted_bills": bill_count,
        }
