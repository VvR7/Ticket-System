# 22306订票系统

一个基于Flask的车站售票管理系统，面向长途汽车与火车售票业务。

## 项目简介

22306订票系统是一个功能完善的在线售票平台，提供：
- 💻 用户注册登录、密码找回功能
- 🔍 多条件车次查询
- 🎫 个人/团体订票功能
- 📋 订单管理与退票
- 🛠️ 管理员后台管理
- 📊 完善的报表系统

## 技术栈

### 后端
- **框架**：Python 3.x + Flask 2.3.3
- **数据库**：MySQL 8.0
- **ORM**：pymysql
- **安全**：bcrypt（密码加密）
- **跨域**：flask-cors

### 前端
- **语言**：HTML5 + CSS3 + JavaScript（原生）
- **样式**：自定义CSS（响应式设计）
- **交互**：原生Fetch API

## 项目结构

```
Project/
├── app/                          # 应用主目录
│   ├── __init__.py              # Flask应用初始化
│   ├── config.py                # 配置文件
│   ├── database.py              # 数据库连接管理
│   ├── routes/                  # 路由模块
│   │   ├── auth.py             # 认证路由（注册、登录、找回密码）
│   │   ├── ticket.py           # 售票路由（查询、订票、退票）
│   │   └── admin.py            # 管理员路由
│   ├── static/                  # 静态资源
│   │   ├── css/style.css       # 全局样式
│   │   └── js/common.js        # 通用JavaScript函数
│   └── templates/               # HTML模板
│       ├── index.html          # 首页
│       ├── login.html          # 登录页
│       ├── register.html       # 注册页
│       ├── search.html         # 车票查询
│       ├── booking.html        # 订票页面
│       ├── my_orders.html      # 我的订单
│       ├── admin.html          # 管理后台
│       └── reset_password.html # 重置密码
├── docs/                        # 文档目录
│   ├── 功能需求分析.md
│   ├── 系统数据字典.md
│   ├── 数据库关系模式设计.md
│   ├── 数据库设计说明.md
│   └── 系统功能实现描述.md
├── sql/                         # SQL脚本
│   ├── create_tables.sql       # 数据库建表脚本
│   └── init_data.sql           # 初始化数据
├── run.py                       # 程序入口
├── requirements.txt             # Python依赖
└── README.md                    # 本文件
```

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
# 建议先创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
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
MYSQL_PASSWORD = '123456'  # 改为你的MySQL密码
MYSQL_DATABASE = 'ticket_system'
```

**方法二：使用环境变量**（推荐）

```bash
# Windows
set MYSQL_PASSWORD=你的密码

# Linux/Mac
export MYSQL_PASSWORD=你的密码
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

## 功能说明

### 用户功能

#### 1. 注册与登录
- 注册新账号（需要设置安全问题）
- 用户登录
- 找回密码（通过安全问题）

#### 2. 车票查询
支持多种查询方式：
- 按出发城市查询
- 按到达城市查询
- 按日期查询
- 按车次号查询
- 组合查询

#### 3. 订票
- 查看座位布局
- 选择座位（可视化）
- 填写乘客信息（支持身份证验证）
- 个人订票：单张车票
- 团体订票：一次订购多张

#### 4. 订单管理
- 查看所有订单
- 查看订单详情（包含所有车票）
- 退票操作
- 订单状态跟踪

### 管理员功能

登录管理员账号后可访问管理后台（`/admin`）：

#### 1. 车站管理
- 添加车站
- 删除车站
- 查看车站列表

#### 2. 线路管理
- 添加线路
- 删除线路
- 查看线路列表

#### 3. 班次管理
- 添加班次
- 删除班次
- 更新班次信息（时间、票价、状态、延误）
- 批量修改票价（按线路统一修改）

#### 4. 报表系统
- **销售报表**：按日期统计销售额、订单数、票数
- **班次统计**：各班次运营情况、收入统计
- **退票统计**：退票数量和金额
- **报表导出**：导出CSV格式报表

#### 5. 操作日志
- 查看所有管理员操作记录
- 包含操作时间、操作类型、IP地址等

## 默认账号

### 管理员账号
- 用户名：`Admin`
- 密码：`23336326`

### 测试账号
系统已预置3个测试用户：
- 用户名：`test001`, `test002`, `test003`
- 密码：需要重新注册或使用找回密码功能

## 数据库设计

### 核心表结构

- **User**：用户表
- **Session**：会话表
- **Station**：车站表
- **Route**：线路表
- **Route_Station**：线路站点关联表
- **Vehicle**：车辆表
- **Seat**：座位表
- **Schedule**：班次表
- **Order**：订单表
- **Ticket**：车票表
- **Refund**：退票记录表
- **Admin_Log**：管理员操作日志表

详细的数据库设计请查看 `docs/数据库关系模式设计.md`

### 关键技术

1. **事务管理**：订票和退票使用事务确保数据一致性
2. **并发控制**：使用悲观锁（FOR UPDATE）防止超卖
3. **索引优化**：为高频查询字段建立索引
4. **外键约束**：保证引用完整性
5. **唯一约束**：防止座位重复售出

## API接口

### 认证相关
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出
- `POST /api/auth/reset_password` - 重置密码
- `GET /api/auth/get_security_question` - 获取安全问题
- `GET /api/auth/check_session` - 检查登录状态

### 售票相关
- `GET /api/ticket/search` - 查询班次
- `GET /api/ticket/schedule/<id>/seats` - 获取座位信息
- `POST /api/ticket/book` - 订票
- `GET /api/ticket/my_orders` - 我的订单
- `POST /api/ticket/refund` - 退票
- `GET /api/ticket/stations` - 获取车站列表
- `GET /api/ticket/cities` - 获取城市列表

### 管理员相关
- `POST /api/admin/station/add` - 添加车站
- `DELETE /api/admin/station/<id>` - 删除车站
- `POST /api/admin/schedule/add` - 添加班次
- `PUT /api/admin/schedule/<id>` - 更新班次
- `DELETE /api/admin/schedule/<id>` - 删除班次
- `POST /api/admin/schedule/batch_update_price` - 批量更新票价
- `GET /api/admin/report/sales` - 销售报表
- `GET /api/admin/report/schedule` - 班次报表
- `GET /api/admin/report/export` - 导出报表
- `GET /api/admin/logs` - 操作日志

## 项目文档

所有详细文档位于 `docs/` 目录：

1. **功能需求分析.md** - 系统功能模块详细说明
2. **系统数据字典.md** - 数据库字段详细说明
3. **数据库关系模式设计.md** - ER图和关系模式
4. **数据库设计说明.md** - 索引、并发、性能优化
5. **系统功能实现描述.md** - 主要功能的技术实现

## 开发说明

### 添加新功能

1. **后端**：在 `app/routes/` 下创建新的路由文件
2. **前端**：在 `app/templates/` 下创建HTML模板
3. **样式**：在 `app/static/css/style.css` 中添加样式
4. **脚本**：在 `app/static/js/` 中添加JavaScript文件

### 数据库迁移

修改数据库结构后：
1. 更新 `sql/create_tables.sql`
2. 创建迁移脚本
3. 更新文档

### 调试模式

开发时Flask运行在调试模式（`debug=True`），会自动重载代码。

生产环境请设置 `debug=False`。

## 常见问题

### 1. 数据库连接失败

**错误**：`Can't connect to MySQL server`

**解决**：
- 检查MySQL是否启动
- 检查 `config.py` 中的数据库配置
- 确认MySQL密码正确

### 2. 导入模块失败

**错误**：`ModuleNotFoundError: No module named 'flask'`

**解决**：
```bash
pip install -r requirements.txt
```

### 3. 端口被占用

**错误**：`Address already in use`

**解决**：
- 修改 `run.py` 中的端口号
- 或杀死占用5000端口的进程

### 4. 中文乱码

**解决**：
- 确保MySQL字符集为 `utf8mb4`
- 确保Python文件编码为 `UTF-8`

## 性能优化建议

1. **使用缓存**：为静态数据（车站列表、城市列表）添加缓存
2. **连接池**：使用数据库连接池
3. **索引优化**：根据慢查询日志优化索引
4. **读写分离**：高并发场景下配置主从复制
5. **CDN**：静态资源使用CDN加速

## 安全建议

1. **生产环境**：
   - 修改管理员默认密码
   - 使用强密码策略
   - 配置HTTPS
   - 启用防火墙

2. **数据库**：
   - 定期备份数据
   - 限制远程访问
   - 使用专用数据库账号

3. **应用**：
   - 配置SESSION密钥
   - 启用CSRF保护
   - 定期更新依赖包

## 许可证

本项目仅用于学习和教学目的。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交Issue
- 发送邮件

## 更新日志

### v1.0.0 (2025-12-06)
- ✅ 初始版本发布
- ✅ 完整的用户功能
- ✅ 完整的管理员功能
- ✅ 报表系统
- ✅ 操作日志
- ✅ 完整文档

---

**22306订票系统** - 让出行更便捷 🚄

