## 快速开始

### 1. 环境要求

- Python 3.7+
- MySQL 8.0+
- 现代浏览器（Chrome、Firefox、Edge等）

### 2. 安装步骤

#### 2.1 克隆或下载项目

```bash
# 如果使用Git
git clone <repository-url>
cd Project

# 或直接下载ZIP并解压
```

#### 2.2 安装Python依赖

```bash
python -m venv venv
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 2.3 配置MySQL数据库

**方法一：修改配置文件**

编辑 `app/config.py`，修改以下配置：

```python
MYSQL_HOST = 'localhost'
MYSQL_PORT = 3306
MYSQL_USER = 'root'
MYSQL_PASSWORD = '******'  # 改为你的MySQL密码
MYSQL_DATABASE = 'ticket_system'
```



#### 2.4 初始化数据库

```bash
# 登录MySQL
mysql -u root -p

# 执行建表脚本
source sql/create_tables.sql

# 执行初始化数据脚本
source sql/init_data.sql

# 或使用命令行直接执行
mysql -u root -p < sql/create_tables.sql
mysql -u root -p < sql/init_data.sql
```

#### 2.5 运行项目

```bash
python run.py
```

成功启动后会看到：

```
============================================================
22306订票系统启动中...
访问地址: http://localhost:5000
管理员账号: Admin
管理员密码: 23336326
============================================================
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://0.0.0.0:5000
```

#### 2.6 访问系统

在浏览器中打开：`http://localhost:5000`


## 默认账号

### 管理员账号
- 用户名：`Admin`
- 密码：`23336326`


