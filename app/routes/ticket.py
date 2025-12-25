# -*- coding: utf-8 -*-
"""
售票相关路由
"""
from flask import Blueprint, request, jsonify, session
from datetime import datetime
from app.database import db, Database
import pymysql

ticket_bp = Blueprint('ticket', __name__, url_prefix='/api/ticket')


def require_login(f):
    """登录装饰器"""
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper


@ticket_bp.route('/search', methods=['GET'])
def search_schedules():
    date = request.args.get('date')
    start_city = request.args.get('start_city')
    end_city = request.args.get('end_city')
    start_station_id = request.args.get('start_station_id')
    end_station_id = request.args.get('end_station_id')
    schedule_no = request.args.get('schedule_no')
    
    # 构建查询SQL
    sql = """
        SELECT 
            s.schedule_id,
            s.schedule_no,
            s.departure_date,
            s.departure_time,
            s.arrival_time,
            s.base_price,
            s.status,
            s.delay_minutes,
            r.route_name,
            r.route_type,
            r.total_distance,
            st_start.station_name AS start_station,
            st_start.city AS start_city,
            st_end.station_name AS end_station,
            st_end.city AS end_city,
            v.vehicle_no,
            v.vehicle_type,
            v.seat_count,
            v.seat_count - COALESCE(
                (SELECT COUNT(*) FROM Ticket t 
                 WHERE t.schedule_id = s.schedule_id AND t.status = 'valid'), 0
            ) AS available_seats
        FROM Schedule s
        JOIN Route r ON s.route_id = r.route_id
        JOIN Station st_start ON r.start_station_id = st_start.station_id
        JOIN Station st_end ON r.end_station_id = st_end.station_id
        JOIN Vehicle v ON s.vehicle_id = v.vehicle_id
        WHERE 1=1
    """
    
    params = []
    
    if date:
        sql += " AND s.departure_date = %s"
        params.append(date)
    
    if start_city:
        sql += " AND st_start.city LIKE %s"
        params.append(f'%{start_city}%')
    
    if end_city:
        sql += " AND st_end.city LIKE %s"
        params.append(f'%{end_city}%')
    
    if start_station_id:
        sql += " AND r.start_station_id = %s"
        params.append(start_station_id)
    
    if end_station_id:
        sql += " AND r.end_station_id = %s"
        params.append(end_station_id)
    
    if schedule_no:
        sql += " AND s.schedule_no LIKE %s"
        params.append(f'%{schedule_no}%')
    
    sql += " ORDER BY s.departure_date, s.departure_time"
    
    try:
        results = db.execute_query(sql, params)
        
        # 格式化时间字段
        for result in results:
            if result['departure_date']:
                result['departure_date'] = result['departure_date'].strftime('%Y-%m-%d')
            if result['departure_time']:
                result['departure_time'] = str(result['departure_time'])
            if result['arrival_time']:
                result['arrival_time'] = str(result['arrival_time'])
        
        return jsonify({
            'success': True,
            'schedules': results
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败: {str(e)}'}), 500


@ticket_bp.route('/schedule/<int:schedule_id>', methods=['GET'])
def get_schedule_info(schedule_id):
    """获取班次详细信息"""
    try:
        sql = """
            SELECT 
                s.schedule_id,
                s.schedule_no,
                s.departure_date,
                s.departure_time,
                s.arrival_time,
                s.base_price,
                s.status,
                s.delay_minutes,
                r.route_name,
                r.route_type,
                r.total_distance,
                st_start.station_name AS start_station,
                st_start.city AS start_city,
                st_end.station_name AS end_station,
                st_end.city AS end_city,
                v.vehicle_no,
                v.vehicle_type,
                v.seat_count,
                v.seat_count - COALESCE(
                    (SELECT COUNT(*) FROM Ticket t 
                     WHERE t.schedule_id = s.schedule_id AND t.status = 'valid'), 0
                ) AS available_seats
            FROM Schedule s
            JOIN Route r ON s.route_id = r.route_id
            JOIN Station st_start ON r.start_station_id = st_start.station_id
            JOIN Station st_end ON r.end_station_id = st_end.station_id
            JOIN Vehicle v ON s.vehicle_id = v.vehicle_id
            WHERE s.schedule_id = %s
        """
        
        schedule = db.execute_query(sql, (schedule_id,), fetch_one=True)
        
        if not schedule:
            return jsonify({'success': False, 'message': '班次不存在'}), 404
        
        # 格式化时间字段
        if schedule['departure_date']:
            schedule['departure_date'] = schedule['departure_date'].strftime('%Y-%m-%d')
        if schedule['departure_time']:
            schedule['departure_time'] = str(schedule['departure_time'])
        if schedule['arrival_time']:
            schedule['arrival_time'] = str(schedule['arrival_time'])
        
        return jsonify({
            'success': True,
            'schedule': schedule
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败: {str(e)}'}), 500


@ticket_bp.route('/schedule/<int:schedule_id>/seats', methods=['GET'])
def get_available_seats(schedule_id):
    """获取班次的可用座位"""
    try:
        # 获取班次信息
        schedule = db.execute_query(
            "SELECT vehicle_id FROM Schedule WHERE schedule_id = %s",
            (schedule_id,),
            fetch_one=True
        )
        
        if not schedule:
            return jsonify({'success': False, 'message': '班次不存在'}), 404
        
        # 获取该车辆的所有座位
        sql = """
            SELECT 
                s.seat_id,
                s.seat_no,
                s.seat_type,
                s.carriage_no,
                CASE 
                    WHEN t.ticket_id IS NOT NULL THEN 'occupied'
                    ELSE 'available'
                END AS seat_status
            FROM Seat s
            LEFT JOIN Ticket t ON s.seat_id = t.seat_id 
                AND t.schedule_id = %s 
                AND t.status = 'valid'
            WHERE s.vehicle_id = %s
            ORDER BY s.carriage_no, s.seat_no
        """
        
        seats = db.execute_query(sql, (schedule_id, schedule['vehicle_id']))
        
        return jsonify({
            'success': True,
            'seats': seats
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败: {str(e)}'}), 500


@ticket_bp.route('/book', methods=['POST'])
@require_login
def book_ticket():
    """
    订票
    支持个人和团体订票
    支持死锁自动重试机制
    """
    data = request.get_json()
    user_id = session['user_id']
    
    schedule_id = data.get('schedule_id')
    passengers = data.get('passengers')  # [{name, card_id, seat_id}, ...]
    
    if not schedule_id or not passengers or len(passengers) == 0:
        return jsonify({'success': False, 'message': '缺少必填字段'}), 400
    
    # 判断是否为团体订票
    order_type = 'group' if len(passengers) > 1 else 'individual'
    
    # 使用装饰器包装的订票逻辑，支持死锁自动重试
    @Database.retry_on_deadlock(max_retries=3)
    def _do_book_ticket():
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            # 开始事务
            conn.begin()
            
            # 检查提交的乘客列表中是否有重复的身份证号
            card_ids = [p['card_id'] for p in passengers]
            if len(card_ids) != len(set(card_ids)):
                conn.rollback()
                raise Exception('同一订单中不能包含相同的身份证号')
            
            # 检查这些身份证号是否已经在该车次订过票
            card_placeholders = ','.join(['%s'] * len(card_ids))
            check_card_sql = f"""
                SELECT card_id FROM Ticket 
                WHERE schedule_id = %s 
                AND card_id IN ({card_placeholders})
                AND status = 'valid'
            """
            cursor.execute(check_card_sql, [schedule_id] + card_ids)
            existing_cards = cursor.fetchall()
            
            if existing_cards:
                existing_card_list = ', '.join([c['card_id'] for c in existing_cards])
                conn.rollback()
                raise Exception(f'身份证号 {existing_card_list} 已在该车次订票，每个身份证号只能订一张票')
            
            # 锁定座位（悲观锁）
            seat_ids = [p['seat_id'] for p in passengers]
            placeholders = ','.join(['%s'] * len(seat_ids))
            
            # 检查座位是否可用
            check_sql = f"""
                SELECT seat_id FROM Ticket 
                WHERE schedule_id = %s 
                AND seat_id IN ({placeholders})
                AND status = 'valid'
                FOR UPDATE
            """
            cursor.execute(check_sql, [schedule_id] + seat_ids)
            occupied_seats = cursor.fetchall()
            
            if occupied_seats:
                conn.rollback()
                raise Exception('所选座位已被占用')
            
            # 获取票价
            cursor.execute(
                "SELECT base_price FROM Schedule WHERE schedule_id = %s",
                (schedule_id,)
            )
            schedule = cursor.fetchone()
            
            if not schedule:
                conn.rollback()
                raise Exception('班次不存在')
            
            base_price = float(schedule['base_price'])
            total_amount = base_price * len(passengers)
            
            # 创建订单
            cursor.execute(
                """INSERT INTO `Order` (user_id, schedule_id, order_time, total_amount, ticket_count, order_type, status)
                   VALUES (%s, %s, %s, %s, %s, %s, 'confirmed')""",
                (user_id, schedule_id, datetime.now(), total_amount, len(passengers), order_type)
            )
            order_id = cursor.lastrowid
            
            # 创建车票
            for passenger in passengers:
                cursor.execute(
                    """INSERT INTO Ticket (order_id, schedule_id, seat_id, passenger_name, card_id, price, status)
                       VALUES (%s, %s, %s, %s, %s, %s, 'valid')""",
                    (order_id, schedule_id, passenger['seat_id'], passenger['name'], 
                     passenger['card_id'], base_price)
                )
        
            # 提交事务
            conn.commit()
            
            return {
                'success': True,
                'message': '订票成功',
                'order_id': order_id,
                'total_amount': total_amount
            }
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    # 执行订票逻辑（带死锁重试）
    try:
        result = _do_book_ticket()
        return jsonify(result), 201
    except Exception as e:
        return jsonify({'success': False, 'message': f'订票失败: {str(e)}'}), 500


@ticket_bp.route('/my_orders', methods=['GET'])
@require_login
def get_my_orders():
    """获取我的订单"""
    user_id = session['user_id']
    
    sql = """
        SELECT 
            o.order_id,
            o.order_time,
            o.total_amount,
            o.ticket_count,
            o.order_type,
            o.status,
            s.schedule_no,
            s.departure_date,
            s.departure_time,
            s.arrival_time,
            r.route_name,
            st_start.station_name AS start_station,
            st_end.station_name AS end_station
        FROM `Order` o
        JOIN Schedule s ON o.schedule_id = s.schedule_id
        JOIN Route r ON s.route_id = r.route_id
        JOIN Station st_start ON r.start_station_id = st_start.station_id
        JOIN Station st_end ON r.end_station_id = st_end.station_id
        WHERE o.user_id = %s
        ORDER BY o.order_time DESC
    """
    
    try:
        orders = db.execute_query(sql, (user_id,))
        
        # 格式化时间
        for order in orders:
            if order['order_time']:
                order['order_time'] = order['order_time'].strftime('%Y-%m-%d %H:%M:%S')
            if order['departure_date']:
                order['departure_date'] = order['departure_date'].strftime('%Y-%m-%d')
            if order['departure_time']:
                order['departure_time'] = str(order['departure_time'])
            if order['arrival_time']:
                order['arrival_time'] = str(order['arrival_time'])
            
            # 获取订单的车票详情
            tickets = db.execute_query(
                """SELECT 
                    t.ticket_id,
                    t.passenger_name,
                    t.card_id,
                    t.price,
                    t.status,
                    se.seat_no,
                    se.seat_type,
                    se.carriage_no
                FROM Ticket t
                JOIN Seat se ON t.seat_id = se.seat_id
                WHERE t.order_id = %s""",
                (order['order_id'],)
            )
            order['tickets'] = tickets
        
        return jsonify({
            'success': True,
            'orders': orders
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败: {str(e)}'}), 500


@ticket_bp.route('/refund', methods=['POST'])
@require_login
def refund_ticket():
    """退票 - 支持死锁自动重试机制"""
    data = request.get_json()
    user_id = session['user_id']
    
    ticket_ids = data.get('ticket_ids')  # 可以退一张或多张
    refund_reason = data.get('refund_reason', '')
    
    if not ticket_ids or len(ticket_ids) == 0:
        return jsonify({'success': False, 'message': '请选择要退的车票'}), 400
    
    # 使用装饰器包装的退票逻辑，支持死锁自动重试
    @Database.retry_on_deadlock(max_retries=3)
    def _do_refund_ticket():
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            conn.begin()
            
            # 验证所有车票都属于该用户
            placeholders = ','.join(['%s'] * len(ticket_ids))
            check_sql = f"""
                SELECT t.ticket_id, t.order_id, t.price, t.status
                FROM Ticket t
                JOIN `Order` o ON t.order_id = o.order_id
                WHERE t.ticket_id IN ({placeholders})
                AND o.user_id = %s
                FOR UPDATE
            """
            cursor.execute(check_sql, ticket_ids + [user_id])
            tickets = cursor.fetchall()
            
            if len(tickets) != len(ticket_ids):
                conn.rollback()
                raise Exception('部分车票不存在或无权退票')
            
            # 检查车票状态
            for ticket in tickets:
                if ticket['status'] != 'valid':
                    conn.rollback()
                    raise Exception('部分车票已退票或状态无效')
            
            # 退票
            refund_amount = 0
            for ticket in tickets:
                # 更新车票状态
                cursor.execute(
                    "UPDATE Ticket SET status = 'refunded' WHERE ticket_id = %s",
                    (ticket['ticket_id'],)
                )
                
                # 创建退票记录
                cursor.execute(
                    """INSERT INTO Refund (ticket_id, refund_time, refund_amount, refund_reason, handled_by)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (ticket['ticket_id'], datetime.now(), ticket['price'], refund_reason, user_id)
                )
                
                refund_amount += float(ticket['price'])
            
            # 更新订单状态
            if tickets:
                order_id = tickets[0]['order_id']
                cursor.execute(
                    "SELECT order_id FROM `Order` WHERE order_id = %s FOR UPDATE",
                    (order_id,)
                )
                cursor.execute(
                    """SELECT COUNT(*) as total, 
                       SUM(CASE WHEN status = 'refunded' THEN 1 ELSE 0 END) as refunded_count
                       FROM Ticket WHERE order_id = %s""",
                    (order_id,)
                )
                count_result = cursor.fetchone()
                
                if count_result['total'] == count_result['refunded_count']:
                    cursor.execute(
                        "UPDATE `Order` SET status = 'refunded' WHERE order_id = %s",
                        (order_id,)
                    )
            
            conn.commit()
            
            return {
                'success': True,
                'message': '退票成功',
                'refund_amount': refund_amount
            }
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    # 执行退票逻辑（带死锁重试）
    try:
        result = _do_refund_ticket()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'退票失败: {str(e)}'}), 500


@ticket_bp.route('/stations', methods=['GET'])
def get_stations():
    """获取所有车站列表"""
    try:
        stations = db.execute_query(
            """SELECT station_id, station_name, city, province, station_type, address
               FROM Station
               ORDER BY province, city, station_name"""
        )
        
        return jsonify({
            'success': True,
            'stations': stations
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败: {str(e)}'}), 500


@ticket_bp.route('/cities', methods=['GET'])
def get_cities():
    """获取所有城市列表"""
    try:
        cities = db.execute_query(
            """SELECT DISTINCT city, province
               FROM Station
               ORDER BY province, city"""
        )
        
        return jsonify({
            'success': True,
            'cities': cities
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败: {str(e)}'}), 500

