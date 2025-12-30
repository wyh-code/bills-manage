"""请求追踪工具"""
import uuid
from flask import request, g, has_request_context
from functools import wraps

def generate_trace_id():
    """生成唯一的追踪ID"""
    return str(uuid.uuid4())

def get_trace_id():
    """
    获取当前请求的追踪ID
    如果不在请求上下文中，返回默认值
    """
    if has_request_context():
        return getattr(g, 'trace_id', 'NO_TRACE_ID')
    return 'STARTUP'  # 应用启动、后台任务等场景
