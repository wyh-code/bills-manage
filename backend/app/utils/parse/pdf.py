from pypdf import PdfReader
from app.utils.logger import get_logger

logger = get_logger(__name__)


def parse_pdf(filepath):
    """解析 PDF 文件"""
    try:
        reader = PdfReader(filepath)

        if not reader.pages:
            logger.warning(f"PDF 文件为空: {filepath}")
            return "[PDF 文件无内容]"

        # 提取所有页面文本
        content = "\n\n".join([page.extract_text() for page in reader.pages])

        logger.info(
            f"PDF 解析成功 - 文件: {filepath}, 页数: {len(reader.pages)}, "
            f"字符数: {len(content)}"
        )

        return content if content.strip() else "[PDF 未识别到文字内容]"

    except Exception as e:
        error_msg = f"PDF 解析失败: {str(e)}"
        logger.error(f"{error_msg} - 文件: {filepath}")
        raise Exception(error_msg)
