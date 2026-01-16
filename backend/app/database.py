import os
from pathlib import Path
from sqlalchemy import create_engine
from contextlib import contextmanager
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app.config import Config
from app.utils import get_logger

logger = get_logger(__name__)

# 数据库文件路径
db_path = Config.DB_DIR / Config.DB_PATH
os.makedirs(os.path.dirname(db_path), exist_ok=True)

# 数据库连接URL
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"

# 创建数据库引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, echo=False
)

# 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def db_session():
    """只读查询使用"""
    session = SessionLocal()
    try:
        yield session
    except Exception as e:
        logger.error(f"数据库会话错误:{e}")
        raise
    finally:
        session.close()


@contextmanager
def db_transaction():
    """写入操作使用(自动提交/回滚)"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"数据库事务错误:{e}")
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"数据库会话错误:{e}")
        raise
    finally:
        session.close()


def init_db():
    try:
        """初始化数据库表"""
        print("=" * 60)
        print("开始初始化数据库...")
        print("=" * 60)

        Base.metadata.create_all(bind=engine)

        print("\n✅ 数据库初始化完成!")
        print(f"📂 数据库文件位置: {engine.url.database}")

    except Exception as e:
        logger.error(f"初始化数据库失败:{e}")
        raise
