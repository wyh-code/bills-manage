"""DeepSeek Token记录装饰器"""

from functools import wraps
from datetime import datetime
from app.utils.logger import get_logger
from app.utils.billing_checker import check_balance_sufficient
from app.services import billing_service

logger = get_logger(__name__)


def track_deepseek_usage(api_type: str):
    """
    装饰器: 自动记录DeepSeek调用的Token消耗

    Args:
        api_type: API类型 'refine'/'convert'
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.now()

            # 提取上下文参数
            workspace_id = kwargs.get("workspace_id")
            file_upload_id = kwargs.get("file_upload_id")
            user_openid = kwargs.get("user_openid")

            # 调用前校验余额
            if user_openid:
                is_sufficient, balance = check_balance_sufficient(user_openid)
                if not is_sufficient:
                    error_msg = f"[DEEPSEEK]账户余额不足，当前余额: {balance:.2f}元，请在【个人中心】充值后继续使用，或自行手动添加账单"
                    logger.warning(
                        f"余额不足阻止API调用 - user: {user_openid}, balance: {balance}"
                    )
                    raise ValueError(error_msg)

            try:
                # 执行原函数
                result, response = func(*args, **kwargs)

                # 记录Token
                if workspace_id and user_openid and hasattr(response, "usage"):
                    try:
                        record_data = {
                            "user_openid": user_openid,
                            "workspace_id": workspace_id,
                            "file_upload_id": file_upload_id,
                            "api_type": api_type,
                            "response": response,
                            "request_start_time": start_time,
                        }
                        logger.info(f"Token记录: {str(record_data)}")
                        billing_service.record_token_usage(
                            openid=record_data["user_openid"],
                            workspace_id=record_data["workspace_id"],
                            file_upload_id=record_data.get("file_upload_id"),
                            api_type=record_data["api_type"],
                            response=record_data["response"],
                            request_start_time=record_data.get("request_start_time"),
                        )
                    except Exception as e:
                        logger.error(f"Token记录异常: {str(e)}")

                return result

            except Exception as e:
                logger.error(
                    f"DeepSeek API调用失败 - api_type: {api_type}, error: {str(e)}"
                )
                raise

        return wrapper

    return decorator
