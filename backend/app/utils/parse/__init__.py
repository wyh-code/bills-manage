from app.utils.logger import get_logger, writeMessage
from .excel import parse_excel
from .pdf import parse_pdf
from .image import parse_image

logger = get_logger(__name__)

def parse_file(filepath, file_ext):
    """
    根据文件类型解析文件内容
    : "pdf", "png", "jpg", "jpeg", "xlsx", "xls"
    """
    try:
        if file_ext == "pdf":
            return parse_pdf(filepath)
        elif file_ext in ["png", "jpg", "jpeg"]:
            return parse_image(filepath)
        elif file_ext in ["xlsx", "xls"]:
            return parse_excel(filepath)
        else:
            error_msg = f"不支持的文件格式: {file_ext}"
            logger.error(writeMessage(error_msg))
            raise Exception(error_msg)

    except Exception as e:
        # 确保异常向上传递
        if str(e).startswith("["):
            # 已经是格式化的错误消息
            raise
        else:
            # 包装为统一格式
            raise Exception(f"[文件解析失败: {str(e)}]")
