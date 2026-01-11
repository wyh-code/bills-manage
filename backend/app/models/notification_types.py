"""通知类型定义"""

class NotificationType:
    """通知类型枚举"""
    
    # 空间相关
    WORKSPACE_INVITED = 'workspace.invited'                    # 被邀请加入空间
    WORKSPACE_MEMBER_ADDED = 'workspace.member_added'          # 被添加为成员
    WORKSPACE_MEMBER_REMOVED = 'workspace.member_removed'      # 被移除出空间
    WORKSPACE_ROLE_CHANGED = 'workspace.role_changed'          # 角色变更
    WORKSPACE_DELETED = 'workspace.deleted'                    # 空间被删除
    WORKSPACE_INVITATION_REVOKED = 'workspace.invitation_revoked'  # 邀请被撤销
    
    # 文件相关
    FILE_UPLOADED = 'file.uploaded'                            # 新文件上传
    FILE_COMPLETED = 'file.completed'                          # 文件处理完成
    FILE_FAILED = 'file.failed'                                # 文件处理失败
    FILE_DELETED = 'file.deleted'                              # 文件被删除
    
    # 账单相关
    BILL_CONFIRMED = 'bill.confirmed'                          # 账单确认
    BILL_BATCH_CONFIRMED = 'bill.batch_confirmed'              # 批量确认
    BILL_UPDATED = 'bill.updated'                              # 账单更新
    BILL_DELETED = 'bill.deleted'                              # 账单删除
    
    # 系统相关
    SYSTEM_MAINTENANCE = 'system.maintenance'                  # 系统维护
    SYSTEM_UPDATE = 'system.update'                            # 功能更新

class NotificationPriority:
    """通知优先级枚举"""
    HIGH = 'high'      # 高优先级（红色角标）
    NORMAL = 'normal'  # 普通（默认）
    LOW = 'low'        # 低优先级