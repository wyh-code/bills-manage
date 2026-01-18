import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from app.config import Config
from .trace_util import get_trace_id


class TraceIDFormatter(logging.Formatter):
    """自动添加 TraceID 的格式化器"""

    DEFAULT_FORMAT = (
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - "
        "[TraceID: %(trace_id)s] %(message)s"
    )

    def __init__(self, fmt=None, datefmt=None, style="%"):
        if fmt is None:
            fmt = self.DEFAULT_FORMAT
        super().__init__(fmt, datefmt, style)

    def format(self, record):
        try:
            record.trace_id = get_trace_id()
        except Exception:
            record.trace_id = "UNKNOWN"
        return super().format(record)


class LoggerManager:
    """日志管理器"""

    MAX_BYTES = 10 * 1024 * 1024
    BACKUP_COUNT = 5

    def __init__(self):
        self.log_dir = Path(Config.LOG_DIR)
        self.log_file = Path(Config.LOG_FILE)
        self.level = getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)
        self.enable_file = Config.LOG_ENABLE_FILE
        self.enable_console = Config.LOG_ENABLE_CONSOLE
        self._initialize()

    def _initialize(self):
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.setLevel(self.level)

        # 使用自定义 Formatter
        formatter = TraceIDFormatter()

        if self.enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.level)
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)

        if self.enable_file:
            Path(self.log_dir).mkdir(parents=True, exist_ok=True)
            log_path = self.log_dir / self.log_file
            file_handler = RotatingFileHandler(
                str(log_path),
                maxBytes=self.MAX_BYTES,
                backupCount=self.BACKUP_COUNT,
                encoding="utf-8",
            )
            file_handler.setLevel(self.level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

        logging.captureWarnings(True)

    def get_logger(self, name="app"):
        return logging.getLogger(name)


loggerManager = LoggerManager()


def get_logger(name="app"):
    return loggerManager.get_logger(name)


def writeMessage(message):
    """已废弃"""
    trace_id = get_trace_id()
    return f"[TraceID: {trace_id}] {message}"
