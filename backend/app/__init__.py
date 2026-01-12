from flask import Flask, g, request, jsonify
from flask_cors import CORS
from datetime import datetime
from app.utils.file_utils import writeMessage
from app.utils.trace_util import generate_trace_id
from app.utils.logger import get_logger
from app.config import Config
from app.database import init_db
import traceback

# 导入路由
from app.routes import auth_bp, workspace_bp, file_bp, bill_bp, invitation_bp

def create_app(config_class=Config):
    """应用工厂函数"""
    logger = get_logger(__name__)
    
    # 初始化数据库
    try:
        logger.info("初始化数据库...")
        init_db()
        logger.info("初始化数据库成功")
    except Exception as e:
        logger.warning(f"数据库初始化失败: {str(e)}")
    
    # 创建Flask应用
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.secret_key = Config.SECRET_KEY
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    
    # 配置CORS
    CORS(app,
         origins=['*'],
         allow_headers=['Content-Type', 'Authorization', 'datasource', 'X-Trace-Id'],
         expose_headers=['X-Trace-Id'],
         supports_credentials=True,
         max_age=86400)
    
    # ================== 注册钩子 ==================
    
    @app.before_request
    def before_request():
        """请求前钩子：设置trace_id"""
        trace_id = request.headers.get('X-Trace-Id', generate_trace_id())
        g.trace_id = trace_id
    
    @app.after_request
    def after_request(response):
        """请求后钩子：返回trace_id"""
        trace_id = getattr(g, 'trace_id', 'NO_TRACE_ID')
        response.headers['X-Trace-Id'] = trace_id
        return response
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        """全局异常处理"""
        logger.error(writeMessage(f"未捕获异常 - path: {request.path}, error: {str(e)}"))
        logger.error(writeMessage(f"错误堆栈: {traceback.format_exc()}"))
        
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
    
    # ================== 注册路由 ==================
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(workspace_bp)
    app.register_blueprint(file_bp)
    app.register_blueprint(bill_bp)
    app.register_blueprint(invitation_bp)
    
    # ================== 健康检查 ==================
    
    @app.route('/api/health', methods=['GET'])
    def health():
        """健康检查"""
        return jsonify({
            'success': True,
            'data': {
                'status': 'ok',
                'version': '2.0.0',
                'timestamp': datetime.now().isoformat(),
                'trace_id': getattr(g, 'trace_id', 'NO_TRACE_ID')
            }
        }), 200
    
    return app