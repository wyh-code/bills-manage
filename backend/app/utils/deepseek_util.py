"""DeepSeek API 工具"""

import json
from openai import OpenAI
from dotenv import load_dotenv
from app.config import Config
from app.utils.file_utils import writeMessage
from app.utils.logger import get_logger

logger = get_logger(__name__)

load_dotenv()

# 初始化 DeepSeek 客户端
deepseek_client = OpenAI(
    api_key=Config.DEEPSEEK_API_KEY, base_url=Config.DEEPSEEK_BASE_URL
)

# 输出格式
ROW_FORMAT = "[发卡行,交易日,记账日,交易摘要,人民币金额,卡号末四位,交易地金额,记账币种]"


def refine_bill_content(content, original_filename):
    """使用 DeepSeek 提纯账单信息"""
    try:
        logger.info(writeMessage(f"开始调用 DeepSeek API 提纯：{original_filename}"))

        prompt = f"""请分析以下账单内容，提取符合条件的账单信息。

提取规则：
1. 提取所有非支付宝消费的账单
2. 提取所有非微信消费的账单
4. 如果账单满足上述二个条件，则提取

输出格式要求：
- 按照以下格式输出，每行一条记录：{ROW_FORMAT}
- 字段说明：
* 发卡行：银行名称
* 交易日：交易发生日期（格式：YYYY-MM-DD）
* 记账日：银行记账日期（格式：YYYY-MM-DD）
* 交易摘要：交易描述
* 人民币金额：该笔交易的人民币金额（如果原始数据是外币且没有人民币金额，请使用"-"占位符）
* 卡号末四位：信用卡后4位数字
* 交易地金额：原始交易金额（含币种符号，如 $99.99 或 ¥100.00）
* 记账币种：记账使用的币种（如：CNY、USD、EUR等）

重要提示：
1. 若有人民币金额字段必须填写，外币交易没有人民币信息的使用"-"占位符
2. 交易地金额保留原始币种和金额
3. 若某字段无信息，使用"-"占位
4. 如果没有符合条件的账单，返回"None"

账单内容：
{content}

请严格按照格式输出，不要添加任何解释文字。"""

        response = deepseek_client.chat.completions.create(
            model=Config.DEEPSEEK_CHAT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的财务账单分析助手，擅长从账单中提取关键信息。你必须严格按照指定格式输出，不添加任何额外说明。",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=2000,
        )

        refined_content = response.choices[0].message.content
        usage = response.usage
        logger.info(
            writeMessage(f"DeepSeek API 调用成功 - tokens: {usage.total_tokens}")
        )

        return refined_content

    except Exception as e:
        logger.error(writeMessage(f"DeepSeek API 调用失败：{str(e)}"))
        return f"[DeepSeek 提纯失败: {str(e)}]\n\n原始内容：\n{content}"


def convert_bills_to_json(refined_content):
    """
    将提纯后的账单文本转换为结构化 JSON
    让 DeepSeek 负责格式转换，避免本地解析错误
    """
    try:
        logger.info(
            writeMessage(
                f"开始调用 DeepSeek 转换为 JSON，内容长度：{len(refined_content)}"
            )
        )

        prompt = f"""请将以下账单数据转换为 JSON 格式。

输入数据格式说明：
- 每行一条账单记录
- 格式：{ROW_FORMAT}
- "-" 表示该字段为空

输出要求：
1. 输出纯 JSON 格式，不要有任何 markdown 标记（如 ```json）
2. 返回一个对象，包含 "bills" 数组
3. 每个账单包含以下字段：
    - bank = Column(String(50), nullable=True, comment='发卡行')
    - trade_date = Column(Date, nullable=True, comment='交易日YYYY-MM-DD 格式')
    - record_date = Column(Date, nullable=True, comment='记账日YYYY-MM-DD 格式')
    - description = Column(Text, nullable=True, comment='交易摘要')
    - amount_cny = Column(DECIMAL(15, 2), nullable=True, comment='人民币金额')
    - card_last4 = Column(String(4), nullable=True, comment='卡号末四位')
    - amount_foreign = Column(DECIMAL(15, 2), nullable=True, comment='交易地金额')
    - currency = Column(String(10), nullable=True, comment='记账币种，如 "USD", "CNY"')
    - raw_line = Column(Text, nullable=False, comment='原始精炼字符串单行')
4. 跳过所有非数据行（如标题、说明文字、"None"等）
5. 如果字段值为 "-"，对应字段使用空字符串 ""

账单数据：
{refined_content}

请输出纯 JSON，示例格式：
{{"bills": [{{"bank": "招商银行", "trade_date": "2024-11-15", "record_date": "2024-11-16", "description": "AMAZON购物", "amount_cny": "", "card_last4": "1234", "amount_foreign": 99.99, "currency": "USD", "raw_line": {ROW_FORMAT}}}]}}"""

        response = deepseek_client.chat.completions.create(
            model=Config.DEEPSEEK_CHAT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个数据格式转换专家，擅长将文本数据转换为结构化 JSON。你必须只返回纯 JSON 格式，不添加任何解释或 markdown 标记。",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,  # 降低温度，提高准确性
            max_tokens=4000,
        )

        json_content_str = response.choices[0].message.content.strip()
        usage = response.usage
        logger.info(
            writeMessage(f"DeepSeek JSON 转换成功 - tokens: {usage.total_tokens}")
        )

        # 清理可能的 markdown 标记
        if json_content_str.startswith("```json"):
            json_content_str = json_content_str[7:]
        if json_content_str.startswith("```"):
            json_content_str = json_content_str[3:]
        if json_content_str.endswith("```"):
            json_content_str = json_content_str[:-3]

        json_content_str = json_content_str.strip()
        logger.info(writeMessage(f"清理后的 JSON 字符：{json_content_str}"))
        json_content_data = json.loads(json_content_str)
        return json_content_data.get("bills", [])

    except Exception as e:
        logger.error(writeMessage(f"DeepSeek JSON 转换失败：{str(e)}"))
        # 返回空的 JSON 结构
        return '{"bills": []}'
