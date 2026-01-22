"""计费服务"""

from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from app.models import (
    UserAccount,
    BillingRecord,
    TokenUsageRecord,
    FileUpload,
    Workspace,
)
from app.database import db_transaction
from app.utils import get_logger
from app.config import Config
from app.database import db_session

logger = get_logger(__name__)


def get_token_unit_price(model_name: str) -> float:
    """获取模型单价(元/千token)"""
    price = Config.TOKEN_PRICING.get(model_name, Config.TOKEN_PRICING["default"])
    return Decimal(str(price))


def record_token_usage(
    openid: str,
    workspace_id: str,
    file_upload_id: str,
    api_type: str,
    response,
    request_start_time: datetime = None,
) -> dict:
    """
    记录Token使用 + 自动扣费

    Args:
        openid: 用户openid
        workspace_id: 工作空间ID
        file_upload_id: 文件ID
        api_type: 'refine' | 'convert'
        response: OpenAI API响应对象
        request_start_time: 请求开始时间(用于计算响应时间)

    Returns:
        {'token_record_id', 'cost', 'balance_after'}
    """
    try:
        # 提取Token数据
        usage = response.usage
        prompt_tokens = usage.prompt_tokens
        completion_tokens = usage.completion_tokens
        total_tokens = usage.total_tokens

        # 计算费用
        unit_price = get_token_unit_price(response.model)
        cost = ((Decimal(str(total_tokens)) / Decimal("1000")) * unit_price).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        logger.info("计算费用 cost: ", cost)
        # 计算响应时间
        response_time = None
        if request_start_time:
            response_time = int(
                (datetime.now() - request_start_time).total_seconds() * 1000
            )

        with db_transaction() as db:
            # 记录Token使用
            token_record = TokenUsageRecord(
                user_openid=openid,
                workspace_id=workspace_id,
                file_upload_id=file_upload_id,
                api_type=api_type,
                model=response.model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                unit_price=unit_price,
                cost=cost,
                request_id=response.id,
                response_time=response_time,
                status="success",
            )
            db.add(token_record)
            db.flush()

            # 自动扣费
            balance_after = _deduct_balance(db, openid, cost, token_record.id)

            logger.info(
                f"Token使用记录成功 - user: {openid}, api_type: {api_type}, "
                f"tokens: {total_tokens}, cost: {cost:.4f}, balance: {balance_after}"
            )

            return {
                "token_record_id": token_record.id,
                "cost": float(cost),
                "balance_after": float(balance_after),
            }

    except Exception as e:
        logger.error(f"记录Token使用失败 - error: {str(e)}")
        # 记录失败的Token使用
        with db_transaction() as db:
            token_record = TokenUsageRecord(
                user_openid=openid,
                workspace_id=workspace_id,
                file_upload_id=file_upload_id,
                api_type=api_type,
                model=response.model,
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                unit_price=None,
                cost=0,
                status="failed",
                error_message=str(e),
            )
            db.add(token_record)
        raise


def _deduct_balance(db, openid: str, amount: float, token_usage_id: str) -> float:
    """
    从用户账户扣除费用

    Returns:
        扣费后余额

    Raises:
        ValueError: 余额不足
    """
    # 获取账户(行级锁)
    account = (
        db.query(UserAccount)
        .filter(UserAccount.user_openid == openid, UserAccount.is_deleted == False)
        .with_for_update()
        .first()
    )

    if not account:
        # 首次使用自动创建账户
        account = UserAccount(user_openid=openid, balance=0.00)
        db.add(account)
        db.flush()

    # 余额检查
    if account.balance < amount:
        logger.warning(
            f"余额不足 - user: {openid}, 需要: {amount:.4f}, 余额: {account.balance}"
        )
        # raise ValueError(f"账户余额不足，当前余额: {account.balance}元")

    # 扣除余额
    balance_before = account.balance
    account.balance -= amount
    account.total_consumed += amount
    account.updated_at = datetime.now()
    balance_after = account.balance

    # 记录扣费
    billing_record = BillingRecord(
        user_openid=openid,
        amount=amount,
        balance_before=balance_before,
        balance_after=balance_after,
        token_usage_id=token_usage_id,
        billing_type="token_usage",
        description=f"AI Token消耗扣费",
    )
    db.add(billing_record)

    return balance_after


def get_billing_records_with_file(
    openid: str, month: str = None, page: int = 1, page_size: int = 20
) -> dict:
    """
    获取扣费记录(含文件信息) - JOIN连表查询

    Args:
        openid: 用户openid
        month: 月份筛选 "YYYY-MM" (可选)
        page: 页码
        page_size: 每页数量

    Returns:
        {
            "total": 100,
            "page": 1,
            "page_size": 20,
            "items": [
                {
                    "id": "xxx",
                    "api_type": "refine",
                    "workspace_name": "账务空间",
                    "original_filename": "原始账单文件名",
                    "token_usage": 1500,
                    "balance_before": 100.00,
                    "balance_after": 99.50,
                    "created_at": "2025-01-22 10:30:00"
                }
            ]
        }
    """
    with db_session() as db:
        # 构建连表查询
        query = (
            db.query(
                BillingRecord.id,
                BillingRecord.balance_before,
                BillingRecord.balance_after,
                BillingRecord.created_at,
                TokenUsageRecord.api_type,
                TokenUsageRecord.total_tokens,
                FileUpload.original_filename,
                Workspace.name.label("workspace_name"),
            )
            .outerjoin(
                TokenUsageRecord, BillingRecord.token_usage_id == TokenUsageRecord.id
            )
            .outerjoin(FileUpload, TokenUsageRecord.file_upload_id == FileUpload.id)
            .outerjoin(Workspace, TokenUsageRecord.workspace_id == Workspace.id)
            .filter(
                BillingRecord.user_openid == openid, BillingRecord.is_deleted == False
            )
        )

        # 月份筛选
        if month:
            try:
                start_date = datetime.strptime(f"{month}-01", "%Y-%m-%d")
                end_date = (
                    start_date.replace(year=start_date.year + 1, month=1, day=1)
                    if start_date.month == 12
                    else start_date.replace(month=start_date.month + 1, day=1)
                )
                query = query.filter(
                    BillingRecord.created_at >= start_date,
                    BillingRecord.created_at < end_date,
                )
            except ValueError:
                raise ValueError("月份格式错误，请使用 YYYY-MM 格式")

        # 总数
        total = query.count()

        # 分页查询
        offset = (page - 1) * page_size
        results = (
            query.order_by(BillingRecord.created_at.desc())
            .limit(page_size)
            .offset(offset)
            .all()
        )

        # 组装返回数据
        items = [
            {
                "id": row.id,
                "api_type": row.api_type or "未知",
                "workspace_name": row.workspace_name or "未知",
                "original_filename": row.original_filename or "未知",
                "token_usage": row.total_tokens or 0,
                "balance_before": float(row.balance_before or 0),
                "balance_after": float(row.balance_after or 0),
                "created_at": row.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for row in results
        ]

        logger.info(
            f"查询扣费记录成功 - user: {openid}, month: {month}, total: {total}"
        )

        return {"total": total, "page": page, "page_size": page_size, "items": items}
