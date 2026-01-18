"""邀请服务"""

import secrets
from datetime import datetime, timedelta
from app.models import Invitation, InvitationUse, WorkspaceMember, User
from app.database import db_session, db_transaction
from app.services.workspace_service import get_workspace_detail
from app.utils import get_logger, writeMessage, check_workspace_permission

logger = get_logger(__name__)

# 常量定义
INVITATION_TYPES = {"platform", "workspace"}
WORKSPACE_ROLES = {"editor", "viewer"}
ROLE_LEVELS = {"owner": 3, "editor": 2, "viewer": 1}
INVITATION_EXPIRE_DAYS = 7
INVITATION_MAX_USES = 10


def create_invitation(
    openid: str,
    invitation_type: str,
    workspace_id: str = None,
    role: str = None,
    base_url: str = None,
) -> dict:
    """
    创建邀请码(统一处理平台邀请和工作空间邀请)

    Args:
        openid: 创建者openid
        invitation_type: 邀请类型 'platform'/'workspace'
        workspace_id: 工作空间ID(workspace类型必填)
        role: 邀请角色(workspace类型必填: editor/viewer)
        base_url: 前端域名
    """
    # 1. 参数校验
    if invitation_type not in INVITATION_TYPES:
        raise ValueError(f"邀请类型必须是: {', '.join(INVITATION_TYPES)}")

    if invitation_type == "workspace":
        # 必填参数校验
        if not workspace_id or not role:
            raise ValueError("工作空间邀请必须提供workspace_id和role")

        # 角色值校验
        if role not in WORKSPACE_ROLES:
            raise ValueError(f"邀请角色只能是: {', '.join(WORKSPACE_ROLES)}")

        # 权限校验
        has_permission, user_role = check_workspace_permission(workspace_id, openid)
        if not has_permission:
            raise ValueError("无权限访问该空间")

        # 合并权限检查：viewer无权限 + 不能授予高于自身角色
        user_level = ROLE_LEVELS.get(user_role, 0)
        role_level = ROLE_LEVELS.get(role, 0)

        if user_level < 2:  # viewer权限不足
            raise ValueError("viewer 角色无法创建邀请")

        if role_level > user_level:
            raise ValueError(f"无法创建高于自身权限的邀请，您的角色为: {user_role}")

    # 2. 查询已有邀请码
    with db_session() as db:
        base_filters = [
            Invitation.created_by_openid == openid,
            Invitation.type == invitation_type,
            Invitation.status == "active",
            Invitation.is_deleted == False,
            Invitation.expires_at > datetime.now(),
        ]

        if workspace_id:
            base_filters.extend(
                [
                    Invitation.workspace_id == workspace_id,
                    Invitation.role == role,
                ]
            )

        existing = db.query(Invitation).filter(*base_filters).first()

        if existing:
            result = existing.to_dict()
            if base_url and invitation_type == "workspace":
                result["share_url"] = (
                    f"{base_url}/dashboard?join={existing.token}&type=workspace"
                )
            logger.info(
                writeMessage(
                    f"返回已有邀请码 - type: {invitation_type}, token: {existing.token}"
                )
            )
            return result

    # 3. 创建新邀请码
    with db_transaction() as db:
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(days=INVITATION_EXPIRE_DAYS)

        invitation = Invitation(
            token=token,
            type=invitation_type,
            workspace_id=workspace_id,
            role=role,
            created_by_openid=openid,
            expires_at=expires_at,
            max_uses=INVITATION_MAX_USES,
            used_count=0,
            status="active",
        )

        db.add(invitation)
        db.flush()
        db.refresh(invitation)

        logger.info(
            writeMessage(
                f"创建邀请成功 - type: {invitation_type}, "
                f"workspace_id: {workspace_id}, role: {role}, creator: {openid}"
            )
        )

        result = invitation.to_dict()
        if base_url and invitation_type == "workspace":
            result["share_url"] = f"{base_url}/dashboard?join={token}"

        return result


def join_by_invitation(token: str, openid: str) -> dict:
    """通过邀请码加入"""
    with db_transaction() as db:
        invitation = (
            db.query(Invitation)
            .filter(Invitation.token == token, Invitation.is_deleted == False)
            .first()
        )
        # print("invitation: ", invitation.to_dict())
        if not invitation:
            raise ValueError("邀请链接无效")

        if invitation.status != "active":
            raise ValueError("邀请已失效")

        if invitation.expires_at < datetime.now():
            raise ValueError("邀请已过期")

        if invitation.used_count >= invitation.max_uses:
            raise ValueError("邀请已达使用上限")

        # 检查是否已使用过该邀请
        existing_use = (
            db.query(InvitationUse)
            .filter(
                InvitationUse.invitation_id == invitation.id,
                InvitationUse.user_openid == openid,
            )
            .first()
        )

        if existing_use:
            if invitation.type == "platform":
                return {"type": "platform", "message": "您已使用过该邀请码"}
            else:
                workspace_detail = get_workspace_detail(invitation.workspace_id, openid)
                return {
                    "type": "workspace",
                    "workspace_id": invitation.workspace_id,
                    "workspace_name": workspace_detail["name"],
                    "role": invitation.role,
                    "message": "您已是该空间成员",
                }

        now = datetime.now()

        # 平台邀请处理
        if invitation.type == "platform":
            user = db.query(User).filter(User.openid == openid).first()
            if not user:
                raise ValueError("用户不存在")

            user.status = "active"
            user.platform_invitation_token = token
            user.activated_at = now
            user.updated_at = now

            # 记录邀请使用
            use_record = InvitationUse(
                invitation_id=invitation.id,
                user_openid=openid,
                invitation_type="platform",
                used_at=now,
            )
            db.add(use_record)

            invitation.used_count += 1
            invitation.updated_at = now

            logger.info(
                writeMessage(f"平台邀请激活用户 - user: {openid}, token: {token}")
            )

            return {
                "type": "platform",
                "user": user.to_dict(),
                "activated_at": now.isoformat(),
                "message": "账号已激活",
            }

        # 工作空间邀请处理
        elif invitation.type == "workspace":
            # 检查空间成员
            existing_member = (
                db.query(WorkspaceMember)
                .filter(
                    WorkspaceMember.workspace_id == invitation.workspace_id,
                    WorkspaceMember.member_openid == openid,
                    WorkspaceMember.is_deleted == False,
                )
                .first()
            )
            # existing_member = openid in [user.member_openid for user in workspace_members]
            if existing_member:
                workspace_detail = get_workspace_detail(
                    invitation.workspace_id, invitation.created_by_openid
                )
                return {
                    "type": "workspace",
                    "workspace_id": invitation.workspace_id,
                    "workspace_name": workspace_detail["name"],
                    "role": existing_member.role,
                    "message": "您已是该空间成员",
                }
            # 添加为成员
            member = WorkspaceMember(
                workspace_id=invitation.workspace_id,
                member_openid=openid,
                role=invitation.role,
                status="active",
                granted_at=now,
            )
            db.add(member)

            # 自动激活用户
            user = db.query(User).filter(User.openid == openid).first()
            if user and user.status == "inactive":
                user.status = "active"
                user.activated_at = now
                user.updated_at = now

            # 记录邀请使用
            use_record = InvitationUse(
                invitation_id=invitation.id,
                user_openid=openid,
                invitation_type="workspace",
                used_at=now,
            )
            db.add(use_record)

            invitation.used_count += 1
            invitation.updated_at = now

            workspace_detail = get_workspace_detail(
                invitation.workspace_id, invitation.created_by_openid
            )

            logger.info(
                writeMessage(
                    f"用户通过邀请加入空间 - workspace_id: {invitation.workspace_id}, "
                    f"user: {openid}, role: {invitation.role}"
                )
            )

            return {
                "type": "workspace",
                "workspace_id": invitation.workspace_id,
                "workspace_name": workspace_detail["name"],
                "role": invitation.role,
                "joined_at": now.isoformat(),
            }


def get_invitations(
    openid: str, invitation_type: str = None, workspace_id: str = None
) -> list:
    """获取邀请列表（优化版）"""
    with db_session() as db:
        # 1. 构建过滤条件
        base_filters = [
            Invitation.created_by_openid == openid,
            Invitation.status == "active",
            Invitation.is_deleted == False,
            Invitation.expires_at > datetime.now(),
        ]

        if invitation_type:
            base_filters.append(Invitation.type == invitation_type)

        if workspace_id:
            base_filters.append(Invitation.workspace_id == workspace_id)

        # 2. 查询邀请列表
        invitations = (
            db.query(Invitation)
            .filter(*base_filters)
            .order_by(Invitation.created_at.desc())
            .all()
        )

        if not invitations:
            return []

        # 3. 批量查询创建者信息
        creator_openids = list(set(inv.created_by_openid for inv in invitations))
        creators = db.query(User).filter(User.openid.in_(creator_openids)).all()
        creator_map = {creator.openid: creator.nickname for creator in creators}

        # 4. 批量查询使用记录 + 用户信息（一次 JOIN）
        invitation_ids = [inv.id for inv in invitations]
        uses_with_users = (
            db.query(
                InvitationUse.invitation_id,
                InvitationUse.user_openid,
                InvitationUse.used_at,
                User.nickname,
            )
            .outerjoin(User, InvitationUse.user_openid == User.openid)
            .filter(InvitationUse.invitation_id.in_(invitation_ids))
            .all()
        )

        # 5. 按 invitation_id 分组
        uses_by_invitation = {}
        for use in uses_with_users:
            if use.invitation_id not in uses_by_invitation:
                uses_by_invitation[use.invitation_id] = []
            uses_by_invitation[use.invitation_id].append(
                {
                    "openid": use.user_openid,
                    "nickname": use.nickname,
                    "joined_at": use.used_at.isoformat() if use.used_at else None,
                    "used_at": use.used_at.isoformat() if use.used_at else None,
                }
            )

        # 6. 组装结果
        result = []
        for inv in invitations:
            inv_dict = inv.to_dict()

            # 添加创建者信息
            inv_dict["creator"] = {
                "openid": inv.created_by_openid,
                "nickname": creator_map.get(inv.created_by_openid),
            }

            # 添加使用记录
            inv_dict["joined_members"] = uses_by_invitation.get(inv.id, [])

            result.append(inv_dict)

        return result


def get_invitation_uses(openid: str, limit: int = None) -> list:
    """获取邀请使用记录"""
    with db_session() as db:
        # 使用 JOIN 一次性获取所有数据
        query = (
            db.query(
                InvitationUse.invitation_type,
                InvitationUse.user_openid,
                InvitationUse.used_at,
                User.nickname,
                User.headimgurl,
                Invitation.created_at.label("invitation_created_at"),
                Invitation.role,
            )
            .join(Invitation, InvitationUse.invitation_id == Invitation.id)
            .outerjoin(User, InvitationUse.user_openid == User.openid)
            .filter(
                Invitation.created_by_openid == openid, Invitation.is_deleted == False
            )
            .order_by(InvitationUse.used_at.desc())
        )

        if limit:
            query = query.limit(limit)

        uses = query.all()
        logger.info(writeMessage(f"len(uses): {len(uses)}"))
        # 组装结果
        return [
            {
                "invitation_type": use.invitation_type,
                "user": {
                    "openid": use.user_openid,
                    "nickname": use.nickname,  # 来自 JOIN 的 User 表
                    "headimgurl": use.headimgurl,  # 来自 JOIN 的 User 表
                },
                "role": use.role,
                "used_at": use.used_at.isoformat() if use.used_at else None,
                "invitation_created_at": (
                    use.invitation_created_at.isoformat()
                    if use.invitation_created_at
                    else None
                ),
            }
            for use in uses
        ]
