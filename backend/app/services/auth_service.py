"""认证服务"""
import requests
from app.utils.jwt_util import generate_token
from app.utils.trace_util import get_trace_id
from app.utils.file_utils import writeMessage
from app.utils.logger import get_logger
from app.config import Config
from app.database import db_transaction
from app.models import User

logger = get_logger(__name__)

# 微信认证服务基础URL
AUTH_BASE_URL = 'http://auth.mocknet.cn/auth/wx'

def config(datasource: str) -> dict:
    """获取微信扫码配置"""
    try:
        trace_id = get_trace_id()
        logger.info(writeMessage(f"请求微信扫码配置 - datasource: {datasource}"))

        response = requests.get(
            f"{AUTH_BASE_URL}/config",
            headers={"datasource": datasource, "X-Trace-Id": trace_id},
            timeout=30,
        )

        response.raise_for_status()
        data = response.json()

        if data.get("code") != 200:
            message = f'获取扫码配置失败: {data.get("message", "未知错误")}'
            logger.warning(writeMessage(message))
            raise Exception(message)

        result = data.get("data", {})
        result["state"] = trace_id

        return result

    except requests.RequestException as e:
        message = f"请求微信认证服务失败: {str(e)}"
        logger.error(writeMessage(message))
        raise Exception(message)

def status(datasource: str, state: str) -> dict:
    """查询扫码状态"""
    
    try:
        response = requests.get(
            f'{AUTH_BASE_URL}/status/{state}',
            headers={ 'datasource': datasource },
            timeout=30
        )
        
        response.raise_for_status()
        data = response.json()
        logger.info(writeMessage(f"查询扫码状态 - response: {response.text}"))

        if data.get('code') != 200:
            message = f'查询扫码状态失败: {data.get("message", "未知错误")}'
            logger.warning(writeMessage(message))
            raise Exception(message)
        
        return data.get('data', {})
        
    except requests.RequestException as e:
        message = f'请求微信认证服务失败: {str(e)}'
        logger.error(writeMessage(message))
        raise Exception(message)

def _is_seed_user(openid: str) -> bool:
    """检查是否为种子用户"""
    return openid in Config.SEED_USERS


def code2info(datasource: str, code: str) -> dict:
    """code换取用户信息和token"""
    if not code:
        raise ValueError('code参数不能为空')
    
    try:
        response = requests.get(
            f'{AUTH_BASE_URL}/code2info',
            params={'code': code},
            headers={'datasource': datasource},
            timeout=30
        )
        
        response.raise_for_status()
        data = response.json()
        
        if data.get('code') != 200:
            message = f'换取用户信息失败: {data.get("message", "未知错误")}'
            logger.warning(writeMessage(message))
            raise Exception(message)
        
        user_info = data.get('data', {})
        
        if not user_info.get('openid'):
            message = '未获取到用户openid'
            logger.warning(writeMessage(message))
            raise Exception(message)
        
        openid = user_info["openid"]
        is_seed = _is_seed_user(openid)
        print("="*50)
        print('Config.SEED_USERS: ', Config.SEED_USERS, is_seed, openid)
        print("="*50)

        # 查询或创建用户
        with db_transaction() as db:
            user = db.query(User).filter_by(openid=openid).first()

            if not user:
                # 创建新用户
                user = User(
                    openid=openid,
                    unionid=user_info.get("unionid"),
                    nickname=user_info.get("nickname"),
                    headimgurl=user_info.get("headimgurl"),
                    status="active" if is_seed else "inactive",
                )
                db.add(user)

                logger.info(
                    writeMessage(
                        f"创建新用户 - openid: {openid}, "
                        f"type: {'root' if is_seed else 'user'}, "
                        f"status: {user.status}"
                    )
                )
            else:
                # 更新用户信息
                user.nickname = user_info.get("nickname")
                user.headimgurl = user_info.get("headimgurl")

                # 种子用户强制激活
                if is_seed and user.status == "inactive":
                    user.status = "active"
                    logger.info(writeMessage(f"种子用户自动激活 - openid: {openid}"))

        
            # 生成JWT token
            token = generate_token({"id": user.id, "openid": user.openid})

            return {"user": user.to_dict(), "token": token}
        
    except requests.RequestException as e:
        # 其他网络错误(超时,连接失败等)
        error_msg = f"请求微信认证服务失败: {str(e)}"
        logger.error(writeMessage(error_msg))
        raise Exception(error_msg)
    
    except ValueError as e:
        # 参数错误
        error_msg = f"参数错误: {str(e)}"
        logger.error(writeMessage(error_msg))
        raise Exception(error_msg)
    
    except Exception as e:
        # 其他所有异常
        error_msg = f"code2info处理失败: {str(e)}"
        logger.error(writeMessage(error_msg))
        raise Exception(error_msg)
