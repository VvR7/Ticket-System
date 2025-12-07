# -*- coding: utf-8 -*-
"""
数据库连接管理
"""
import pymysql
from pymysql.cursors import DictCursor
from contextlib import contextmanager
from app.config import Config


class Database:
    """数据库连接管理类"""
    
    @staticmethod
    def get_connection():
        """获取数据库连接"""
        return pymysql.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DATABASE,
            charset=Config.MYSQL_CHARSET,
            cursorclass=DictCursor,
            autocommit=False
        )
    
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

