# -*- coding: utf-8 -*-
import os
from typing import Union, Dict, Literal, List, Optional
from sqlalchemy import create_engine, Table, Column, CHAR, Text, DateTime, Integer, Date, inspect, JSON, Index, \
    UniqueConstraint, func, VARCHAR
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.mysql import LONGTEXT, BLOB
from daphantom.exceptions.mysqlerr import *

class BaseModel:
    def __init__(self,
                 *,
                 cut: Literal['DB', 'MYSQL'],
                 table_name: str = '',
                 db_file: str = '',
                 db_path: str = '',
                 mysql_config: dict = None,
                 pool_size: int = 200,
                 Base: declarative_base = None
                 ):
        self.cut = cut.upper()
        self.table_name = table_name
        self.pool_size = pool_size
        self.Base = Base
        if self.cut == 'DB':
            # 路径
            file_path = db_path or os.path.dirname(__file__)
            # 文件夹创建
            if not os.path.exists(file_path): os.makedirs(file_path, exist_ok=True)
            # 绝对路径
            self.db_file = os.path.join(file_path, db_file or "cache.db")
            self.engine = create_engine(f'sqlite:///{self.db_file}', pool_size=self.pool_size, echo=False)
        elif self.cut == 'MYSQL':
            # 本段代码用于创建与数据库的连接，使用mysql+pymysql作为数据库引擎
            user = mysql_config.get('USER')
            password = mysql_config.get('PASSWORD')
            host = mysql_config.get('HOST')
            port = mysql_config.get('PORT')
            name = mysql_config.get('NAME')
            if not all(v is not None and v != '' for v in [user, password, host, port, name]):
                raise MysqlErrorParameter("The `user, password, host, port, name` parameters are missing.")
            self.engine = create_engine(
                f'mysql+pymysql://{user}:{password}@{host}:{port}/{name}',  # 创建MySQL数据库连接引擎
                pool_size=self.pool_size,   # 连接池大小设置为20
                echo=False,  # 不输出SQL日志
                pool_recycle=3600,  # 连接回收时间设为3600秒(1小时)
                pool_pre_ping=True  # 启用连接前ping检测，确保连接有效性
            )
        else:
            raise MysqlErrorType('Type error, please select `MYSQL` or `DB`')

        # 定义Session，绑定数据库引擎
        self.Session = sessionmaker(bind=self.engine)
        # 模型定义 占位
        self.DynamicProduct = None
        self.dynamics_model_definition(table_name=table_name)
        self.create_table()

    def dynamics_model_definition(self, table_name) -> Union[int, ValueError]:
        """
        动态模型定义
        `table_name` 表名称
        """
        if table_name in self.Base.registry.mappers:
            self.DynamicProduct = self.Base.registry.mappers[table_name]
            return 1
        self.DynamicProduct = self.model_definition(table_name)
        return 1

    def model_definition(self,table_name):
        return type(table_name, (self.Base,), {
            '__tablename__': table_name,
            '__table_args__': (
                Index(f'idx_{table_name}_timestamp_end', 'timestamp_end'),  # 单列索引
                UniqueConstraint('Key', name=f'uq_{table_name}_key'),  # 唯一约束
                {
                    'mysql_engine': 'InnoDB',
                    'mysql_charset': 'utf8mb4',
                    'mysql_collate': 'utf8mb4_general_ci'
                }),
            'id': Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='自增ID'),
            'timestamp_end': Column(Integer, nullable=False, comment='时间戳'),
            'Key': Column(CHAR(100), nullable=False, comment='键', index=True),
            'Value': Column(Text, nullable=False, comment='值'),
        })
    def create_table(self) -> int:
        """创建表"""
        inspector = inspect(self.engine)
        if self.table_name not in inspector.get_table_names():
            self.Base.metadata.create_all(self.engine)
        return 1


class _ceshi(BaseModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def local_insert_data(self, data_dict: dict) -> Union[int, ValueError]:
        """插入数据 | 更新数据"""
        self.create_table()
        with self.Session() as session:
            try:
                # 查找是否已存在相同Key的记录
                existing = session.query(self.DynamicProduct).filter(self.DynamicProduct.Key == data_dict['Key']).first()
                # 如果存在 则执行更新 所有键值信息
                if existing:
                    # 更新现有记录
                    for key, value in data_dict.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                else:
                    # 插入新记录
                    product = self.DynamicProduct(**data_dict)
                    session.add(product)
                session.commit()
                # 数据插入成功
                return 1
            except Exception as e:
                session.rollback()
                raise MysqlErrorOther(f'[{self.cut}]数据插入失败: {e}')



if __name__ == '__main__':
    Base = declarative_base()

    DBSqlalchemy2 = _ceshi(
        cut='DB',
        db_path='D:/eo',
        db_file='c.db',
        table_name='ceshi',
        pool_size=2,
        Base=Base)

    data_dict = {'Key': '2s1', 'Value': 'asd', "timestamp_end":1231241242141}

    DBSqlalchemy2.local_insert_data(data_dict=data_dict)

