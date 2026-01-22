import os
import cv2
import numpy as np
from threading import Lock
from paddleocr import PaddleOCR
from typing import Optional
from app.utils.logger import get_logger

logger = get_logger(__name__)

# 全局单例及线程锁
_ocr_instance: Optional[PaddleOCR] = None
_ocr_lock = Lock()


def get_ocr_instance() -> PaddleOCR:
    """获取 PaddleOCR 单例实例(线程安全)"""
    global _ocr_instance

    if _ocr_instance is None:
        with _ocr_lock:
            # 双重检查锁定模式
            if _ocr_instance is None:
                _ocr_instance = PaddleOCR(lang="ch")
                logger.info("PaddleOCR 初始化成功")

    return _ocr_instance


def parse_image(filepath: str, min_confidence: float = 0.5) -> str:
    """
    使用PaddleOCR解析图片中的文本

    Args:
        filepath: 图片路径
        min_confidence: 最小置信度阈值，低于此值的文本将被过滤
    """
    try:
        logger.info(f"开始调用PaddleOCR解析图片: {filepath}")

        # 1. 验证文件存在
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"图片文件不存在: {filepath}")

        # 2. 验证图片可读（处理中文路径）
        img_array = np.fromfile(filepath, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        if img is None:
            error_msg = f"无法读取图片文件（可能已损坏）: {filepath}"
            logger.error(error_msg)
            return "[图片文件损坏]"

        # 3. 获取 OCR 实例并识别
        ocr = get_ocr_instance()
        result = ocr.predict(img)  # 使用图片数组而不是路径

        # 4. 检查结果
        if not result:
            logger.warning(f"未识别到任何文本: {filepath}")
            return "[图片未识别到文字内容]"

        # 5. 提取文本（适配 PaddleX 返回格式）
        text_items = []

        for page_result in result:
            # PaddleX 返回格式
            if isinstance(page_result, dict):
                rec_texts = page_result.get("rec_texts", [])
                rec_scores = page_result.get("rec_scores", [])
                rec_polys = page_result.get("rec_polys", [])

                for i, text in enumerate(rec_texts):
                    if i >= len(rec_scores):
                        break

                    confidence = rec_scores[i]

                    # 过滤低置信度文本
                    if confidence < min_confidence:
                        logger.debug(
                            f"过滤低置信度文本: {text} (置信度: {confidence:.2f})"
                        )
                        continue

                    # 获取边界框坐标（用于排序）
                    if i < len(rec_polys):
                        bbox = rec_polys[i]
                        y_center = (
                            (bbox[0][1] + bbox[2][1]) / 2 if len(bbox) >= 3 else i * 20
                        )
                        x_left = bbox[0][0] if len(bbox) > 0 else 0
                    else:
                        # 如果没有坐标信息，按顺序排列
                        y_center = i * 20
                        x_left = 0

                    text_items.append(
                        {
                            "text": text,
                            "confidence": confidence,
                            "y": y_center,
                            "x": x_left,
                        }
                    )

        # 6. 检查是否有有效文本
        if not text_items:
            logger.warning(f"所有文本置信度过低（< {min_confidence}）: {filepath}")
            return "[图片文字置信度过低]"

        # 7. 按Y坐标排序（从上到下），同一行按X坐标排序（从左到右）
        text_items.sort(key=lambda item: (round(item["y"] / 20), item["x"]))

        # 8. 提取排序后的文本
        extracted_lines = [item["text"] for item in text_items]
        extracted_text = "\n".join(extracted_lines)

        # 9. 计算平均置信度
        avg_confidence = sum(item["confidence"] for item in text_items) / len(
            text_items
        )

        logger.info(
            f"PaddleOCR解析成功 - 文件: {filepath}, "
            f"识别行数: {len(extracted_lines)}, "
            f"平均置信度: {avg_confidence:.2f}"
        )
        logger.info(f"识别文本预览: {extracted_text}")

        return extracted_text

    except FileNotFoundError as e:
        logger.error(str(e))
        raise
    except Exception as e:
        error_msg = f"图片文件解析错误: {str(e)}"
        logger.error(f"{error_msg} - 文件: {filepath}")
        raise Exception(error_msg)
