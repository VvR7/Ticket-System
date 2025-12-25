--数据库建表脚本

-- 创建数据库
DROP DATABASE IF EXISTS ticket_system;
CREATE DATABASE ticket_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ticket_system;

-- ============================================
-- 1. 用户与权限相关表
-- ============================================

-- 用户表
CREATE TABLE User (
    user_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
    password VARCHAR(255) NOT NULL COMMENT '密码（加密）',
    real_name VARCHAR(50) NOT NULL COMMENT '真实姓名',
    security_question VARCHAR(200) NOT NULL COMMENT '安全问题',
    security_answer VARCHAR(100) NOT NULL COMMENT '安全问题答案',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
    is_admin BOOLEAN DEFAULT FALSE COMMENT '是否为管理员',
    INDEX idx_username (username),
    INDEX idx_real_name (real_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 会话表
CREATE TABLE Session (
    session_id VARCHAR(64) PRIMARY KEY COMMENT '会话ID',
    user_id INT NOT NULL COMMENT '用户ID',
    login_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '登录时间',
    expire_time DATETIME NOT NULL COMMENT '过期时间',
    token VARCHAR(128) UNIQUE NOT NULL COMMENT '会话令牌',
    device_info VARCHAR(200) COMMENT '设备信息',
    INDEX idx_user_id (user_id),
    INDEX idx_token (token),
    INDEX idx_expire_time (expire_time),
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='会话表';

-- 管理员操作日志表
CREATE TABLE Admin_Log (
    log_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '日志ID',
    user_id INT COMMENT '操作管理员ID',
    operation_type VARCHAR(50) NOT NULL COMMENT '操作类型',
    operation_desc TEXT COMMENT '操作描述',
    target_table VARCHAR(50) COMMENT '操作的目标表',
    target_id INT COMMENT '操作的目标记录ID',
    operation_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    ip_address VARCHAR(50) COMMENT 'IP地址',
    INDEX idx_user_id (user_id),
    INDEX idx_operation_time (operation_time),
    INDEX idx_operation_type (operation_type),
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='管理员操作日志表';

-- ============================================
-- 2. 线路与车站相关表
-- ============================================

-- 车站信息表
CREATE TABLE Station (
    station_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '车站ID',
    station_name VARCHAR(100) NOT NULL COMMENT '车站名称',
    city VARCHAR(50) NOT NULL COMMENT '所在城市',
    province VARCHAR(50) NOT NULL COMMENT '所在省份',
    station_type ENUM('train', 'bus', 'both') NOT NULL COMMENT '车站类型',
    address VARCHAR(200) COMMENT '详细地址',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_city (city),
    INDEX idx_station_type (station_type),
    INDEX idx_station_name (station_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='车站信息表';

-- 线路信息表
CREATE TABLE Route (
    route_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '线路ID',
    route_name VARCHAR(100) NOT NULL COMMENT '线路名称',
    start_station_id INT NOT NULL COMMENT '起始站ID',
    end_station_id INT NOT NULL COMMENT '终点站ID',
    route_type ENUM('train', 'bus') NOT NULL COMMENT '线路类型',
    total_distance DECIMAL(10,2) COMMENT '总里程(km)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_start_station (start_station_id),
    INDEX idx_end_station (end_station_id),
    INDEX idx_route_type (route_type),
    FOREIGN KEY (start_station_id) REFERENCES Station(station_id),
    FOREIGN KEY (end_station_id) REFERENCES Station(station_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='线路信息表';

-- 线路站点表
CREATE TABLE Route_Station (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '记录ID',
    route_id INT NOT NULL COMMENT '线路ID',
    station_id INT NOT NULL COMMENT '车站ID',
    order_no INT NOT NULL COMMENT '站点顺序',
    distance_from_start DECIMAL(10,2) COMMENT '距离起点距离(km)',
    estimated_minutes INT COMMENT '预计到达分钟数',
    UNIQUE INDEX uk_route_order (route_id, order_no),
    INDEX idx_route_id (route_id),
    INDEX idx_station_id (station_id),
    FOREIGN KEY (route_id) REFERENCES Route(route_id) ON DELETE CASCADE,
    FOREIGN KEY (station_id) REFERENCES Station(station_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='线路站点表';

-- ============================================
-- 3. 车辆与座位相关表
-- ============================================

-- 车辆表
CREATE TABLE Vehicle (
    vehicle_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '车辆ID',
    vehicle_no VARCHAR(50) UNIQUE NOT NULL COMMENT '车辆编号',
    vehicle_type ENUM('train', 'bus') NOT NULL COMMENT '车辆类型',
    seat_count INT NOT NULL COMMENT '座位总数',
    seat_layout VARCHAR(50) COMMENT '座位布局',
    manufacturer VARCHAR(100) COMMENT '制造商',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_vehicle_type (vehicle_type),
    CHECK (seat_count > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='车辆表';

-- 座位表
CREATE TABLE Seat (
    seat_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '座位ID',
    vehicle_id INT NOT NULL COMMENT '车辆ID',
    seat_no VARCHAR(20) NOT NULL COMMENT '座位编号',
    seat_type ENUM('hard_seat', 'soft_seat', 'hard_sleeper', 'soft_sleeper', 'business', 'first_class', 'second_class') NOT NULL COMMENT '座位类型',
    carriage_no VARCHAR(10) COMMENT '车厢号',
    UNIQUE INDEX uk_vehicle_seat (vehicle_id, seat_no),
    INDEX idx_vehicle_id (vehicle_id),
    INDEX idx_seat_type (seat_type),
    FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='座位表';

-- ============================================
-- 4. 班次调度相关表
-- ============================================

-- 班次表
CREATE TABLE Schedule (
    schedule_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '班次ID',
    schedule_no VARCHAR(50) NOT NULL COMMENT '班次号',
    route_id INT NOT NULL COMMENT '线路ID',
    vehicle_id INT NOT NULL COMMENT '车辆ID',
    departure_date DATE NOT NULL COMMENT '发车日期',
    departure_time TIME NOT NULL COMMENT '发车时间',
    arrival_time TIME NOT NULL COMMENT '到达时间',
    base_price DECIMAL(10,2) NOT NULL COMMENT '基础票价',
    status ENUM('normal', 'delayed', 'cancelled') DEFAULT 'normal' COMMENT '班次状态',
    delay_minutes INT DEFAULT 0 COMMENT '延误分钟数',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UNIQUE INDEX uk_schedule_date (schedule_no, departure_date),
    INDEX idx_route_id (route_id),
    INDEX idx_vehicle_id (vehicle_id),
    INDEX idx_departure_date (departure_date),
    INDEX idx_status (status),
    FOREIGN KEY (route_id) REFERENCES Route(route_id),
    FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id),
    CHECK (base_price >= 0),
    CHECK (delay_minutes >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='班次表';

-- ============================================
-- 5. 售票业务相关表
-- ============================================

-- 订单表
CREATE TABLE `Order` (
    order_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '订单ID',
    user_id INT NOT NULL COMMENT '用户ID',
    schedule_id INT NOT NULL COMMENT '班次ID',
    order_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '下单时间',
    total_amount DECIMAL(10,2) NOT NULL COMMENT '订单总金额',
    ticket_count INT NOT NULL COMMENT '票数',
    order_type ENUM('individual', 'group') DEFAULT 'individual' COMMENT '订单类型',
    status ENUM('pending', 'confirmed', 'cancelled', 'refunded') DEFAULT 'confirmed' COMMENT '订单状态',
    INDEX idx_user_id (user_id),
    INDEX idx_schedule_id (schedule_id),
    INDEX idx_order_time (order_time),
    INDEX idx_status (status),
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE,
    FOREIGN KEY (schedule_id) REFERENCES Schedule(schedule_id),
    CHECK (total_amount >= 0),
    CHECK (ticket_count > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单表';

-- 车票表
CREATE TABLE Ticket (
    ticket_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '车票ID',
    order_id INT NOT NULL COMMENT '订单ID',
    schedule_id INT NOT NULL COMMENT '班次ID',
    seat_id INT NOT NULL COMMENT '座位ID',
    passenger_name VARCHAR(50) NOT NULL COMMENT '乘客姓名',
    card_id VARCHAR(18) NOT NULL COMMENT '身份证号',
    price DECIMAL(10,2) NOT NULL COMMENT '票价',
    status ENUM('valid', 'refunded') DEFAULT 'valid' COMMENT '车票状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UNIQUE INDEX uk_schedule_seat_valid (schedule_id, seat_id, status),
    INDEX idx_order_id (order_id),
    INDEX idx_schedule_id (schedule_id),
    INDEX idx_seat_id (seat_id),
    INDEX idx_passenger_name (passenger_name),
    INDEX idx_status (status),
    INDEX idx_card_id (card_id),
    FOREIGN KEY (order_id) REFERENCES `Order`(order_id) ON DELETE CASCADE,
    FOREIGN KEY (schedule_id) REFERENCES Schedule(schedule_id),
    FOREIGN KEY (seat_id) REFERENCES Seat(seat_id),
    CHECK (price >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='车票表';

-- 退票记录表
CREATE TABLE Refund (
    refund_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '退票ID',
    ticket_id INT UNIQUE NOT NULL COMMENT '车票ID',
    refund_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '退票时间',
    refund_amount DECIMAL(10,2) NOT NULL COMMENT '退款金额',
    refund_reason TEXT COMMENT '退票原因',
    handled_by INT COMMENT '处理人ID',
    INDEX idx_refund_time (refund_time),
    FOREIGN KEY (ticket_id) REFERENCES Ticket(ticket_id),
    FOREIGN KEY (handled_by) REFERENCES User(user_id),
    CHECK (refund_amount >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='退票记录表';

-- ============================================
-- 创建管理员账号
-- ============================================

-- 插入管理员账号 (密码: 23336326, 使用bcrypt加密)
-- 注意：实际密码hash需要在应用层生成
INSERT INTO User (username, password, real_name, security_question, security_answer, is_admin) 
VALUES ('Admin', '$2b$12$KIXxLfZ8qJz.KvJYvN3zVeYXqN3YqGJ8kN3zVeYXqN3YqGJ8kN3zVe', '系统管理员', '管理员密保问题', '管理员密保答案', TRUE);

