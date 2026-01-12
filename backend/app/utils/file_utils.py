"""文件处理工具函数"""
import os
import hashlib
from datetime import datetime
from nanoid import generate
from app.utils.trace_util import get_trace_id
from app.config import Config
from app.utils.logger import get_logger

logger = get_logger(__name__)

# LangChain 导入
from langchain_community.document_loaders import PyPDFLoader, UnstructuredImageLoader
import xml.etree.ElementTree as ET

def writeMessage(message):
    trace_id = get_trace_id()
    return f"[TraceID: {trace_id}] {message}\n"

def writeLog(message):
    """日志记录函数"""
    rootDir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    today = datetime.now().date()
    logdir = os.path.join(rootDir, 'log')
    os.makedirs(logdir, exist_ok=True)
    
    logpath = os.path.join(logdir, f"{today.isoformat()}.log")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    trace_id = get_trace_id()
    log_message = f"[{timestamp}] [TraceID: {trace_id}] {message}\n"
    
    with open(logpath, 'a', encoding="utf-8") as f:
        print(log_message.strip())
        f.write(log_message)

def allowed_file(filename):
    """检查文件扩展名"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def get_file_extension(filename):
    """提取文件扩展名（小写）"""
    if '.' not in filename:
        return ''
    return filename.rsplit('.', 1)[1].lower()

def calculate_file_hash(file_stream):
    """
    计算文件SHA256哈希
    :param file_stream: 文件流对象
    :return: 64位哈希字符串
    """
    sha256_hash = hashlib.sha256()
    
    # 重置文件指针到开头
    file_stream.seek(0)
    
    # 分块读取文件计算hash
    for byte_block in iter(lambda: file_stream.read(4096), b""):
        sha256_hash.update(byte_block)
    
    # 重置文件指针到开头，供后续使用
    file_stream.seek(0)
    
    return sha256_hash.hexdigest()

def ensure_source_dir(workspace_id):
    """
    创建上传目录结构: storages/{workspace_id}/{YYYYMMDD}/
    :param workspace_id: 空间ID
    :return: 目录路径
    """
   
    today = datetime.now().strftime('%Y%m%d')
    dir_path = Config.STORAGE_DIR / str(workspace_id) / today
    os.makedirs(dir_path, exist_ok=True)
    return dir_path, today

"""文件工具函数 - 优化后的 save_uploaded_file"""

def save_uploaded_file(file, workspace_id, original_filename, file_hash=None):
    """
    保存上传的文件
    :param file: 文件流对象
    :param workspace_id: 空间ID
    :param original_filename: 原始文件名
    :param file_hash: 文件hash（可选，如果已计算则传入，避免重复计算）
    :return: (相对路径, 文件hash, 文件大小)
    """
    # 创建目录
    dir_path, today = ensure_source_dir(workspace_id)
    
    # 如果没有传入hash，则计算
    if file_hash is None:
        file_hash = calculate_file_hash(file)
    
    # 生成唯一文件名
    unique_filename = f"{generate()}_{original_filename}"
    file_path = os.path.join(dir_path, unique_filename)
    
    # 保存文件
    file.save(file_path)
    
    # 获取文件大小
    file_size = os.path.getsize(file_path)
    
    # 返回相对路径（相对于source目录）
    relative_path = os.path.join(str(workspace_id), today, unique_filename)
    
    logger.info(writeMessage(f"文件保存成功 - path: {relative_path}, hash: {file_hash}, size: {file_size}"))
    
    return relative_path, file_hash, file_size

def get_absolute_path(saved_path):
    """
    将相对路径转换为绝对路径
    :param saved_path: 相对路径（相对于source目录）
    :return: 绝对路径
    """
    return Config.STORAGE_DIR / saved_path

def parse_pdf(filepath):
    """解析 PDF 文件"""
    try:
        loader = PyPDFLoader(filepath)
        pages = loader.load()
        content = "\n\n".join([page.page_content for page in pages])
        return content
    except Exception as e:
        logger.error(writeMessage(f"PDF 解析失败：{str(e)}"))
        return f"[PDF 解析错误: {str(e)}]"

def parse_image(filepath):
    """解析图片文件（OCR）"""
    try:
        loader = UnstructuredImageLoader(filepath)
        documents = loader.load()
        content = "\n\n".join([doc.page_content for doc in documents])
        return content if content.strip() else "[图片未识别到文字内容]"
    except Exception as e:
        logger.error(writeMessage(f"图片 OCR 失败：{str(e)}"))
        return f"[图片解析错误: {str(e)}]"

def parse_ecxml(filepath):
    """解析 ECXML 文件"""
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        
        content_parts = []
        
        def extract_text(element, level=0):
            indent = "  " * level
            if element.text and element.text.strip():
                content_parts.append(f"{indent}{element.tag}: {element.text.strip()}")
            
            for child in element:
                extract_text(child, level + 1)
            
            if element.tail and element.tail.strip():
                content_parts.append(f"{indent}[text]: {element.tail.strip()}")
        
        extract_text(root)
        return "\n".join(content_parts) if content_parts else "[XML 文件无文本内容]"
    except Exception as e:
        logger.error(writeMessage(f"ECXML 解析失败：{str(e)}"))
        return f"[ECXML 解析错误: {str(e)}]"

def parse_file(filepath, file_ext):
    """根据文件类型解析文件内容"""
    if file_ext == 'pdf':
        return parse_pdf(filepath)
    elif file_ext == 'png':
        return parse_image(filepath)
    elif file_ext == 'ecxml':
        return parse_ecxml(filepath)
    else:
        return "[不支持的文件格式]"