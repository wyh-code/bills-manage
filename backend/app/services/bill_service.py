"""账单管理服务"""

from datetime import datetime
from sqlalchemy import func, or_
from app.models import Bill, FileUpload, WorkspaceMember, User
from app.database import db_session, db_transaction
from app.utils import get_logger, writeMessage, require_workspace_permission

logger = get_logger(__name__)


def get_settlement_summary(openid: str, workspace_ids: list = None) -> dict:
    """
    获取结算汇总统计

    Returns:
        {
            'total': {...},  # 总金额
            'settled': {...},  # 已结算金额(payed)
            'unsettled': {...},  # 未结算金额(active/modified)
            'settled_percentage': float  # 结算比例
        }
    """
    with db_session() as db:
        # 获取用户有权限的所有空间
        members = (
            db.query(WorkspaceMember)
            .filter(
                WorkspaceMember.member_openid == openid,
                WorkspaceMember.is_deleted == False,
            )
            .all()
        )

        accessible_workspace_ids = [m.workspace_id for m in members]

        # 筛选空间
        if workspace_ids:
            accessible_workspace_ids = [
                wid for wid in workspace_ids if wid in accessible_workspace_ids
            ]

        # 查询所有已确认/已修改的账单
        bills = (
            db.query(Bill)
            .filter(
                Bill.workspace_id.in_(accessible_workspace_ids),
                Bill.is_deleted == False,
                or_(
                    Bill.status == "active",
                    Bill.status == "modified",
                    Bill.status == "payed",
                ),
            )
            .all()
        )

        total = {}
        settled = {}
        unsettled = {}
        if bills:
            for bill in bills:
                if bill.amount_cny:
                    currency = "CNY"
                    amount = float(bill.amount_cny)
                elif bill.amount_foreign and bill.currency:
                    currency = bill.currency
                    amount = float(bill.amount_foreign)
                else:
                    continue

                # 总计
                total[currency] = total.get(currency, 0) + amount

                # 分类统计
                if bill.status == "payed":
                    settled[currency] = settled.get(currency, 0) + amount
                else:
                    unsettled[currency] = unsettled.get(currency, 0) + amount

            # 计算结算比例(以CNY为基准)
            settled_percentage = 0
            if total.get("CNY", 0) > 0:
                settled_percentage = (settled.get("CNY", 0) / total.get("CNY", 0)) * 100

            return {
                "total": total,
                "settled": settled,
                "unsettled": unsettled,
                "settled_percentage": round(settled_percentage, 2),
            }

        return {
            "total": None,
            "settled": None,
            "unsettled": None,
            "settled_percentage": None,
        }


def get_bills(
    openid: str,
    workspace_ids: list = None,
    card_last4_list: list = None,
    status_list: list = None,
    start_date: str = None,
    end_date: str = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """
    分页查询账单列表

    Args:
        openid: 用户openid
        workspace_ids: 空间ID列表(多选)
        card_last4_list: 卡号末四位列表(多选)
        status_list: 账单状态列表
        start_date: 开始日期 YYYY-MM-DD
        end_date: 结束日期 YYYY-MM-DD
        page: 页码(从1开始)
        page_size: 每页数量

    Returns:
        {total, page, page_size, items}
    """
    with db_session() as db:

        # 获取用户有权限的所有空间
        members = (
            db.query(WorkspaceMember)
            .filter(
                WorkspaceMember.member_openid == openid,
                WorkspaceMember.is_deleted == False,
            )
            .all()
        )

        accessible_workspace_ids = [m.workspace_id for m in members]

        # 构建基础查询
        query = db.query(Bill).filter(
            Bill.workspace_id.in_(accessible_workspace_ids), Bill.is_deleted == False
        )

        # 筛选:指定空间
        if workspace_ids:
            filtered_ids = [
                wid for wid in workspace_ids if wid in accessible_workspace_ids
            ]
            if not filtered_ids:
                return {"total": 0, "page": page, "page_size": page_size, "items": []}
            query = query.filter(Bill.workspace_id.in_(filtered_ids))

        # 筛选:卡号
        if card_last4_list:
            query = query.filter(Bill.card_last4.in_(card_last4_list))

        # 筛选:状态
        if status_list:
            query = query.filter(Bill.status.in_(status_list))

        # 筛选:日期范围
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
                query = query.filter(Bill.trade_date >= start_dt)
            except ValueError:
                pass

        if end_date:
            try:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
                query = query.filter(Bill.trade_date <= end_dt)
            except ValueError:
                pass

        # 统计总数
        total = query.count()

        # 分页查询
        offset = (page - 1) * page_size
        bills = (
            query.order_by(Bill.trade_date.desc(), Bill.created_at.desc())
            .limit(page_size)
            .offset(offset)
            .all()
        )

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": [bill.to_dict() for bill in bills],
        }


def get_card_list(openid: str, workspace_ids: list = None) -> list:
    """
    获取卡号列表(用于筛选下拉)

    Args:
        openid: 用户openid
        workspace_ids: 可选,指定空间ID列表

    Returns:
        [{'card_last4': '1234', 'count': 10}, ...]
    """
    with db_session() as db:

        # 获取用户有权限的所有空间
        members = (
            db.query(WorkspaceMember)
            .filter(
                WorkspaceMember.member_openid == openid,
                WorkspaceMember.is_deleted == False,
            )
            .all()
        )

        accessible_workspace_ids = [m.workspace_id for m in members]

        # 构建查询
        query = db.query(Bill.card_last4, func.count(Bill.id).label("count")).filter(
            Bill.workspace_id.in_(accessible_workspace_ids),
            Bill.is_deleted == False,
            Bill.card_last4.isnot(None),
        )

        # 可选:按指定空间筛选
        if workspace_ids:
            filtered_ids = [
                wid for wid in workspace_ids if wid in accessible_workspace_ids
            ]
            if filtered_ids:
                query = query.filter(Bill.workspace_id.in_(filtered_ids))

        # 分组统计
        results = query.group_by(Bill.card_last4).order_by(Bill.card_last4).all()

        return [{"card_last4": card, "count": count} for card, count in results]


def batch_confirm_bills(
    workspace_id: str, file_id: str, bill_ids: list, openid: str
) -> dict:
    """
    批量确认账单(pending → active)

    Args:
        workspace_id: 空间ID
        file_id: 文件ID
        bill_ids: 要确认的账单ID列表
        openid: 操作用户openid

    Returns:
        {file_id, bills_count, updated_count, bills}
    """
    # 校验权限(需要editor及以上)
    require_workspace_permission(workspace_id, openid, required_role="editor")

    with db_transaction() as db:
        # 获取文件记录
        file_record = (
            db.query(FileUpload)
            .filter(
                FileUpload.id == file_id,
                FileUpload.workspace_id == workspace_id,
                FileUpload.is_deleted == False,
            )
            .first()
        )

        if not file_record:
            raise ValueError("文件记录不存在")

        # 批量更新账单状态
        updated_count = (
            db.query(Bill)
            .filter(
                Bill.id.in_(bill_ids),
                Bill.file_upload_id == file_id,
                Bill.workspace_id == workspace_id,
                Bill.is_deleted == False,
                Bill.status == "pending",
            )
            .update(
                {"status": "active", "updated_at": datetime.now()},
                synchronize_session=False,
            )
        )

        # 获取更新后的账单列表
        bills = (
            db.query(Bill).filter(Bill.id.in_(bill_ids), Bill.is_deleted == False).all()
        )

        logger.info(
            writeMessage(
                f"批量确认账单成功 - file_id: {file_id}, "
                f"updated: {updated_count}, total: {len(bills)}"
            )
        )

        return {
            "file_id": file_id,
            "bills_count": len(bills),
            "updated_count": updated_count,
            "bills": [bill.to_dict() for bill in bills],
        }


def get_bill_detail(workspace_id: str, bill_id: str, openid: str) -> dict:
    """获取单个账单详情"""
    # 校验权限
    require_workspace_permission(workspace_id, openid)

    with db_session() as db:
        bill = (
            db.query(Bill)
            .filter(
                Bill.id == bill_id,
                Bill.workspace_id == workspace_id,
                Bill.is_deleted == False,
            )
            .first()
        )

        if not bill:
            raise ValueError("账单不存在")

        return bill.to_dict()


def update_bill(openid: str, workspace_id: str, bill_id: str, update_data: dict):
    """更新账单"""
    # 校验权限(需要editor及以上)
    require_workspace_permission(workspace_id, openid, required_role="editor")

    with db_transaction() as db:
        bill = (
            db.query(Bill)
            .filter(
                Bill.id == bill_id,
                Bill.workspace_id == workspace_id,
                Bill.is_deleted == False,
            )
            .first()
        )

        if not bill:
            raise ValueError("账单不存在")

        # 更新字段
        if "bank" in update_data:
            bill.bank = update_data["bank"]

        if "trade_date" in update_data and update_data["trade_date"]:
            try:
                bill.trade_date = datetime.strptime(
                    update_data["trade_date"], "%Y-%m-%d"
                ).date()
            except ValueError:
                pass

        if "record_date" in update_data and update_data["record_date"]:
            try:
                bill.record_date = datetime.strptime(
                    update_data["record_date"], "%Y-%m-%d"
                ).date()
            except ValueError:
                pass

        if "description" in update_data:
            bill.description = update_data["description"]

        if "remark" in update_data:
            bill.remark = update_data["remark"]

        if "amount_cny" in update_data:
            bill.amount_cny = update_data["amount_cny"]

        if "card_last4" in update_data:
            bill.card_last4 = update_data["card_last4"]

        if "amount_foreign" in update_data:
            bill.amount_foreign = update_data["amount_foreign"]

        if "currency" in update_data:
            bill.currency = update_data["currency"]

        if "status" in update_data:
            bill.status = update_data["status"]

        bill.updated_at = datetime.now()
        logger.info(writeMessage(f"账单更新成功 - bill_id: {bill_id}"))

        return bill.to_dict()


def batch_update_bills(workspace_id: str, updates: list, openid: str) -> dict:
    """
    批量更新账单

    Args:
        workspace_id: 空间ID
        updates: [{'id': 'xxx', ...更新字段}, ...]
        openid: 操作用户openid

    Returns:
        {updated_count, failed_count, results}
    """
    # 校验权限(需要editor及以上)
    require_workspace_permission(workspace_id, openid, required_role="editor")

    updated_count = 0
    failed_count = 0
    results = []

    with db_transaction() as db:

        now = datetime.now()

        for item in updates:
            bill_id = item.get("id")

            if not bill_id:
                failed_count += 1
                results.append({"id": None, "success": False, "message": "id不能为空"})
                continue

            try:
                # 获取账单
                bill = (
                    db.query(Bill)
                    .filter(
                        Bill.id == bill_id,
                        Bill.workspace_id == workspace_id,
                        Bill.is_deleted == False,
                    )
                    .first()
                )

                if not bill:
                    failed_count += 1
                    results.append(
                        {"id": bill_id, "success": False, "message": "账单不存在"}
                    )
                    continue

                # 更新字段
                if "bank" in item:
                    bill.bank = item["bank"]

                if "trade_date" in item and item["trade_date"]:
                    try:
                        bill.trade_date = datetime.strptime(
                            item["trade_date"], "%Y-%m-%d"
                        ).date()
                    except ValueError:
                        pass

                if "record_date" in item and item["record_date"]:
                    try:
                        bill.record_date = datetime.strptime(
                            item["record_date"], "%Y-%m-%d"
                        ).date()
                    except ValueError:
                        pass

                if "description" in item:
                    bill.description = item["description"]

                if "remark" in item:
                    bill.remark = item["remark"]

                if "amount_cny" in item:
                    bill.amount_cny = item["amount_cny"]

                if "card_last4" in item:
                    bill.card_last4 = item["card_last4"]

                if "amount_foreign" in item:
                    bill.amount_foreign = item["amount_foreign"]

                if "currency" in item:
                    bill.currency = item["currency"]

                if "status" in item:
                    bill.status = item["status"]

                bill.updated_at = now
                updated_count += 1
                results.append({"bill_id": bill_id, "success": True})

            except Exception as e:
                failed_count += 1
                results.append(
                    {"bill_id": bill_id, "success": False, "message": str(e)}
                )

    logger.info(
        writeMessage(
            f"批量更新账单 - workspace_id: {workspace_id}, "
            f"updated: {updated_count}, failed: {failed_count}"
        )
    )

    return {
        "updated_count": updated_count,
        "failed_count": failed_count,
        "results": results,
    }


def batch_create_bills(workspace_id: str, bills_data: list, openid: str) -> dict:
    """
    批量创建账单

    Args:
        workspace_id: 空间ID
        bills_data: [{账单字段}, ...]
        openid: 操作用户openid

    Returns:
        {created_count, failed_count, results}
    """
    # 校验权限(需要editor及以上)
    require_workspace_permission(workspace_id, openid, required_role="editor")

    created_count = 0
    failed_count = 0
    results = []

    with db_transaction() as db:
        for bill_item in bills_data:
            try:
                # 处理日期字段
                if bill_item.get("trade_date"):
                    try:
                        bill_item["trade_date"] = datetime.strptime(
                            bill_item["trade_date"], "%Y-%m-%d"
                        ).date()
                    except ValueError:
                        bill_item["trade_date"] = None

                if bill_item.get("record_date"):
                    try:
                        bill_item["record_date"] = datetime.strptime(
                            bill_item["record_date"], "%Y-%m-%d"
                        ).date()
                    except ValueError:
                        bill_item["record_date"] = None

                # 创建账单
                bill = Bill(
                    file_upload_id=bill_item.get("file_upload_id"),
                    workspace_id=workspace_id,
                    bank=bill_item.get("bank"),
                    trade_date=bill_item.get("trade_date"),
                    record_date=bill_item.get("record_date"),
                    description=bill_item.get("description"),
                    amount_cny=bill_item.get("amount_cny"),
                    card_last4=bill_item.get("card_last4"),
                    amount_foreign=bill_item.get("amount_foreign"),
                    currency=bill_item.get("currency"),
                    raw_line=bill_item.get("raw_line", ""),
                    status=bill_item.get("status", "active"),
                )
                db.add(bill)
                created_count += 1
                results.append({"bill_id": bill_item.get("id", ""), "success": True})

            except Exception as e:
                failed_count += 1
                results.append(
                    {
                        "bill_id": bill_item.get("id", ""),
                        "success": False,
                        "message": str(e),
                    }
                )

    logger.info(
        writeMessage(
            f"批量创建账单 - workspace_id: {workspace_id}, "
            f"created: {created_count}, failed: {failed_count}"
        )
    )

    return {
        "created_count": created_count,
        "failed_count": failed_count,
        "results": results,
    }


def delete_bill(workspace_id: str, bill_id: str, openid: str) -> None:
    """删除账单(软删除)"""
    # 校验权限(需要editor及以上)
    require_workspace_permission(workspace_id, openid, required_role="editor")

    with db_transaction() as db:
        bill = (
            db.query(Bill)
            .filter(
                Bill.id == bill_id,
                Bill.workspace_id == workspace_id,
                Bill.is_deleted == False,
            )
            .first()
        )

        if not bill:
            raise ValueError("账单不存在")

        # 软删除账单
        now = datetime.now()
        bill.is_deleted = True
        bill.deleted_at = now
        bill.updated_at = now

        # 更新关联文件的账单数量
        file_record = (
            db.query(FileUpload)
            .filter(
                FileUpload.id == bill.file_upload_id, FileUpload.is_deleted == False
            )
            .first()
        )

        if file_record:
            valid_bills_count = (
                db.query(Bill)
                .filter(Bill.file_upload_id == file_record.id, Bill.is_deleted == False)
                .count()
            )
            file_record.bills_count = valid_bills_count

        logger.info(writeMessage(f"账单删除成功 - bill_id: {bill_id}"))
