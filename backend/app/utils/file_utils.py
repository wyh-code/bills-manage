"""文件处理工具函数"""

import os
import hashlib
from datetime import datetime
from nanoid import generate
from app.config import Config
from app.utils import writeMessage, get_logger

logger = get_logger(__name__)


def allowed_file(filename):
    """检查文件扩展名"""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS
    )


def get_file_extension(filename):
    """提取文件扩展名（小写）"""
    if "." not in filename:
        return ""
    return filename.rsplit(".", 1)[1].lower()


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

    today = datetime.now().strftime("%Y%m%d")
    dir_path = Config.STORAGE_DIR / str(workspace_id) / today
    os.makedirs(dir_path, exist_ok=True)
    return dir_path, today


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

    logger.info(
        writeMessage(
            f"文件保存成功 - path: {relative_path}, hash: {file_hash}, size: {file_size}"
        )
    )

    return relative_path, file_hash, file_size


def get_absolute_path(saved_path):
    """
    将相对路径转换为绝对路径
    :param saved_path: 相对路径（相对于source目录）
    :return: 绝对路径
    """
    return Config.STORAGE_DIR / saved_path
