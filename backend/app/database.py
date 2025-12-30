import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 获取项目根目录
rootDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 数据库文件路径
db_path = os.path.join(rootDir, 'database', 'bills.db')
os.makedirs(os.path.dirname(db_path), exist_ok=True)

# 数据库连接URL
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"

# 创建数据库引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite特有配置
    echo=False  # 设为True可打印SQL语句
)

# 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 模型基类
Base = declarative_base()

# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
