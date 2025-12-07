# -*- coding: utf-8 -*-
"""
认证相关路由
"""
from flask import Blueprint, request, jsonify, session
import bcrypt
import secrets
from datetime import datetime, timedelta
from app.database import db
from app.config import Config

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['username', 'password', 'real_name', 'security_question', 'security_answer']
    if not all(field in data for field in required_fields):
        return jsonify({'success': False, 'message': '缺少必填字段'}), 400
    
    username = data['username']
    password = data['password']
    real_name = data['real_name']
    security_question = data['security_question']
    security_answer = data['security_answer']
    
    # 检查用户名是否已存在
    existing_user = db.execute_query(
        "SELECT user_id FROM User WHERE username = %s",
        (username,),
        fetch_one=True
    )
    
    if existing_user:
        return jsonify({'success': False, 'message': '用户名已存在'}), 400
    
    # 加密密码
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # 插入用户记录
    try:
        user_id = db.execute_insert(
            """INSERT INTO User (username, password, real_name, security_question, security_answer, is_admin)
               VALUES (%s, %s, %s, %s, %s, FALSE)""",
            (username, hashed_password, real_name, security_question, security_answer)
        )
        
        return jsonify({
            'success': True,
            'message': '注册成功',
            'user_id': user_id
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'message': f'注册失败: {str(e)}'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400
    
    # 查询用户
    user = db.execute_query(
        "SELECT user_id, username, password, real_name, is_admin FROM User WHERE username = %s",
        (username,),
        fetch_one=True
    )
    
    if not user:
        return jsonify({'success': False, 'message': '用户名或密码错误'}), 401
    
    # 验证密码
    try:
        if not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return jsonify({'success': False, 'message': '用户名或密码错误'}), 401
    except Exception:
        # 如果是管理员且密码是明文（用于测试）
        if user['username'] == Config.ADMIN_USERNAME and password == Config.ADMIN_PASSWORD:
            pass
        else:
            return jsonify({'success': False, 'message': '用户名或密码错误'}), 401
    
    # 创建会话
    session_id = secrets.token_hex(32)
    token = secrets.token_hex(64)
    expire_time = datetime.now() + timedelta(seconds=Config.SESSION_TIMEOUT)
    
    try:
        db.execute_insert(
            """INSERT INTO Session (session_id, user_id, login_time, expire_time, token, device_info)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (session_id, user['user_id'], datetime.now(), expire_time, token, request.user_agent.string)
        )
        
        # 设置Flask session
        session['user_id'] = user['user_id']
        session['username'] = user['username']
        session['is_admin'] = bool(user['is_admin'])
        session['token'] = token
        
        return jsonify({
            'success': True,
            'message': '登录成功',
            'user': {
                'user_id': user['user_id'],
                'username': user['username'],
                'real_name': user['real_name'],
                'is_admin': bool(user['is_admin'])
            },
            'token': token
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'登录失败: {str(e)}'}), 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """用户登出"""
    token = session.get('token')
    
    if token:
        # 删除会话记录
        db.execute_update("DELETE FROM Session WHERE token = %s", (token,))
    
    # 清除Flask session
    session.clear()
    
    return jsonify({'success': True, 'message': '登出成功'}), 200


@auth_bp.route('/reset_password', methods=['POST'])
def reset_password():
    """重置密码"""
    data = request.get_json()
    
    username = data.get('username')
    security_answer = data.get('security_answer')
    new_password = data.get('new_password')
    
    if not all([username, security_answer, new_password]):
        return jsonify({'success': False, 'message': '缺少必填字段'}), 400
    
    # 查询用户
    user = db.execute_query(
        "SELECT user_id, security_answer FROM User WHERE username = %s",
        (username,),
        fetch_one=True
    )
    
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404
    
    # 验证安全问题答案
    if user['security_answer'] != security_answer:
        return jsonify({'success': False, 'message': '安全问题答案错误'}), 401
    
    # 加密新密码
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # 更新密码
    try:
        db.execute_update(
            "UPDATE User SET password = %s WHERE user_id = %s",
            (hashed_password, user['user_id'])
        )
        
        return jsonify({'success': True, 'message': '密码重置成功'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'密码重置失败: {str(e)}'}), 500


@auth_bp.route('/get_security_question', methods=['GET'])
def get_security_question():
    """获取用户的安全问题"""
    username = request.args.get('username')
    
    if not username:
        return jsonify({'success': False, 'message': '用户名不能为空'}), 400
    
    user = db.execute_query(
        "SELECT security_question FROM User WHERE username = %s",
        (username,),
        fetch_one=True
    )
    
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404
    
    return jsonify({
        'success': True,
        'security_question': user['security_question']
    }), 200


@auth_bp.route('/check_session', methods=['GET'])
def check_session():
    """检查会话是否有效"""
    if 'user_id' in session:
        return jsonify({
            'success': True,
            'logged_in': True,
            'user': {
                'user_id': session['user_id'],
                'username': session['username'],
                'is_admin': session.get('is_admin', False)
            }
        }), 200
    else:
        return jsonify({
            'success': True,
            'logged_in': False
        }), 200

