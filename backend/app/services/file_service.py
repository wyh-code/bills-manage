"""文件上传服务"""
import os
import threading
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import FileUpload, Bill, WorkspaceMember
from app.database import SessionLocal
from app.utils.deepseek_util import refine_bill_content, convert_bills_to_json
from app.utils.file_utils import (
    save_uploaded_file, 
    get_absolute_path, 
    parse_file, 
    get_file_extension,
    calculate_file_hash,
    writeLog
)

def clean_bill_data(bill: dict) -> dict:
    """
    清洗账单数据，处理各种异常情况
    Args: bill: 原始账单数据字典
    Returns: 清洗后的账单数据字典
    """
    cleaned = {}
    
    # 字符串字段 - 直接复制或设置默认值
    string_fields = ['bank', 'description', 'card_last4', 'currency', 'raw_line']
    for field in string_fields:
        cleaned[field] = bill.get(field, '')
    
    # 日期字段 - 转换为 date 对象
    for date_field in ['trade_date', 'record_date']:
        value = bill.get(date_field)
        if isinstance(value, str):
            try:
                cleaned[date_field] = datetime.strptime(value, '%Y-%m-%d').date()
            except:
                cleaned[date_field] = None
        elif value:
            cleaned[date_field] = value
        else:
            cleaned[date_field] = None
    
    # 金额字段 - 处理空字符串、'-'、None 等情况
    for amount_field in ['amount_cny', 'amount_foreign']:
        value = bill.get(amount_field)
        
        # 处理各种空值情况
        if value in ('', '-', None, 'null', 'NULL'):
            cleaned[amount_field] = None
        else:
            try:
                # 尝试转换为 float
                cleaned[amount_field] = float(value)
            except (ValueError, TypeError):
                # 转换失败，设置为 None
                cleaned[amount_field] = None
    
    # 固定字段
    cleaned['status'] = 'pending'
    cleaned['is_deleted'] = False
    cleaned['deleted_at'] = None
    
    return cleaned

def check_workspace_permission(db: Session, workspace_id: str, openid: str, required_role: str = None) -> tuple:
    """
    检查用户是否为空间成员及权限等级
    :param db: 数据库会话（外部传入）
    :param required_role: 'owner', 'editor', 'viewer' 或 None
    :return: (has_permission: bool, user_role: str)
    """

    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.member_openid == openid,
        WorkspaceMember.is_deleted == False
    ).first()
    
    if not member:
        return False, None
    
    # 如果不需要特定角色，只要是成员即可
    if required_role is None:
        return True, member.role
    
    # 角色等级: owner > editor > viewer
    role_levels = {'owner': 3, 'editor': 2, 'viewer': 1}
    user_level = role_levels.get(member.role, 0)
    required_level = role_levels.get(required_role, 0)
    
    return user_level >= required_level, member.role

def check_file_duplicate(db: Session, workspace_id: str, file_hash: str) -> tuple:
    """
    检查文件是否重复
    :return: (is_duplicate: bool, file_record: FileUpload | None, bills: list)
    """
    file_record = db.query(FileUpload).filter(
        FileUpload.workspace_id == workspace_id,
        FileUpload.file_hash == file_hash,
        FileUpload.is_deleted == False
    ).first()
    
    if not file_record:
        return False, None, []
    
    if file_record and file_record.status == 'failed':
        return False, None, []
    
    # 获取关联的账单
    bills = db.query(Bill).filter(
        Bill.file_upload_id == file_record.id,
        Bill.is_deleted == False
    ).all()
    
    bills_list = [bill.to_dict() for bill in bills]
    
    return True, file_record, bills_list

def process_file_async(file_id: str, workspace_id: str, raw_content: str, original_filename: str):
    """
    异步处理文件精炼（在后台线程中执行）
    延迟创建db，避免在AI调用期间占用连接
    """
    # 先完成AI调用（不占用db连接）
    bills_data = []
    
    writeLog(f"开始精炼 - file_id: {file_id}")
    
    if not raw_content.startswith('['): # 不是错误信息
        try:
            refined_content = refine_bill_content(raw_content, original_filename)
            
            if refined_content:
                bills_data_json_list = convert_bills_to_json(refined_content)
                
                # 3. 清洗每条账单数据
                bills_data = [clean_bill_data(bill) for bill in bills_data_json_list]
                
                writeLog(f"精炼完成 - file_id: {file_id}, bills: {len(bills_data)}")
        except Exception as e:
            writeLog(f"精炼失败 - file_id: {file_id}, error: {str(e)}")
 
    # AI调用完成后，再创建db连接做数据库操作
    db = SessionLocal()
    try:
        file_record = db.query(FileUpload).filter(FileUpload.id == file_id).first()
        if not file_record:
            writeLog(f"文件记录不存在 - file_id: {file_id}")
            return
        
        # 创建账单
        for bill_item in bills_data:
            bill = Bill(
                file_upload_id=file_record.id,
                workspace_id=workspace_id,
                bank=bill_item.get('bank'),
                trade_date=bill_item.get('trade_date'),
                record_date=bill_item.get('record_date'),
                description=bill_item.get('description'),
                amount_cny=bill_item.get('amount_cny'),
                card_last4=bill_item.get('card_last4'),
                amount_foreign=bill_item.get('amount_foreign'),
                currency=bill_item.get('currency'),
                raw_line=bill_item.get('raw_line', ''),
                status='pending'
            )
            db.add(bill)
        
        # 更新文件状态
        file_record.bills_count = len(bills_data)
        file_record.status = 'completed'
        
        db.commit()
        writeLog(f"异步处理完成 - file_id: {file_id}, bills: {len(bills_data)}")
        
    except Exception as e:
        db.rollback()
        writeLog(f"数据库操作失败 - file_id: {file_id}, error: {str(e)}")
        
        # 更新失败状态
        try:
            file_record = db.query(FileUpload).filter(FileUpload.id == file_id).first()
            if file_record:
                file_record.status = 'failed'
                db.commit()
        except Exception as update_error:
            writeLog(f"更新失败状态异常 - file_id: {file_id}, error: {str(update_error)}")
    finally:
        db.close()  # 确保关闭

def upload_and_parse_file(db: Session, workspace_id: str, openid: str, file) -> dict:
    """上传文件并解析（使用外部传入的db）"""
    try:
        # 校验权限并获取文件记录
        has_permission, _ = check_workspace_permission(db, workspace_id, openid, required_role='editor')
        if not has_permission:
            raise ValueError('无权限操作该空间')
    
        original_filename = file.filename
        file_ext = get_file_extension(original_filename)
        
        # 1. 计算文件hash
        file_hash = calculate_file_hash(file)

        # 2. 检查重复
        is_duplicate, file_record, bills = check_file_duplicate(db, workspace_id, file_hash)
        
        if is_duplicate:
            writeLog(f"文件重复 - file_hash: {file_hash}, existing_file_id: {file_record.id}")
            return {
                'status': 'duplicate',
                'data': {
                    'file_id': file_record.id,
                    'original_filename': file_record.original_filename,
                    'file_status': 'completed',
                    'bills': bills,
                    'bills_count': len(bills)
                }
            }
        
        # 3. 保存文件
        saved_path, _, file_size = save_uploaded_file(file, workspace_id, original_filename, file_hash)
        
        # 4. 解析文件内容
        absolute_path = get_absolute_path(saved_path)
        raw_content = parse_file(absolute_path, file_ext)

        # 5. 创建文件记录（status='processing'）
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
            status='processing'
        )
        
        db.add(file_record)
        db.commit()
        db.refresh(file_record)
        
        writeLog(f"文件上传成功 - file_id: {file_record.id}, 开始异步精炼")
        
        # 6. 启动后台线程
        thread = threading.Thread(
            target=process_file_async,
            args=(file_record.id, workspace_id, raw_content, original_filename)
        )
        thread.daemon = True
        thread.start()
        
        return {
            'status': 'success',
            'data': {
                'file_id': file_record.id,
                'original_filename': file_record.original_filename,
                'file_size': file_record.file_size,
                'file_status': 'processing',
                'raw_content': file_record.raw_content,
                'upload_time': file_record.upload_time
            }
        }
    except Exception as e:
        raise

def get_file_progress(db: Session, workspace_id: str, file_id: str, openid: str) -> dict:
    """获取文件处理进度（使用外部传入的db）"""
    # 校验权限并获取文件记录
    has_permission, _ = check_workspace_permission(db, workspace_id, openid)
    if not has_permission:
        raise ValueError('无权限访问该空间')
    
    file_record = db.query(FileUpload).filter(
        FileUpload.id == file_id,
        FileUpload.workspace_id == workspace_id,
        FileUpload.is_deleted == False
    ).first()
    
    if not file_record:
        raise ValueError('文件记录不存在')
    
    result = {
        'file_id': file_record.id,
        'original_filename': file_record.original_filename,
        'file_status': file_record.status,
        'bills_count': file_record.bills_count
    }
    try: 
        # 如果处理完成，返回账单列表
        if file_record.status == 'completed':
            bills = db.query(Bill).filter(
                Bill.file_upload_id == file_id,
                Bill.is_deleted == False
            ).all()
            result['bills'] = [bill.to_dict() for bill in bills]
    except Exception as e:
        writeLog(str(e))
    
    return result

def get_file_for_view(db: Session, workspace_id: str, file_id: str, openid: str) -> tuple:
    """
    获取文件用于预览或下载
    :return: (file_path: str, filename: str, mime_type: str)
    :raises ValueError: 权限不足或文件不存在
    """
    # 权限校验
    has_permission, _ = check_workspace_permission(db, workspace_id, openid)
    if not has_permission:
        raise ValueError('无权限访问该空间')
    
    # 查询文件记录
    file_record = db.query(FileUpload).filter(
        FileUpload.id == file_id,
        FileUpload.workspace_id == workspace_id,
        FileUpload.is_deleted == False
    ).first()
    
    if not file_record:
        raise ValueError('文件记录不存在')
    
    # 获取文件绝对路径
    absolute_path = get_absolute_path(file_record.saved_path)
    
    # 检查文件是否存在
    if not os.path.exists(absolute_path):
        writeLog(f"文件物理路径不存在 - file_id: {file_id}, path: {absolute_path}")
        raise ValueError('文件物理文件缺失')
    
    # 获取MIME类型
    file_ext = get_file_extension(file_record.original_filename)
    mime_type = _get_mime_type(file_ext)
    
    return absolute_path, file_record.original_filename, mime_type


def _get_mime_type(file_ext: str) -> str:
    """根据文件扩展名返回MIME类型"""
    mime_map = {
        'pdf': 'application/pdf',
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'ecxml': 'application/xml'
    }
    return mime_map.get(file_ext.lower(), 'application/octet-stream')