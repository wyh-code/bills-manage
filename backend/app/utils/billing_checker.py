"""余额检查工具 - 独立模块，无循环依赖"""

from app.models import UserAccount
from app.database import db_session
from app.utils.logger import get_logger

logger = get_logger(__name__)


def check_balance_sufficient(user_openid: str) -> tuple[bool, float]:
    """
    检查用户余额是否充足

    Args:
        user_openid: 用户openid

    Returns:
        (is_sufficient, balance)
    """
    try:
        with db_session() as db:
            account = (
                db.query(UserAccount)
                .filter(
                    UserAccount.user_openid == user_openid,
                    UserAccount.is_deleted == False,
                )
                .first()
            )

            if not account:
                # 新用户，余额为0
                return False, 0.0

            balance = float(account.balance)
            logger.info(f"当前余额 - user: {user_openid}, balance: {balance}")
            return balance > 0.2, balance

    except Exception as e:
        logger.error(f"余额检查异常 - user: {user_openid}, error: {str(e)}")
        # 检查失败时放行，避免阻塞正常流程
        return True, 0.0
