import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 项目根目录的路径
class Config:
    BASE_DIR = Path(__file__).parent.parent
    # 种子用户配置
    SEED_USERS = os.environ.get("SEED_USERS", "").split(",") if os.environ.get("SEED_USERS") else []

    # 加载环境变量中配置的密钥
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "JWT_SECRET_KEY")
    JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_HOURS = os.environ.get("JWT_ACCESS_TOKEN_EXPIRE_HOURS", 24)
    DATASOURCE = os.environ.get("DATASOURCE", "authmate")

    # 应用配置
    # 应用监听的主机地址
    APP_HOST = os.environ.get("APP_HOST", "0.0.0.0")
    # 服务器监听的端口号
    APP_PORT = os.environ.get("APP_PORT", 7788)
    # 是否启动调用模式
    APP_DEBUG = os.environ.get("APP_DEBUG", "true").lower() == "true"

    # 日志配置
    # 日志存放目录
    LOG_DIR = os.environ.get("LOG_DIR", BASE_DIR / "logs")
    # 日志文件
    LOG_FILE = os.environ.get("LOG_FILE", "app.log")
    # 日志级别
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    # 是否启用文件日志
    LOG_ENABLE_FILE = os.environ.get("LOG_ENABLE_FILE", "true").lower() == "true"
    # 是否启用控制台
    LOG_ENABLE_CONSOLE = os.environ.get("LOG_ENABLE_CONSOLE", "true").lower() == "true"

    DB_DIR = os.environ.get("DB_DIR", BASE_DIR / "database")
    DB_PATH = os.environ.get("DB_PATH", "bills.db")

    # 本地文件的存储目录
    STORAGE_DIR = os.environ.get("STORAGE_DIR", BASE_DIR / "storages")
    # 允许的文件扩展名
    ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "xml", "xlsx", "ecxml"}

    DEEPSEEK_CHAT_MODEL = os.environ.get("DEEPSEEK_CHAT_MODEL", "deepseek-chat")
    DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
