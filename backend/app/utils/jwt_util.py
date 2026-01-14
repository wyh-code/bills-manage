"""JWT工具类"""

import jwt
from datetime import datetime, timedelta, timezone
from app.config import Config

# 配置参数
JWT_SECRET_KEY = Config.JWT_SECRET_KEY
JWT_ALGORITHM = Config.JWT_ALGORITHM
JWT_EXPIRE_HOURS = int(Config.JWT_ACCESS_TOKEN_EXPIRE_HOURS)

def generate_token(user_data: dict) -> str:
    """
    生成JWT Token
    :param user_data: 用户数据，必须包含 id 和 openid
    :return: JWT字符串
    """
    if not JWT_SECRET_KEY:
        raise ValueError('JWT_SECRET_KEY未配置')
    
    payload = {
        'openid': user_data['openid'],
        'exp': datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS),
        'iat': datetime.now(timezone.utc)
    }
    
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> dict:
    """
    验证JWT Token
    :param token: JWT字符串
    :return: payload数据
    :raises: ValueError
    """
    if not JWT_SECRET_KEY:
        raise ValueError('JWT_SECRET_KEY未配置')
    
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError('Token已过期')
    except jwt.InvalidTokenError:
        raise ValueError('无效的Token')
