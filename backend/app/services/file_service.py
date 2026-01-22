"""文件上传服务"""

import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from app.models import FileUpload, Bill, User, Workspace, WorkspaceMember
from app.database import SessionLocal, db_session, db_transaction
from app.utils import (
    get_logger,
    require_workspace_permission,
    save_uploaded_file,
    get_absolute_path,
    get_file_extension,
    calculate_file_hash,
    parse_file,
)
from app.utils.deepseek_util import refine_bill_content, convert_bills_to_json
logger = get_logger(__name__)
executor = ThreadPoolExecutor(max_workers=6)


def clean_bill_data(bill: dict) -> dict:
    """清洗账单数据,处理各种异常情况"""
    cleaned = {}

    string_fields = ["bank", "description", "card_last4", "currency", "raw_line"]
    for field in string_fields:
        cleaned[field] = bill.get(field, "")

    for date_field in ["trade_date", "record_date"]:
        value = bill.get(date_field)
        if isinstance(value, str):
            try:
                cleaned[date_field] = datetime.strptime(value, "%Y-%m-%d").date()
            except:
                cleaned[date_field] = None
        elif value:
            cleaned[date_field] = value
        else:
            cleaned[date_field] = None

    for amount_field in ["amount_cny", "amount_foreign"]:
        value = bill.get(amount_field)
        if value in ("", "-", None, "null", "NULL"):
            cleaned[amount_field] = None
        else:
            try:
                cleaned[amount_field] = float(value)
            except (ValueError, TypeError):
                cleaned[amount_field] = None

    cleaned["status"] = "pending"
    cleaned["is_deleted"] = False
    cleaned["deleted_at"] = None

    return cleaned


def check_file_duplicate(workspace_id: str, file_hash: str) -> tuple:
    """检查文件是否重复"""
    with db_session() as db:
        file_record = (
            db.query(FileUpload)
            .filter(
                FileUpload.workspace_id == workspace_id,
                FileUpload.file_hash == file_hash,
                FileUpload.is_deleted == False,
            )
            .first()
        )

        if not file_record:
            return False, None, []

        if file_record.status == "failed":
            return False, None, []

        bills = (
            db.query(Bill)
            .filter(Bill.file_upload_id == file_record.id, Bill.is_deleted == False)
            .all()
        )

        bills_list = [bill.to_dict() for bill in bills]

        return True, file_record, bills_list


def process_file_async(
    file_id: str,
    workspace_id: str,
    raw_content: str,
    original_filename: str,
    user_openid: str,
):
    """异步处理文件精炼"""
    logger.info(f"开始精炼 - file_id: {file_id}")

    try:
        refined_content = refine_bill_content(
            content=raw_content,
            original_filename=original_filename,
            user_openid=user_openid,
            workspace_id=workspace_id,
            file_upload_id=file_id,
        )
        logger.info(
            f"初步提取refined_content完成 - file_id: {file_id}, refined_content: {refined_content}"
        )
        # 检查精炼结果是否为错误信息（成功时以 "-" 开头，失败时以 "[" 开头）
        if refined_content.startswith("["):
            raise ValueError(refined_content)

        if not refined_content or refined_content == "-None":
            with db_transaction() as db:
                file_record = (
                    db.query(FileUpload).filter(FileUpload.id == file_id).first()
                )
                if not file_record:
                    raise ValueError(f"文件记录不存在 - file_id: {file_id}")

                file_record.refined_content = refined_content
                file_record.bills_count = 0
                file_record.status = "completed"
                file_record.updated_at = datetime.now()

            logger.info(f"异步处理完成 - file_id: {file_id}, 精炼结果为空")
        else:
            bills_data_json_list = convert_bills_to_json(
                refined_content=refined_content,
                user_openid=user_openid,
                workspace_id=workspace_id,
                file_upload_id=file_id,
            )
            bills_data = [clean_bill_data(bill) for bill in bills_data_json_list]

            logger.info(f"精炼完成 - file_id: {file_id}, bills: {len(bills_data)}")

            with db_transaction() as db:
                file_record = (
                    db.query(FileUpload).filter(FileUpload.id == file_id).first()
                )
                if not file_record:
                    raise ValueError(f"文件记录不存在 - file_id: {file_id}")

                now = datetime.now()

                for bill_item in bills_data:
                    bill = Bill(
                        file_upload_id=file_record.id,
                        workspace_id=workspace_id,
                        bank=bill_item.get("bank"),
                        trade_date=bill_item.get("trade_date"),
                        record_date=bill_item.get("record_date"),
                        description=bill_item.get("description"),
                        amount_cny=bill_item.get("amount_cny"),
                        card_last4=bill_item.get("card_last4"),
                        amount_foreign=bill_item.get("amount_foreign"),
                        currency=bill_item.get("currency"),
                        raw_line=bill_item.get("raw_line", ""),
                        status="pending",
                    )
                    db.add(bill)

                file_record.refined_content = refined_content
                file_record.bills_count = len(bills_data)
                file_record.status = "completed"
                file_record.updated_at = now

            logger.info(f"异步处理完成 - file_id: {file_id}, bills: {len(bills_data)}")

    except Exception as e:
        msg = str(e)
        logger.error(f"精炼失败 - file_id: {file_id}, error: {msg}")
        
        remark = msg if msg.startswith('[DEEPSEEK]') else None

        try:
            with db_transaction() as db:
                file_record = (
                    db.query(FileUpload).filter(FileUpload.id == file_id).first()
                )

                if file_record:
                    # 查找并删除同 hash 的旧失败记录
                    db.query(FileUpload).filter(
                        FileUpload.workspace_id == file_record.workspace_id,
                        FileUpload.file_hash == file_record.file_hash,
                        FileUpload.is_deleted == False,
                        FileUpload.status == "failed",
                    ).update(
                        {"is_deleted": True, "deleted_at": datetime.now() },
                        synchronize_session=False,
                    )

                    file_record.refined_content = str(e)
                    file_record.status = "failed"
                    file_record.remark = remark
                    file_record.updated_at = datetime.now()
        except Exception as update_error:
            logger.error(
                f"更新失败状态异常 - file_id: {file_id}, error: {str(update_error)}"
            )


def upload_and_parse_file(workspace_id: str, openid: str, file) -> dict:
    """上传文件并解析"""
    require_workspace_permission(workspace_id, openid, required_role="editor")

    original_filename = file.filename
    file_ext = get_file_extension(original_filename)

    # 1. 计算文件hash
    file_hash = calculate_file_hash(file)

    # 2. 检查重复
    is_duplicate, file_record, bills = check_file_duplicate(workspace_id, file_hash)

    if is_duplicate:
        logger.info(
            f"文件重复 - file_hash: {file_hash}, existing_file_id: {file_record.id}"
        )

        return {
            "status": "duplicate",
            "data": {
                "file_id": file_record.id,
                "original_filename": file_record.original_filename,
                "file_status": "completed",
                "bills": bills,
                "bills_count": len(bills),
            },
        }

    # 3. 解析文件内容(图片使用DeepSeek,其他使用LangChain)
    raw_content = None

    # 先保存文件用于解析
    saved_path, _, file_size = save_uploaded_file(
        file, workspace_id, original_filename, file_hash
    )
    absolute_path = get_absolute_path(saved_path)

    try:
        raw_content = parse_file(absolute_path, file_ext)
        if not raw_content or raw_content.startswith("["):
            # 删除无效文件
            os.remove(absolute_path)
            raise ValueError("文件解析失败或内容为空")
    except Exception as e:
        # 清理无效文件
        if os.path.exists(absolute_path):
            os.remove(absolute_path)
        raise ValueError(f"文件解析失败: {str(e)}")

    # 4. 创建文件记录(status='processing')
    with db_transaction() as db:
        upload_time = int(datetime.now().timestamp() * 1000)
        file_record = FileUpload(
            workspace_id=workspace_id,
            uploaded_by_openid=openid,
            file_hash=file_hash,
            original_filename=original_filename,
            saved_path=saved_path,
            file_size=file_size,
            raw_content=raw_content,
            refined_content=None,
            bills_count=0,
            upload_time=upload_time,
            status="processing",
        )

        db.add(file_record)
        db.flush()
        db.refresh(file_record)

        logger.info(f"文件上传成功 - file_id: {file_record.id}, 开始异步精炼")

        file_id = file_record.id

    # 5. 启动后台线程
    executor.submit(
        process_file_async,
        file_id,
        workspace_id,
        raw_content,
        original_filename,
        openid,
    )

    return {
        "status": "success",
        "data": {
            "file_id": file_id,
            "original_filename": original_filename,
            "file_size": file_size,
            "file_status": "processing",
            "raw_content": raw_content,
            "upload_time": upload_time,
        },
    }


def get_file_progress(workspace_id: str, file_id: str, openid: str) -> dict:
    """获取文件处理进度"""
    require_workspace_permission(workspace_id, openid)

    with db_session() as db:
        file_record = (
            db.query(FileUpload)
            .filter(
                FileUpload.id == file_id,
                FileUpload.workspace_id == workspace_id,
                FileUpload.is_deleted == False,
            )
            .first()
        )

        if not file_record:
            raise ValueError("文件记录不存在")

        result = {
            "file_id": file_record.id,
            "original_filename": file_record.original_filename,
            "file_status": file_record.status,
            "bills_count": file_record.bills_count,
            "remark": file_record.remark,
        }

        try:
            if file_record.status == "completed":
                bills = (
                    db.query(Bill)
                    .filter(Bill.file_upload_id == file_id, Bill.is_deleted == False)
                    .all()
                )
                result["bills"] = [bill.to_dict() for bill in bills]
        except Exception as e:
            logger.error(str(e))

        return result


def get_file_for_view(workspace_id: str, file_id: str, openid: str) -> tuple:
    """获取文件用于预览或下载"""
    require_workspace_permission(workspace_id, openid)

    with db_session() as db:
        file_record = (
            db.query(FileUpload)
            .filter(
                FileUpload.id == file_id,
                FileUpload.workspace_id == workspace_id,
                FileUpload.is_deleted == False,
            )
            .first()
        )

        if not file_record:
            raise ValueError("文件记录不存在")

        absolute_path = get_absolute_path(file_record.saved_path)

        if not os.path.exists(absolute_path):
            logger.warning(
                f"文件物理路径不存在 - file_id: {file_id}, path: {absolute_path}"
            )
            raise ValueError("文件物理文件缺失")

        file_ext = get_file_extension(file_record.original_filename)
        mime_type = _get_mime_type(file_ext)

        return absolute_path, file_record.original_filename, mime_type


def get_file_records(openid: str, workspace_ids=None, page=1, page_size=10) -> list:
    """获取文件上传记录"""

    with db_session() as db:
        # 获取用户有权限的所有空间
        members = (
            db.query(WorkspaceMember)
            .filter(
                WorkspaceMember.member_openid == openid,
                WorkspaceMember.is_deleted == False,
            )
            .all()
        )

        accessible_workspace_ids = [m.workspace_id for m in members]

        # 筛选空间
        if workspace_ids:
            accessible_workspace_ids = [
                wid for wid in workspace_ids if wid in accessible_workspace_ids
            ]

        # 构建基础查询(用于统计和分页)
        base_query = db.query(FileUpload).filter(
            FileUpload.workspace_id.in_(accessible_workspace_ids),
            FileUpload.is_deleted == False,
            FileUpload.status != "failed",
        )

        # 统计总数
        total = base_query.count()

        # 分页查询
        offset = (page - 1) * page_size
        files = (
            base_query.order_by(FileUpload.created_at.desc())
            .limit(page_size)
            .offset(offset)
            .all()
        )

        if not files:
            return [], total

        # 批量查询相关数据
        file_ids = [f.id for f in files]
        uploader_openids = list(set(f.uploaded_by_openid for f in files))
        workspace_ids_set = list(set(f.workspace_id for f in files))

        # 批量查询上传人信息
        uploaders = db.query(User).filter(User.openid.in_(uploader_openids)).all()
        uploader_map = {u.openid: u for u in uploaders}

        # 批量查询空间信息
        workspaces = (
            db.query(Workspace)
            .filter(Workspace.id.in_(workspace_ids_set), Workspace.is_deleted == False)
            .all()
        )
        workspace_map = {w.id: w for w in workspaces}

        # 批量查询所有文件的账单
        bills = (
            db.query(Bill)
            .filter(Bill.file_upload_id.in_(file_ids), Bill.is_deleted == False)
            .all()
        )

        # 按文件ID组织账单
        bills_by_file = {}
        for bill in bills:
            if bill.file_upload_id not in bills_by_file:
                bills_by_file[bill.file_upload_id] = []
            bills_by_file[bill.file_upload_id].append(bill)

        # 组装结果
        records = []
        for file in files:
            uploader = uploader_map.get(file.uploaded_by_openid)
            workspace = workspace_map.get(file.workspace_id)
            file_bills = bills_by_file.get(file.id, [])

            # 计算账单总金额
            total_amount = {}
            bills_list = []
            for bill in file_bills:
                if bill.amount_cny:
                    total_amount["CNY"] = total_amount.get("CNY", 0) + float(
                        bill.amount_cny
                    )
                elif bill.amount_foreign and bill.currency:
                    total_amount[bill.currency] = total_amount.get(
                        bill.currency, 0
                    ) + float(bill.amount_foreign)
                bills_list.append(bill.to_dict())

            records.append(
                {
                    "file_id": file.id,
                    "file_name": file.original_filename,
                    "workspace": {
                        "name": workspace.name if workspace else None,
                        "id": workspace.id if workspace else None,
                    },
                    "uploader": {
                        "openid": file.uploaded_by_openid,
                        "nickname": uploader.nickname if uploader else None,
                    },
                    "upload_time": (
                        file.created_at.isoformat() if file.created_at else None
                    ),
                    "bills_count": len(bills_list),
                    "total_amount": total_amount,
                    "bills": bills_list,
                }
            )

        return records, total


def _get_mime_type(file_ext: str) -> str:
    """根据文件扩展名返回MIME类型"""
    mime_map = {
        "pdf": "application/pdf",
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "ecxml": "application/xml",
    }
    return mime_map.get(file_ext.lower(), "application/octet-stream")
