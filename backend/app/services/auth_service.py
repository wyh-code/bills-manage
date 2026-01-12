"""认证服务"""
import requests
from app.utils.jwt_util import generate_token
from app.utils.trace_util import get_trace_id
from app.utils.file_utils import writeMessage
from app.utils.logger import get_logger
from app.database import SessionLocal
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
            f'{AUTH_BASE_URL}/config',
            headers={
                'datasource': datasource,
                'X-Trace-Id': trace_id  # 透传trace_id
            },
            timeout=30
        )
        
        response.raise_for_status()
        data = response.json()
        
        if data.get('code') != 200:
            message = f'获取扫码配置失败: {data.get("message", "未知错误")}'
            logger.warning(writeMessage(message))
            raise Exception(message)
        
        # 返回配置（包含前端state）
        result = data.get('data', {})
        result['state'] = trace_id
        
        return result
        
    except requests.RequestException as e:
        message = f'请求微信认证服务失败: {str(e)}'
        logger.error(writeMessage(message))
        raise Exception(message)

def status(datasource: str, state: str) -> dict:
    """查询扫码状态"""
    
    try:
        trace_id = get_trace_id()
        response = requests.get(
            f'{AUTH_BASE_URL}/status/{state}',
            headers={
                'datasource': datasource,
                'X-Trace-Id': trace_id  # 透传trace_id
            },
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

def code2info(datasource: str, code: str) -> dict:
    """code换取用户信息和token"""
    if not code:
        raise ValueError('code参数不能为空')
    
    db = SessionLocal()
    
    try:
        trace_id = get_trace_id()
        
        response = requests.get(
            f'{AUTH_BASE_URL}/code2info',
            params={'code': code},
            headers={
                'datasource': datasource,
                'X-Trace-Id': trace_id  # 透传trace_id
            },
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
        
        # 查询或创建用户
        user = db.query(User).filter_by(openid=user_info['openid']).first()
        
        if not user:
            # 创建新用户
            user = User(
                openid=user_info['openid'],
                unionid=user_info.get('unionid'),
                nickname=user_info.get('nickname'),
                headimgurl=user_info.get('headimgurl')
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            # 更新用户信息（昵称和头像可能变化）
            user.nickname = user_info.get('nickname')
            user.headimgurl = user_info.get('headimgurl')
            db.commit()
        
        # 生成JWT token
        token = generate_token({
            'id': user.id,
            'openid': user.openid
        })
        
        return {
            'user': user.to_dict(),
            'token': token
        }
        
    except requests.RequestException as e:
        message = f'请求微信认证服务失败: {str(e)}'
        logger.error(writeMessage(message))
        raise Exception(message)
    finally:
        db.close()
