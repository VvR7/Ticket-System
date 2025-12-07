# -*- coding: utf-8 -*-
"""
22306订票系统 - 入口程序
"""
from app import create_app

app = create_app()

if __name__ == '__main__':
    print("="*60)
    print("22306订票系统启动中...")
    print("访问地址: http://localhost:5000")
    print("管理员账号: Admin")
    print("管理员密码: 23336326")
    print("="*60)
    app.run(debug=True, host='0.0.0.0', port=5000)

