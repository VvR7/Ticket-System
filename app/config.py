# -*- coding: utf-8 -*-
"""
配置文件
"""
import os

class Config:
    """应用配置"""
    
    # 密钥（用于session加密）
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-22306-ticket-system'
    
    # 数据库配置
    MYSQL_HOST = 'localhost'
    MYSQL_PORT = 3306
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = '123456'
    MYSQL_DATABASE = 'ticket_system'
    MYSQL_CHARSET = 'utf8mb4'
    
    # Session配置
    SESSION_TIMEOUT = 3600  # 1小时
    
    # 分页配置
    PER_PAGE = 20
    
    # 上传文件配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # 管理员配置
    ADMIN_USERNAME = 'Admin'
    ADMIN_PASSWORD = '23336326'

