from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.inspection import inspect
from sqlalchemy import Column, Boolean, DateTime
from datetime import datetime
from decimal import Decimal

Base = declarative_base()

class BaseModel(Base):
    """所有模型的基类"""
    __abstract__ = True
    
    # 通用字段：软删除 + 时间戳
    is_deleted = Column(Boolean, default=False, nullable=False, index=True, comment='是否删除')
    deleted_at = Column(DateTime, nullable=True, comment='删除时间')
    created_at = Column(DateTime, default=datetime.now, nullable=False, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def to_dict(self, exclude=[], **kwargs):
        """转换为字典，自动处理日期和数字类型"""
        result = {}
        mapper = inspect(self.__class__)
        
        for column in mapper.columns:
            col_name = column.name
            if col_name in exclude:
                continue
            
            value = getattr(self, col_name, None)
            
            # 处理日期类型
            if hasattr(value, "isoformat"):
                result[col_name] = value.isoformat() if value else None
            # 处理数字类型（Decimal、float、int，但排除bool）
            elif isinstance(value, (Decimal, float, int)) and not isinstance(value, bool):
                result[col_name] = float(value) if value is not None else None
            else:
                result[col_name] = value
        
        return result

    def __repr__(self):
        if hasattr(self, "__repr_fields__"):
            fields = getattr(self, "__repr_fields__")
            attrs = ", ".join(f"{field}={getattr(self,field,None)}" for field in fields)
        else:
            attrs = f"id={getattr(self,'id',None)}"
        return f"<{self.__class__.__name__}({attrs})>"