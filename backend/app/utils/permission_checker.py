"""权限校验工具"""

from app.models import WorkspaceMember
from app.database import db_session


def check_workspace_permission(
    workspace_id: str, openid: str, required_role: str = None
) -> tuple[bool, str | None]:
    """
    检查用户空间权限(独立创建session)

    Args:
        workspace_id: 空间ID
        openid: 用户openid
        required_role: 要求的角色 'owner'/'editor'/'viewer' 或 None

    Returns:
        (has_permission: bool, user_role: str | None)
    """
    with db_session() as db:
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
            return False, None

        # 如果不需要特定角色,只要是成员即可
        if required_role is None:
            return True, member.role

        # 角色等级: owner > editor > viewer
        role_levels = {"owner": 3, "editor": 2, "viewer": 1}
        user_level = role_levels.get(member.role, 0)
        required_level = role_levels.get(required_role, 0)

        return user_level >= required_level, member.role


def require_workspace_permission(
    workspace_id: str, openid: str, required_role: str = None, error_message: str = None
) -> str:
    """
    要求用户具有空间权限,否则抛出异常

    Args:
        workspace_id: 空间ID
        openid: 用户openid
        required_role: 要求的角色
        error_message: 自定义错误信息

    Returns:
        user_role: 用户角色

    Raises:
        ValueError: 权限不足
    """
    has_permission, user_role = check_workspace_permission(
        workspace_id, openid, required_role
    )

    if not has_permission:
        if error_message:
            raise ValueError(error_message)

        if required_role:
            raise ValueError(f"无权限执行此操作,需要{required_role}或更高角色")
        else:
            raise ValueError("无权限访问该空间")

    return user_role
