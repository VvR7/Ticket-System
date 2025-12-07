# -*- coding: utf-8 -*-
"""
Flask应用初始化
"""
from flask import Flask, render_template, session
from flask_cors import CORS
from app.config import Config
from app.routes.auth import auth_bp
from app.routes.ticket import ticket_bp
from app.routes.admin import admin_bp


def create_app():
    """创建Flask应用"""
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(Config)
    
    # 启用CORS
    CORS(app, supports_credentials=True)
    
    # 注册蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(ticket_bp)
    app.register_blueprint(admin_bp)
    
    # 主页路由
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/login')
    def login_page():
        return render_template('login.html')
    
    @app.route('/register')
    def register_page():
        return render_template('register.html')
    
    @app.route('/search')
    def search_page():
        return render_template('search.html')
    
    @app.route('/booking/<int:schedule_id>')
    def booking_page(schedule_id):
        return render_template('booking.html', schedule_id=schedule_id)
    
    @app.route('/my_orders')
    def my_orders_page():
        if 'user_id' not in session:
            return render_template('login.html')
        return render_template('my_orders.html')
    
    @app.route('/admin')
    def admin_page():
        if 'user_id' not in session or not session.get('is_admin'):
            return render_template('login.html')
        return render_template('admin.html')
    
    @app.route('/reset_password')
    def reset_password_page():
        return render_template('reset_password.html')
    
    return app

