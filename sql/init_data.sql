-- 22306订票系统 初始化数据脚本
USE ticket_system;

-- ============================================
-- 1. 插入车站数据
-- ============================================

INSERT INTO Station (station_name, city, province, station_type, address) VALUES
-- 北京
('北京站', '北京', '北京市', 'both', '北京市东城区毛家湾胡同甲13号'),
('北京西站', '北京', '北京市', 'train', '北京市丰台区莲花池东路118号'),
('北京南站', '北京', '北京市', 'train', '北京市丰台区永外大街12号'),
('北京六里桥客运站', '北京', '北京市', 'bus', '北京市丰台区六里桥南里甲1号'),

-- 上海
('上海站', '上海', '上海市', 'both', '上海市静安区秣陵路303号'),
('上海虹桥站', '上海', '上海市', 'train', '上海市闵行区申虹路'),
('上海南站', '上海', '上海市', 'train', '上海市徐汇区沪闵路9001号'),
('上海长途汽车客运总站', '上海', '上海市', 'bus', '上海市静安区中兴路1666号'),

-- 广州
('广州站', '广州', '广东省', 'both', '广东省广州市越秀区环市西路'),
('广州南站', '广州', '广东省', 'train', '广东省广州市番禺区石壁街道南站北路'),
('广州东站', '广州', '广东省', 'train', '广东省广州市天河区林和街道东站路1号'),
('广州省汽车客运站', '广州', '广东省', 'bus', '广东省广州市越秀区环市西路145号'),

-- 深圳
('深圳站', '深圳', '广东省', 'both', '广东省深圳市罗湖区和平路'),
('深圳北站', '深圳', '广东省', 'train', '广东省深圳市龙华区民治街道'),
('深圳福田汽车站', '深圳', '广东省', 'bus', '广东省深圳市福田区深南大道竹子林'),

-- 杭州
('杭州站', '杭州', '浙江省', 'both', '浙江省杭州市上城区环城东路1号'),
('杭州东站', '杭州', '浙江省', 'train', '浙江省杭州市江干区天城路1号'),
('杭州汽车客运中心', '杭州', '浙江省', 'bus', '浙江省杭州市江干区九堡镇德胜东路3339号'),

-- 南京
('南京站', '南京', '江苏省', 'both', '江苏省南京市玄武区龙蟠路111号'),
('南京南站', '南京', '江苏省', 'train', '江苏省南京市雨花台区玉兰路98号'),
('南京汽车客运站', '南京', '江苏省', 'bus', '江苏省南京市建邺区集庆门大街268号'),

-- 武汉
('武汉站', '武汉', '湖北省', 'train', '湖北省武汉市洪山区杨春湖'),
('武汉汉口站', '武汉', '湖北省', 'both', '湖北省武汉市江汉区发展大道'),
('武汉宏基汽车客运站', '武汉', '湖北省', 'bus', '湖北省武汉市洪山区青菱乡'),

-- 成都
('成都站', '成都', '四川省', 'both', '四川省成都市金牛区荷花池街道北站西一路'),
('成都东站', '成都', '四川省', 'train', '四川省成都市成华区保和街道邛崃山路'),
('成都五桂桥汽车站', '成都', '四川省', 'bus', '四川省成都市成华区迎晖路196号'),

-- 西安
('西安站', '西安', '陕西省', 'both', '陕西省西安市新城区环城北路44号'),
('西安北站', '西安', '陕西省', 'train', '陕西省西安市未央区元朔路'),
('西安城北客运站', '西安', '陕西省', 'bus', '陕西省西安市未央区纬二十六街');

-- ============================================
-- 2. 插入车辆数据
-- ============================================

INSERT INTO Vehicle (vehicle_no, vehicle_type, seat_count, seat_layout, manufacturer) VALUES
-- 火车车辆
('CR400AF-0001', 'train', 556, '3+2', '中国中车'),
('CR400BF-0002', 'train', 600, '3+2', '中国中车'),
('CR400BF-0003', 'train', 600, '3+2', '中国中车'),
('CRH380A-0001', 'train', 494, '3+2', '中国中车'),
('CRH380A-0002', 'train', 494, '3+2', '中国中车'),

-- 长途客车
('京B-88888', 'bus', 45, '2+2', '宇通客车'),
('京B-88889', 'bus', 45, '2+2', '宇通客车'),
('沪A-66666', 'bus', 50, '2+2', '金龙客车'),
('沪A-66667', 'bus', 50, '2+2', '金龙客车'),
('粤A-99999', 'bus', 40, '2+2', '比亚迪客车');

-- ============================================
-- 3. 生成座位数据
-- ============================================

-- 为火车生成座位（以CR400AF-0001为例，生成556个座位）
-- 商务座 (1车厢，10座)
INSERT INTO Seat (vehicle_id, seat_no, seat_type, carriage_no)
SELECT 1, CONCAT(seat_num, CHAR(64 + row_letter)), 'business', '01'
FROM (SELECT 1 AS seat_num UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) seats
CROSS JOIN (SELECT 1 AS row_letter UNION SELECT 2) letters;

-- 一等座 (2-3车厢，每车厢50座，共100座)
INSERT INTO Seat (vehicle_id, seat_no, seat_type, carriage_no)
SELECT 1, CONCAT(carriage, '-', seat_num, CHAR(64 + row_letter)), 'first_class', LPAD(carriage, 2, '0')
FROM (SELECT 2 AS carriage UNION SELECT 3) carriages
CROSS JOIN (SELECT 1 AS seat_num UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 
            UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10) seats
CROSS JOIN (SELECT 1 AS row_letter UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) letters;

-- 二等座 (4-16车厢，每车厢40座，部分车厢省略，这里示例生成部分)
INSERT INTO Seat (vehicle_id, seat_no, seat_type, carriage_no)
SELECT 1, CONCAT('04-', seat_num, CHAR(64 + row_letter)), 'second_class', '04'
FROM (SELECT 1 AS seat_num UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 
      UNION SELECT 6 UNION SELECT 7 UNION SELECT 8) seats
CROSS JOIN (SELECT 1 AS row_letter UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) letters;

-- 为长途客车生成座位（以京B-88888为例，45座）
INSERT INTO Seat (vehicle_id, seat_no, seat_type, carriage_no)
SELECT 6, LPAD(seat_num, 2, '0'), 'soft_seat', NULL
FROM (
    SELECT 1 AS seat_num UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5
    UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10
    UNION SELECT 11 UNION SELECT 12 UNION SELECT 13 UNION SELECT 14 UNION SELECT 15
    UNION SELECT 16 UNION SELECT 17 UNION SELECT 18 UNION SELECT 19 UNION SELECT 20
    UNION SELECT 21 UNION SELECT 22 UNION SELECT 23 UNION SELECT 24 UNION SELECT 25
    UNION SELECT 26 UNION SELECT 27 UNION SELECT 28 UNION SELECT 29 UNION SELECT 30
    UNION SELECT 31 UNION SELECT 32 UNION SELECT 33 UNION SELECT 34 UNION SELECT 35
    UNION SELECT 36 UNION SELECT 37 UNION SELECT 38 UNION SELECT 39 UNION SELECT 40
    UNION SELECT 41 UNION SELECT 42 UNION SELECT 43 UNION SELECT 44 UNION SELECT 45
) seats;

-- ============================================
-- 4. 插入线路数据
-- ============================================

INSERT INTO Route (route_name, start_station_id, end_station_id, route_type, total_distance) VALUES
-- 火车线路
('京沪高铁', 1, 5, 'train', 1318.0),
('京广高铁-北京至广州段', 1, 9, 'train', 2298.0),
('沪杭高铁', 5, 16, 'train', 159.0),
('京杭线', 1, 16, 'train', 1200.0),

-- 长途客车线路
('北京-天津客运', 4, 5, 'bus', 120.0),
('上海-杭州客运', 8, 18, 'bus', 180.0),
('广州-深圳客运', 12, 13, 'bus', 120.0);

-- ============================================
-- 5. 插入线路站点数据
-- ============================================

-- 京沪高铁站点 (北京站 -> 南京南站 -> 上海站)
INSERT INTO Route_Station (route_id, station_id, order_no, distance_from_start, estimated_minutes) VALUES
(1, 1, 1, 0, 0),           -- 北京站
(1, 20, 2, 1023, 240),     -- 南京南站
(1, 5, 3, 1318, 300);      -- 上海站

-- 京广高铁站点 (北京站 -> 武汉站 -> 广州站)
INSERT INTO Route_Station (route_id, station_id, order_no, distance_from_start, estimated_minutes) VALUES
(2, 1, 1, 0, 0),           -- 北京站
(2, 22, 2, 1200, 280),     -- 武汉站
(2, 9, 3, 2298, 520);      -- 广州站

-- 沪杭高铁站点 (上海站 -> 杭州东站)
INSERT INTO Route_Station (route_id, station_id, order_no, distance_from_start, estimated_minutes) VALUES
(3, 5, 1, 0, 0),           -- 上海站
(3, 17, 2, 159, 45);       -- 杭州东站

-- 北京-天津客运
INSERT INTO Route_Station (route_id, station_id, order_no, distance_from_start, estimated_minutes) VALUES
(5, 4, 1, 0, 0),           -- 北京六里桥客运站
(5, 5, 2, 120, 90);        -- 上海站(示例)

-- 广州-深圳客运
INSERT INTO Route_Station (route_id, station_id, order_no, distance_from_start, estimated_minutes) VALUES
(7, 12, 1, 0, 0),          -- 广州省汽车客运站
(7, 15, 2, 40, 45),        -- 深圳福田汽车站(中途站)
(7, 13, 3, 120, 120);      -- 深圳站

-- ============================================
-- 6. 插入班次数据
-- ============================================

-- 京沪高铁班次 G1次 (每天)
INSERT INTO Schedule (schedule_no, route_id, vehicle_id, departure_date, departure_time, arrival_time, base_price, status) VALUES
('G1', 1, 1, CURDATE(), '08:00:00', '13:00:00', 553.5, 'normal'),
('G1', 1, 1, DATE_ADD(CURDATE(), INTERVAL 1 DAY), '08:00:00', '13:00:00', 553.5, 'normal'),
('G1', 1, 1, DATE_ADD(CURDATE(), INTERVAL 2 DAY), '08:00:00', '13:00:00', 553.5, 'normal'),
('G1', 1, 1, DATE_ADD(CURDATE(), INTERVAL 3 DAY), '08:00:00', '13:00:00', 553.5, 'normal'),
('G1', 1, 1, DATE_ADD(CURDATE(), INTERVAL 4 DAY), '08:00:00', '13:00:00', 553.5, 'normal'),
('G1', 1, 1, DATE_ADD(CURDATE(), INTERVAL 5 DAY), '08:00:00', '13:00:00', 553.5, 'normal'),
('G1', 1, 1, DATE_ADD(CURDATE(), INTERVAL 6 DAY), '08:00:00', '13:00:00', 553.5, 'normal');

-- 京沪高铁班次 G2次 (下午)
INSERT INTO Schedule (schedule_no, route_id, vehicle_id, departure_date, departure_time, arrival_time, base_price, status) VALUES
('G2', 1, 2, CURDATE(), '14:00:00', '19:00:00', 553.5, 'normal'),
('G2', 1, 2, DATE_ADD(CURDATE(), INTERVAL 1 DAY), '14:00:00', '19:00:00', 553.5, 'normal'),
('G2', 1, 2, DATE_ADD(CURDATE(), INTERVAL 2 DAY), '14:00:00', '19:00:00', 553.5, 'normal');

-- 京广高铁班次 G100次
INSERT INTO Schedule (schedule_no, route_id, vehicle_id, departure_date, departure_time, arrival_time, base_price, status) VALUES
('G100', 2, 3, CURDATE(), '09:00:00', '17:40:00', 862.0, 'normal'),
('G100', 2, 3, DATE_ADD(CURDATE(), INTERVAL 1 DAY), '09:00:00', '17:40:00', 862.0, 'normal'),
('G100', 2, 3, DATE_ADD(CURDATE(), INTERVAL 2 DAY), '09:00:00', '17:40:00', 862.0, 'delayed', 30);

-- 沪杭高铁班次 G7301次
INSERT INTO Schedule (schedule_no, route_id, vehicle_id, departure_date, departure_time, arrival_time, base_price, status) VALUES
('G7301', 3, 4, CURDATE(), '07:00:00', '07:45:00', 73.0, 'normal'),
('G7301', 3, 4, DATE_ADD(CURDATE(), INTERVAL 1 DAY), '07:00:00', '07:45:00', 73.0, 'normal');

-- 广州-深圳客运 (长途客车)
INSERT INTO Schedule (schedule_no, route_id, vehicle_id, departure_date, departure_time, arrival_time, base_price, status) VALUES
('粤A-001', 7, 10, CURDATE(), '08:00:00', '10:00:00', 50.0, 'normal'),
('粤A-001', 7, 10, DATE_ADD(CURDATE(), INTERVAL 1 DAY), '08:00:00', '10:00:00', 50.0, 'normal'),
('粤A-002', 7, 10, CURDATE(), '14:00:00', '16:00:00', 50.0, 'normal');



-- 管理员用户（密码为明文，用于测试）
INSERT INTO User (username, password, real_name, security_question, security_answer, is_admin) VALUES
('Admin', '23336326', '系统管理员', '你的角色是什么？', '管理员', TRUE);



COMMIT;

