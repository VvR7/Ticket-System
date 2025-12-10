# -*- coding: utf-8 -*-
"""
数据库连接管理（使用连接池）
"""
import pymysql
from pymysql.cursors import DictCursor
from contextlib import contextmanager
from functools import wraps
import time
import random
from dbutils.pooled_db import PooledDB
from app.config import Config


class Database:
    """数据库连接管理类（使用连接池）"""
    
    # 连接池实例（类变量，所有实例共享）
    _pool = None
    
    @classmethod
    def init_pool(cls):
        """
        初始化数据库连接池
        连接池可以：
        1. 复用连接，减少建立/关闭连接的开销
        2. 控制并发连接数，防止数据库过载
        3. 自动管理连接的生命周期
        """
        if cls._pool is None:
            print("正在初始化数据库连接池...")
            cls._pool = PooledDB(
                creator=pymysql,           # 使用pymysql作为连接模块
                maxconnections=Config.POOL_MAX_CONNECTIONS,  # 连接池允许的最大连接数
                mincached=Config.POOL_MIN_CACHED,            # 初始化时创建的空闲连接数
                maxcached=Config.POOL_MAX_CACHED,            # 连接池中最多保持的空闲连接数
                maxshared=Config.POOL_MAX_SHARED,            # 最大共享连接数
                blocking=Config.POOL_BLOCKING,               # 连接池满时是否阻塞等待
                maxusage=Config.POOL_MAX_USAGE,              # 单个连接最大使用次数
                setsession=[],                               # 连接建立时执行的SQL命令列表
                ping=1,                                      # 检测连接是否可用（0=不检测, 1=默认检测, 2=连接使用时检测, 4=事务开始时检测, 7=总是检测）
                reset=Config.POOL_RESET,                     # 连接归还池时是否重置状态
                # 数据库连接参数
                host=Config.MYSQL_HOST,
                port=Config.MYSQL_PORT,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                database=Config.MYSQL_DATABASE,
                charset=Config.MYSQL_CHARSET,
                cursorclass=DictCursor,
                autocommit=False
            )
            print(f"数据库连接池初始化成功！配置：max={Config.POOL_MAX_CONNECTIONS}, min_cached={Config.POOL_MIN_CACHED}, max_cached={Config.POOL_MAX_CACHED}")
        return cls._pool
    
    @classmethod
    def get_pool_status(cls):
        """
        获取连接池状态信息（用于监控）
        """
        if cls._pool is None:
            return "连接池未初始化"
        
        # DBUtils的PooledDB没有直接提供状态查询接口
        # 这里返回配置信息
        return {
            'max_connections': Config.POOL_MAX_CONNECTIONS,
            'min_cached': Config.POOL_MIN_CACHED,
            'max_cached': Config.POOL_MAX_CACHED,
            'max_shared': Config.POOL_MAX_SHARED,
            'status': '运行中'
        }
    
    @staticmethod
    def retry_on_deadlock(max_retries=3, base_wait_time=0.01):
        """
        死锁重试装饰器
        :param max_retries: 最大重试次数，默认3次
        :param base_wait_time: 基础等待时间（秒），默认0.01秒
        :return: 装饰器函数
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                for attempt in range(max_retries):
                    try:
                        return func(*args, **kwargs)
                    except pymysql.err.OperationalError as e:
                        # 检查是否是死锁错误（错误码1213）
                        if e.args[0] == 1213:
                            if attempt < max_retries - 1:
                                # 使用指数退避策略，避免多个事务同时重试
                                wait_time = random.uniform(
                                    base_wait_time * (2 ** attempt),
                                    base_wait_time * (2 ** (attempt + 1))
                                )
                                print(f"检测到死锁，{wait_time:.4f}秒后进行第{attempt + 2}次重试...")
                                time.sleep(wait_time)
                                continue
                            else:
                                # 达到最大重试次数
                                raise Exception('系统繁忙，请稍后重试（死锁）')
                        else:
                            # 其他操作错误，直接抛出
                            raise
                    except Exception as e:
                        # 非死锁异常，直接抛出
                        raise
                return None
            return wrapper
        return decorator
    
    @classmethod
    def get_connection(cls):
        """
        从连接池获取数据库连接
        :return: 数据库连接对象
        """
        if cls._pool is None:
            cls.init_pool()
        return cls._pool.connection()
    
    @staticmethod
    @contextmanager
    def get_cursor(commit=True):
        """
        获取数据库游标的上下文管理器
        :param commit: 是否自动提交事务
        """
        conn = Database.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            if commit:
                conn.commit()
        except pymysql.err.OperationalError as e:
            conn.rollback()
            # 保留原始的死锁异常，让装饰器处理
            if e.args[0] == 1213:
                raise
            raise e
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def execute_query(sql, params=None, fetch_one=False):
        """
        执行查询SQL
        :param sql: SQL语句
        :param params: 参数
        :param fetch_one: 是否只获取一条记录
        :return: 查询结果
        """
        with Database.get_cursor(commit=False) as cursor:
            cursor.execute(sql, params or ())
            if fetch_one:
                return cursor.fetchone()
            return cursor.fetchall()
    
    @staticmethod
    def execute_update(sql, params=None):
        """
        执行更新SQL（INSERT, UPDATE, DELETE）
        :param sql: SQL语句
        :param params: 参数
        :return: 影响的行数
        """
        with Database.get_cursor(commit=True) as cursor:
            affected_rows = cursor.execute(sql, params or ())
            return affected_rows
    
    @staticmethod
    def execute_insert(sql, params=None):
        """
        执行插入SQL并返回插入的ID
        :param sql: SQL语句
        :param params: 参数
        :return: 插入的ID
        """
        with Database.get_cursor(commit=True) as cursor:
            cursor.execute(sql, params or ())
            return cursor.lastrowid
    
    @staticmethod
    def execute_batch(sql_list):
        """
        批量执行SQL（事务）
        :param sql_list: SQL列表，每个元素为(sql, params)元组
        :return: 是否成功
        """
        with Database.get_cursor(commit=True) as cursor:
            for sql, params in sql_list:
                cursor.execute(sql, params or ())
            return True


# 数据库实例
db = Database()

