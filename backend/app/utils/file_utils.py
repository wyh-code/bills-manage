"""文件处理工具函数"""
import os
from datetime import datetime
from app.utils.trace_util import get_trace_id

# LangChain 导入
from langchain_community.document_loaders import PyPDFLoader, UnstructuredImageLoader
import xml.etree.ElementTree as ET

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'png', 'pdf', 'ecxml'}

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
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def parse_pdf(filepath):
    """解析 PDF 文件"""
    try:
        loader = PyPDFLoader(filepath)
        pages = loader.load()
        content = "\n\n".join([page.page_content for page in pages])
        return content
    except Exception as e:
        writeLog(f"PDF 解析失败：{str(e)}")
        return f"[PDF 解析错误: {str(e)}]"

def parse_image(filepath):
    """解析图片文件（OCR）"""
    try:
        loader = UnstructuredImageLoader(filepath)
        documents = loader.load()
        content = "\n\n".join([doc.page_content for doc in documents])
        return content if content.strip() else "[图片未识别到文字内容]"
    except Exception as e:
        writeLog(f"图片 OCR 失败：{str(e)}")
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
        writeLog(f"ECXML 解析失败：{str(e)}")
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
