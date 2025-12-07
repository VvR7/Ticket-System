# 22306订票系统 - 安装部署指南

## 一、系统要求

### 软件要求
- **操作系统**：Windows 10/11, Linux, macOS
- **Python**：3.7 或更高版本
- **MySQL**：8.0 或更高版本
- **浏览器**：Chrome 90+, Firefox 88+, Edge 90+ 或其他现代浏览器

### 硬件要求（最低配置）
- CPU：双核处理器
- 内存：4GB RAM
- 硬盘：500MB 可用空间

## 二、详细安装步骤

### 步骤1：安装MySQL

#### Windows
1. 下载MySQL安装包：https://dev.mysql.com/downloads/installer/
2. 运行安装程序，选择"Developer Default"
3. 设置root密码（默认配置中为`123456`）
4. 完成安装

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install mysql-server
sudo mysql_secure_installation
```

#### macOS
```bash
brew install mysql
brew services start mysql
mysql_secure_installation
```

### 步骤2：安装Python

#### Windows
1. 下载Python：https://www.python.org/downloads/
2. 运行安装程序
3. **重要**：勾选"Add Python to PATH"
4. 验证安装：
```bash
python --version
pip --version
```

#### Linux
```bash
# Ubuntu/Debian
sudo apt install python3 python3-pip

# CentOS/RHEL
sudo yum install python3 python3-pip
```

#### macOS
```bash
brew install python3
```

### 步骤3：下载项目

#### 方法A：使用Git
```bash
git clone <repository-url>
cd Project
```

#### 方法B：下载ZIP
1. 下载项目ZIP文件
2. 解压到目标目录
3. 进入项目目录

### 步骤4：创建Python虚拟环境（推荐）

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate

# Linux/macOS:
source venv/bin/activate

# 激活后，命令提示符前会出现 (venv) 标记
```

### 步骤5：安装Python依赖包

```bash
# 确保在虚拟环境中
pip install -r requirements.txt

# 如果下载速度慢，可以使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**依赖包列表**：
- Flask==2.3.3 - Web框架
- flask-cors==4.0.0 - 跨域支持
- pymysql==1.1.0 - MySQL数据库驱动
- bcrypt==4.0.1 - 密码加密

### 步骤6：配置数据库连接

#### 方法A：修改配置文件（简单）

编辑 `app/config.py`：

```python
class Config:
    # 数据库配置
    MYSQL_HOST = 'localhost'     # 数据库主机
    MYSQL_PORT = 3306            # 端口
    MYSQL_USER = 'root'          # 用户名
    MYSQL_PASSWORD = '123456'    # ⚠️ 修改为你的MySQL密码
    MYSQL_DATABASE = 'ticket_system'
```

#### 方法B：使用环境变量（推荐）

```bash
# Windows CMD
set MYSQL_PASSWORD=你的密码

# Windows PowerShell
$env:MYSQL_PASSWORD="你的密码"

# Linux/macOS
export MYSQL_PASSWORD=你的密码
```

然后修改 `app/config.py`：

```python
import os

class Config:
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or '123456'
```

### 步骤7：初始化数据库

#### 方法A：使用MySQL命令行

```bash
# 1. 登录MySQL
mysql -u root -p
# 输入密码

# 2. 在MySQL中执行
source D:\college\DB_Project\sql\create_tables.sql
source D:\college\DB_Project\sql\init_data.sql

# 或使用完整路径（Linux/macOS）
source /path/to/Project/sql/create_tables.sql
source /path/to/Project/sql/init_data.sql

# 3. 验证
use ticket_system;
show tables;
# 应该看到12个表
```

#### 方法B：使用命令行导入

```bash
# Windows
mysql -u root -p < sql\create_tables.sql
mysql -u root -p < sql\init_data.sql

# Linux/macOS
mysql -u root -p < sql/create_tables.sql
mysql -u root -p < sql/init_data.sql
```

### 步骤8：启动应用

```bash
# 确保在项目根目录
python run.py
```

**成功启动的标志**：

```
============================================================
22306订票系统启动中...
访问地址: http://localhost:5000
管理员账号: Admin
管理员密码: 23336326
============================================================
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://0.0.0.0:5000
```

### 步骤9：访问系统

1. 打开浏览器
2. 访问：`http://localhost:5000`
3. 看到首页即表示安装成功！

## 三、验证安装

### 测试1：访问首页
- URL: `http://localhost:5000`
- 应该看到系统首页和导航栏

### 测试2：用户注册
1. 点击"注册"
2. 填写注册信息
3. 提交注册
4. 看到"注册成功"提示

### 测试3：用户登录
1. 使用刚注册的账号登录
2. 或使用管理员账号：
   - 用户名：`Admin`
   - 密码：`23336326`

### 测试4：查询车票
1. 在首页选择出发城市、到达城市、日期
2. 点击"查询车票"
3. 应该看到班次列表

### 测试5：管理员后台
1. 使用管理员账号登录
2. 访问：`http://localhost:5000/admin`
3. 应该看到管理后台界面

## 四、常见问题排查

### 问题1：MySQL连接失败

**错误信息**：
```
pymysql.err.OperationalError: (2003, "Can't connect to MySQL server on 'localhost'")
```

**解决方案**：
1. 检查MySQL是否运行：
   ```bash
   # Windows
   net start MySQL80
   
   # Linux
   sudo systemctl status mysql
   
   # macOS
   brew services list
   ```

2. 检查端口是否正确（默认3306）
3. 检查用户名密码是否正确
4. 尝试手动连接：
   ```bash
   mysql -u root -p -h localhost
   ```

### 问题2：数据库不存在

**错误信息**：
```
pymysql.err.InternalError: (1049, "Unknown database 'ticket_system'")
```

**解决方案**：
重新执行建表脚本：
```bash
mysql -u root -p < sql/create_tables.sql
```

### 问题3：Python模块未找到

**错误信息**：
```
ModuleNotFoundError: No module named 'flask'
```

**解决方案**：
```bash
# 确保虚拟环境已激活
pip install -r requirements.txt
```

### 问题4：端口被占用

**错误信息**：
```
OSError: [Errno 98] Address already in use
```

**解决方案A**：修改端口

编辑 `run.py`：
```python
app.run(debug=True, host='0.0.0.0', port=8000)  # 改为8000
```

**解决方案B**：杀死占用进程

```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <进程ID> /F

# Linux/macOS
lsof -i :5000
kill -9 <PID>
```

### 问题5：中文显示乱码

**解决方案**：

1. 确保MySQL字符集为utf8mb4：
   ```sql
   SHOW VARIABLES LIKE 'character%';
   ```

2. 如果不是，修改MySQL配置文件（my.ini或my.cnf）：
   ```ini
   [mysqld]
   character-set-server=utf8mb4
   collation-server=utf8mb4_unicode_ci
   
   [client]
   default-character-set=utf8mb4
   ```

3. 重启MySQL服务

### 问题6：bcrypt安装失败（Windows）

**错误信息**：
```
error: Microsoft Visual C++ 14.0 is required
```

**解决方案**：

下载预编译版本：
```bash
pip install bcrypt --only-binary :all:
```

或安装Visual C++ Build Tools：
https://visualstudio.microsoft.com/downloads/

## 五、生产环境部署（可选）

### 使用Gunicorn（Linux/macOS）

```bash
# 安装gunicorn
pip install gunicorn

# 运行
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### 使用Nginx反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /path/to/Project/app/static;
    }
}
```

### 使用systemd管理服务（Linux）

创建 `/etc/systemd/system/ticket-system.service`：

```ini
[Unit]
Description=22306 Ticket System
After=network.target

[Service]
User=your-user
WorkingDirectory=/path/to/Project
Environment="PATH=/path/to/Project/venv/bin"
ExecStart=/path/to/Project/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 run:app

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl start ticket-system
sudo systemctl enable ticket-system
```

## 六、数据备份

### 备份数据库

```bash
# 全量备份
mysqldump -u root -p ticket_system > backup_$(date +%Y%m%d).sql

# 恢复备份
mysql -u root -p ticket_system < backup_20251206.sql
```

### 定时备份（Linux）

添加到crontab：
```bash
crontab -e

# 每天凌晨2点备份
0 2 * * * mysqldump -u root -pYourPassword ticket_system > /backup/ticket_$(date +\%Y\%m\%d).sql
```

## 七、卸载

### 停止服务
```bash
# 按 Ctrl+C 停止Flask应用
```

### 删除数据库
```bash
mysql -u root -p
DROP DATABASE ticket_system;
```

### 删除虚拟环境
```bash
# Windows
rmdir /s venv

# Linux/macOS
rm -rf venv
```

### 删除项目文件
直接删除项目目录即可。

## 八、获取帮助

如果遇到其他问题：

1. 查看 `README.md` 文档
2. 查看 `docs/` 目录下的详细文档
3. 检查Flask日志输出
4. 检查MySQL错误日志

---

**安装成功后，享受使用22306订票系统！** 🎉

