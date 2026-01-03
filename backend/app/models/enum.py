class CommonStatus:
    """通用状态常量"""
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    
    ALL = [ACTIVE, INACTIVE]
    
    @classmethod
    def is_valid(cls, value: str) -> bool:
        """验证状态值是否有效"""
        return value in cls.ALL