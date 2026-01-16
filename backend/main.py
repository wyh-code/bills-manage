"""主应用文件"""

from app import create_app
from app.utils import writeMessage, get_logger
from app.config import Config

# 创建应用实例
app = create_app()

logger = get_logger(__name__)

# 应用启动
if __name__ == "__main__":
    logger.info(writeMessage("Flask 应用启动 - 已集成认证系统、文件上传和账单管理功能"))
    app.run(host=Config.APP_HOST, port=Config.APP_PORT, debug=Config.APP_DEBUG)
