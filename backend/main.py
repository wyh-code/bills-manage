"""主应用文件"""
import os
from flask import Flask, jsonify, g, request
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime
from app.utils.file_utils import writeLog
from app.utils.trace_util import generate_trace_id

# 导入路由
from app.routes import auth_bp

# 加载环境变量
load_dotenv()

# 创建Flask应用
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# 配置CORS
CORS(app, 
     origins=['*'],
     allow_headers=['Content-Type', 'Authorization', 'datasource', 'X-Trace-Id'],
     expose_headers=['X-Trace-Id'],
     supports_credentials=True)

# 全局请求前钩子
@app.before_request
def before_request():
    """在每个请求前执行：设置trace_id"""
    trace_id = request.headers.get('X-Trace-Id', generate_trace_id())
    g.trace_id = trace_id

# 全局请求后钩子
@app.after_request
def after_request(response):
    """在每个请求后执行：返回trace_id"""
    trace_id = getattr(g, 'trace_id', 'NO_TRACE_ID')
    response.headers['X-Trace-Id'] = trace_id
    return response

# 注册路由
app.register_blueprint(auth_bp)

# 健康检查接口
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

# 应用启动
if __name__ == '__main__':
    writeLog("Flask 应用启动 - 已集成认证系统、上传功能和汇总功能")
    app.run(host='0.0.0.0', port=7788, debug=True)
