# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify, session
from datetime import datetime
from app.database import db, Database
import io
import csv

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


def require_admin(f):
    """管理员权限装饰器"""
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        if not session.get('is_admin', False):
            return jsonify({'success': False, 'message': '需要管理员权限'}), 403
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper


def log_admin_operation(operation_type, operation_desc, target_table=None, target_id=None):
    """记录管理员操作日志"""
    try:
        db.execute_insert(
            """INSERT INTO Admin_Log (user_id, operation_type, operation_desc, target_table, target_id, ip_address)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (session.get('user_id'), operation_type, operation_desc, target_table, target_id, request.remote_addr)
        )
    except Exception:
        pass  # 日志失败不影响主流程


# ==================== 车站管理 ====================

@admin_bp.route('/station/add', methods=['POST'])
@require_admin
def add_station():
    """添加车站"""
    data = request.get_json()
    
    required_fields = ['station_name', 'city', 'province', 'station_type']
    if not all(field in data for field in required_fields):
        return jsonify({'success': False, 'message': '缺少必填字段'}), 400
    
    try:
        station_id = db.execute_insert(
            """INSERT INTO Station (station_name, city, province, station_type, address)
               VALUES (%s, %s, %s, %s, %s)""",
            (data['station_name'], data['city'], data['province'], 
             data['station_type'], data.get('address', ''))
        )
        
        log_admin_operation('ADD_STATION', f"添加车站: {data['station_name']}", 'Station', station_id)
        
        return jsonify({
            'success': True,
            'message': '车站添加成功',
            'station_id': station_id
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'}), 500


@admin_bp.route('/station/<int:station_id>', methods=['DELETE'])
@require_admin
def delete_station(station_id):
    """删除车站"""
    try:
        # 检查是否有线路使用该车站
        routes = db.execute_query(
            """SELECT route_id FROM Route 
               WHERE start_station_id = %s OR end_station_id = %s""",
            (station_id, station_id)
        )
        
        if routes:
            return jsonify({'success': False, 'message': '该车站正在被线路使用，无法删除'}), 400
        
        affected = db.execute_update(
            "DELETE FROM Station WHERE station_id = %s",
            (station_id,)
        )
        
        if affected > 0:
            log_admin_operation('DELETE_STATION', f"删除车站ID: {station_id}", 'Station', station_id)
            return jsonify({'success': True, 'message': '车站删除成功'}), 200
        else:
            return jsonify({'success': False, 'message': '车站不存在'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500


# ==================== 城市管理 ====================

@admin_bp.route('/city/add', methods=['POST'])
@require_admin
def add_city():
    """添加城市（实际是添加该城市的第一个车站）"""
    data = request.get_json()
    
    required_fields = ['city', 'province', 'station_name', 'station_type']
    if not all(field in data for field in required_fields):
        return jsonify({'success': False, 'message': '缺少必填字段'}), 400
    
    try:
        station_id = db.execute_insert(
            """INSERT INTO Station (station_name, city, province, station_type, address)
               VALUES (%s, %s, %s, %s, %s)""",
            (data['station_name'], data['city'], data['province'], 
             data['station_type'], data.get('address', ''))
        )
        
        log_admin_operation('ADD_CITY', f"添加城市: {data['province']}-{data['city']}", 'Station', station_id)
        
        return jsonify({
            'success': True,
            'message': '城市添加成功',
            'station_id': station_id
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'}), 500


# ==================== 车次管理 ====================

@admin_bp.route('/schedule/add', methods=['POST'])
@require_admin
def add_schedule():
    """添加车次"""
    data = request.get_json()
    
    required_fields = ['schedule_no', 'route_id', 'vehicle_id', 'departure_date', 
                      'departure_time', 'arrival_date', 'arrival_time', 'base_price']
    if not all(field in data for field in required_fields):
        return jsonify({'success': False, 'message': '缺少必填字段'}), 400
    
    # 验证票价
    try:
        base_price = float(data['base_price'])
        if base_price < 0:
            return jsonify({'success': False, 'message': '票价不能为负数'}), 400
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': '票价格式不正确'}), 400
    
    # 验证时间：到达时间必须晚于发车时间
    try:
        departure_datetime = datetime.strptime(
            f"{data['departure_date']} {data['departure_time']}", 
            '%Y-%m-%d %H:%M:%S' if ':' in data['departure_time'] and len(data['departure_time']) > 5 else '%Y-%m-%d %H:%M'
        )
        arrival_datetime = datetime.strptime(
            f"{data['arrival_date']} {data['arrival_time']}", 
            '%Y-%m-%d %H:%M:%S' if ':' in data['arrival_time'] and len(data['arrival_time']) > 5 else '%Y-%m-%d %H:%M'
        )
        
        if arrival_datetime <= departure_datetime:
            return jsonify({'success': False, 'message': '到达时间必须晚于发车时间'}), 400
    except ValueError as e:
        return jsonify({'success': False, 'message': f'日期时间格式不正确: {str(e)}'}), 400
    
    try:
        schedule_id = db.execute_insert(
            """INSERT INTO Schedule (schedule_no, route_id, vehicle_id, departure_date, 
                                     departure_time, arrival_date, arrival_time, base_price, status, delay_minutes)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (data['schedule_no'], data['route_id'], data['vehicle_id'], 
             data['departure_date'], data['departure_time'], data['arrival_date'], data['arrival_time'],
             data['base_price'], data.get('status', 'normal'), data.get('delay_minutes', 0))
        )
        
        log_admin_operation('ADD_SCHEDULE', f"添加班次: {data['schedule_no']}", 'Schedule', schedule_id)
        
        return jsonify({
            'success': True,
            'message': '班次添加成功',
            'schedule_id': schedule_id
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'}), 500


@admin_bp.route('/schedule/<int:schedule_id>', methods=['PUT'])
@require_admin
def update_schedule(schedule_id):
    """更新车次信息"""
    data = request.get_json()
    
    # 构建更新SQL
    update_fields = []
    params = []
    
    allowed_fields = ['departure_time', 'arrival_time', 'base_price', 'status', 'delay_minutes']
    for field in allowed_fields:
        if field in data:
            update_fields.append(f"{field} = %s")
            params.append(data[field])
    
    if not update_fields:
        return jsonify({'success': False, 'message': '没有要更新的字段'}), 400
    
    params.append(schedule_id)
    sql = f"UPDATE Schedule SET {', '.join(update_fields)} WHERE schedule_id = %s"
    
    try:
        affected = db.execute_update(sql, params)
        
        if affected > 0:
            log_admin_operation('UPDATE_SCHEDULE', f"更新班次ID: {schedule_id}", 'Schedule', schedule_id)
            return jsonify({'success': True, 'message': '班次更新成功'}), 200
        else:
            return jsonify({'success': False, 'message': '班次不存在'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500


@admin_bp.route('/schedule/<int:schedule_id>', methods=['DELETE'])
@require_admin
def delete_schedule(schedule_id):
    """删除车次"""
    try:
        # 检查是否有订单
        orders = db.execute_query(
            "SELECT order_id FROM `Order` WHERE schedule_id = %s",
            (schedule_id,)
        )
        
        if orders:
            return jsonify({'success': False, 'message': '该班次已有订单，无法删除'}), 400
        
        affected = db.execute_update(
            "DELETE FROM Schedule WHERE schedule_id = %s",
            (schedule_id,)
        )
        
        if affected > 0:
            log_admin_operation('DELETE_SCHEDULE', f"删除班次ID: {schedule_id}", 'Schedule', schedule_id)
            return jsonify({'success': True, 'message': '班次删除成功'}), 200
        else:
            return jsonify({'success': False, 'message': '班次不存在'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500


@admin_bp.route('/schedule/batch_update_price', methods=['POST'])
@require_admin
def batch_update_price():
    """批量更新票价（同一起始站到终点站的线路）"""
    data = request.get_json()
    
    start_station_id = data.get('start_station_id')
    end_station_id = data.get('end_station_id')
    new_price = data.get('new_price')
    
    if not all([start_station_id, end_station_id, new_price]):
        return jsonify({'success': False, 'message': '缺少必填字段'}), 400
    
    try:
        # 更新符合条件的所有班次票价
        affected = db.execute_update(
            """UPDATE Schedule s
               JOIN Route r ON s.route_id = r.route_id
               SET s.base_price = %s
               WHERE r.start_station_id = %s AND r.end_station_id = %s""",
            (new_price, start_station_id, end_station_id)
        )
        
        log_admin_operation(
            'BATCH_UPDATE_PRICE', 
            f"批量更新票价: 站点{start_station_id}→{end_station_id}, 新价格{new_price}, 影响{affected}条记录",
            'Schedule'
        )
        
        return jsonify({
            'success': True,
            'message': f'成功更新{affected}条班次的票价'
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500


# ==================== 线路管理 ====================

@admin_bp.route('/route/add', methods=['POST'])
@require_admin
def add_route():
    """添加线路"""
    data = request.get_json()
    
    required_fields = ['route_name', 'start_station_id', 'end_station_id', 'route_type']
    if not all(field in data for field in required_fields):
        return jsonify({'success': False, 'message': '缺少必填字段'}), 400
    
    try:
        route_id = db.execute_insert(
            """INSERT INTO Route (route_name, start_station_id, end_station_id, route_type, total_distance)
               VALUES (%s, %s, %s, %s, %s)""",
            (data['route_name'], data['start_station_id'], data['end_station_id'],
             data['route_type'], data.get('total_distance', 0))
        )
        
        log_admin_operation('ADD_ROUTE', f"添加线路: {data['route_name']}", 'Route', route_id)
        
        return jsonify({
            'success': True,
            'message': '线路添加成功',
            'route_id': route_id
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'}), 500


@admin_bp.route('/route/<int:route_id>', methods=['DELETE'])
@require_admin
def delete_route(route_id):
    """删除线路"""
    try:
        # 检查是否有班次使用该线路
        schedules = db.execute_query(
            "SELECT schedule_id FROM Schedule WHERE route_id = %s",
            (route_id,)
        )
        
        if schedules:
            return jsonify({'success': False, 'message': '该线路正在被班次使用，无法删除'}), 400
        
        affected = db.execute_update(
            "DELETE FROM Route WHERE route_id = %s",
            (route_id,)
        )
        
        if affected > 0:
            log_admin_operation('DELETE_ROUTE', f"删除线路ID: {route_id}", 'Route', route_id)
            return jsonify({'success': True, 'message': '线路删除成功'}), 200
        else:
            return jsonify({'success': False, 'message': '线路不存在'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500


# ==================== 报表系统 ====================

@admin_bp.route('/report/sales', methods=['GET'])
@require_admin
def get_sales_report():
    """销售报表"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    sql = """
        SELECT 
            DATE(o.order_time) as order_date,
            COUNT(DISTINCT CASE WHEN o.status = 'confirmed' THEN o.order_id END) as order_count,
            COUNT(DISTINCT CASE WHEN o.status = 'refunded' THEN o.order_id END) as refunded_count,
            SUM(CASE WHEN o.status = 'confirmed' THEN o.ticket_count ELSE 0 END) as ticket_count,
            SUM(CASE WHEN o.status = 'confirmed' THEN o.total_amount ELSE 0 END) as total_sales,
            SUM(CASE WHEN o.status = 'refunded' THEN o.total_amount ELSE 0 END) as refunded_amount,
            COUNT(DISTINCT CASE WHEN o.order_type = 'group' AND o.status = 'confirmed' THEN o.order_id END) as group_order_count
        FROM `Order` o
        WHERE o.status IN ('confirmed', 'refunded')
    """
    
    params = []
    if start_date:
        sql += " AND o.order_time >= %s"
        params.append(start_date)
    if end_date:
        sql += " AND o.order_time <= %s"
        params.append(end_date + ' 23:59:59')
    
    sql += " GROUP BY DATE(o.order_time) ORDER BY order_date DESC"
    
    try:
        results = db.execute_query(sql, params)
        
        for result in results:
            if result['order_date']:
                result['order_date'] = result['order_date'].strftime('%Y-%m-%d')
            result['total_sales'] = float(result['total_sales'] or 0)
            result['refunded_amount'] = float(result['refunded_amount'] or 0)
            # 计算实际收入（销售额 - 退款额）
            result['net_revenue'] = result['total_sales']
        
        return jsonify({
            'success': True,
            'report': results
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败: {str(e)}'}), 500


@admin_bp.route('/report/schedule', methods=['GET'])
@require_admin
def get_schedule_report():
    """班次统计报表"""
    try:
        sql = """
            SELECT 
                s.schedule_no,
                r.route_name,
                COUNT(DISTINCT s.schedule_id) as total_schedules,
                SUM(CASE WHEN s.status = 'normal' THEN 1 ELSE 0 END) as normal_count,
                SUM(CASE WHEN s.status = 'delayed' THEN 1 ELSE 0 END) as delayed_count,
                SUM(CASE WHEN s.status = 'cancelled' THEN 1 ELSE 0 END) as cancelled_count,
                COUNT(DISTINCT CASE WHEN o.status = 'confirmed' THEN o.order_id END) as order_count,
                COUNT(DISTINCT CASE WHEN o.status = 'refunded' THEN o.order_id END) as refunded_order_count,
                COALESCE(SUM(CASE WHEN o.status = 'confirmed' THEN o.total_amount ELSE 0 END), 0) as total_revenue
            FROM Schedule s
            JOIN Route r ON s.route_id = r.route_id
            LEFT JOIN `Order` o ON s.schedule_id = o.schedule_id
            GROUP BY s.schedule_no, r.route_name
            ORDER BY total_revenue DESC
        """
        
        results = db.execute_query(sql)
        
        for result in results:
            result['total_revenue'] = float(result['total_revenue'] or 0)
        
        return jsonify({
            'success': True,
            'report': results
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败: {str(e)}'}), 500


@admin_bp.route('/report/refund', methods=['GET'])
@require_admin
def get_refund_report():
    """退票统计报表"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    sql = """
        SELECT 
            DATE(r.refund_time) as refund_date,
            COUNT(r.refund_id) as refund_count,
            SUM(r.refund_amount) as total_refund_amount
        FROM Refund r
        WHERE 1=1
    """
    
    params = []
    if start_date:
        sql += " AND r.refund_time >= %s"
        params.append(start_date)
    if end_date:
        sql += " AND r.refund_time <= %s"
        params.append(end_date + ' 23:59:59')
    
    sql += " GROUP BY DATE(r.refund_time) ORDER BY refund_date DESC"
    
    try:
        results = db.execute_query(sql, params)
        
        for result in results:
            if result['refund_date']:
                result['refund_date'] = result['refund_date'].strftime('%Y-%m-%d')
            result['total_refund_amount'] = float(result['total_refund_amount'] or 0)
        
        return jsonify({
            'success': True,
            'report': results
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败: {str(e)}'}), 500


@admin_bp.route('/report/export', methods=['GET'])
@require_admin
def export_report():
    """导出综合报表为CSV"""
    try:
        # 获取综合数据
        sql = """
            SELECT 
                o.order_id,
                u.username,
                u.real_name,
                s.schedule_no,
                r.route_name,
                st_start.station_name AS start_station,
                st_end.station_name AS end_station,
                s.departure_date,
                s.departure_time,
                o.order_time,
                o.ticket_count,
                o.total_amount,
                o.order_type,
                o.status
            FROM `Order` o
            JOIN User u ON o.user_id = u.user_id
            JOIN Schedule s ON o.schedule_id = s.schedule_id
            JOIN Route r ON s.route_id = r.route_id
            JOIN Station st_start ON r.start_station_id = st_start.station_id
            JOIN Station st_end ON r.end_station_id = st_end.station_id
            ORDER BY o.order_time DESC
            LIMIT 1000
        """
        
        results = db.execute_query(sql)
        
        # 格式化时间
        for result in results:
            if result['order_time']:
                result['order_time'] = result['order_time'].strftime('%Y-%m-%d %H:%M:%S')
            if result['departure_date']:
                result['departure_date'] = result['departure_date'].strftime('%Y-%m-%d')
            if result['departure_time']:
                result['departure_time'] = str(result['departure_time'])
        
        log_admin_operation('EXPORT_REPORT', f"导出报表，共{len(results)}条记录")
        
        return jsonify({
            'success': True,
            'data': results
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'导出失败: {str(e)}'}), 500


@admin_bp.route('/logs', methods=['GET'])
@require_admin
def get_admin_logs():
    """获取管理员操作日志"""
    limit = request.args.get('limit', 100, type=int)
    
    try:
        logs = db.execute_query(
            """SELECT 
                l.log_id,
                l.operation_type,
                l.operation_desc,
                l.target_table,
                l.target_id,
                l.operation_time,
                l.ip_address,
                u.username
            FROM Admin_Log l
            LEFT JOIN User u ON l.user_id = u.user_id
            ORDER BY l.operation_time DESC
            LIMIT %s""",
            (limit,)
        )
        
        for log in logs:
            if log['operation_time']:
                log['operation_time'] = log['operation_time'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({
            'success': True,
            'logs': logs
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败: {str(e)}'}), 500


# ==================== 车辆管理 ====================

@admin_bp.route('/vehicles', methods=['GET'])
@require_admin
def get_vehicles():
    """获取所有车辆"""
    try:
        vehicles = db.execute_query(
            "SELECT * FROM Vehicle ORDER BY vehicle_id"
        )
        
        return jsonify({
            'success': True,
            'vehicles': vehicles
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败: {str(e)}'}), 500


@admin_bp.route('/routes', methods=['GET'])
@require_admin
def get_routes():
    """获取所有线路"""
    try:
        routes = db.execute_query(
            """SELECT 
                r.*,
                st_start.station_name AS start_station_name,
                st_end.station_name AS end_station_name
            FROM Route r
            JOIN Station st_start ON r.start_station_id = st_start.station_id
            JOIN Station st_end ON r.end_station_id = st_end.station_id
            ORDER BY r.route_id"""
        )
        
        return jsonify({
            'success': True,
            'routes': routes
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败: {str(e)}'}), 500


@admin_bp.route('/schedules', methods=['GET'])
@require_admin
def get_all_schedules():
    """获取所有班次"""
    try:
        schedules = db.execute_query(
            """SELECT 
                s.*,
                r.route_name,
                v.vehicle_no
            FROM Schedule s
            JOIN Route r ON s.route_id = r.route_id
            JOIN Vehicle v ON s.vehicle_id = v.vehicle_id
            ORDER BY s.departure_date DESC, s.departure_time
            LIMIT 200"""
        )
        
        for schedule in schedules:
            if schedule.get('departure_date'):
                schedule['departure_date'] = schedule['departure_date'].strftime('%Y-%m-%d')
            if schedule.get('arrival_date'):
                schedule['arrival_date'] = schedule['arrival_date'].strftime('%Y-%m-%d')
            if schedule.get('departure_time'):
                schedule['departure_time'] = str(schedule['departure_time'])
            if schedule.get('arrival_time'):
                schedule['arrival_time'] = str(schedule['arrival_time'])
        
        return jsonify({
            'success': True,
            'schedules': schedules
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败: {str(e)}'}), 500


# ==================== 系统监控 ====================

@admin_bp.route('/pool/status', methods=['GET'])
@require_admin
def get_pool_status():
    """获取数据库连接池状态"""
    try:
        status = Database.get_pool_status()
        return jsonify({
            'success': True,
            'pool_status': status
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取连接池状态失败: {str(e)}'}), 500

