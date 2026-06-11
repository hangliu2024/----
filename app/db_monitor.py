"""
数据库连接池监控模块

提供连接池状态监控、健康检查、性能统计等功能。

使用示例:
    from app.db_monitor import DBMonitor
    
    # 获取连接池状态
    status = DBMonitor.get_pool_status()
    
    # 执行健康检查
    health = DBMonitor.health_check()
    
    # 获取性能统计
    stats = DBMonitor.get_performance_stats()
"""

import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class DBMonitor:
    """
    数据库连接池监控器
    
    功能:
    1. 连接池状态监控
    2. 查询性能统计
    3. 健康检查
    4. 慢查询检测
    """
    
    # 性能统计存储
    _query_stats: Dict[str, List[float]] = defaultdict(list)
    _slow_queries: List[Dict] = []
    _lock = threading.Lock()
    
    # 配置
    SLOW_QUERY_THRESHOLD = 1.0      # 慢查询阈值（秒）
    MAX_SLOW_QUERIES = 100          # 最大保存慢查询数
    MAX_STATS_PER_QUERY = 1000      # 每个查询保留的最大统计数
    STATS_RETENTION_HOURS = 24      # 统计保留时间（小时）
    
    @classmethod
    def get_pool_status(cls) -> Dict:
        """
        获取连接池状态
        
        Returns:
            连接池状态字典
        """
        try:
            from app import db
            from sqlalchemy import inspect
            
            engine = db.engine
            pool = engine.pool
            
            status = {
                'pool_size': pool.size(),
                'checked_in_connections': pool.checkedin(),
                'checked_out_connections': pool.checkedout(),
                'overflow_connections': pool.overflow(),
                'total_connections': pool.size() + pool.overflow(),
                'invalid_connections': pool.invalidatedcount() if hasattr(pool, 'invalidatedcount') else 0,
                'pool_status': 'healthy'
            }
            
            # 计算连接池使用率
            max_connections = getattr(pool, '_max_overflow', 10) + getattr(pool, '_pool_size', 20)
            usage_percent = (status['total_connections'] / max_connections) * 100 if max_connections > 0 else 0
            status['usage_percent'] = round(usage_percent, 2)
            
            # 判断状态
            if usage_percent > 80:
                status['pool_status'] = 'warning'
            elif usage_percent > 95:
                status['pool_status'] = 'critical'
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get pool status: {e}")
            return {
                'error': str(e),
                'pool_status': 'error'
            }
    
    @classmethod
    def health_check(cls) -> Dict:
        """
        执行数据库健康检查
        
        Returns:
            健康检查结果
        """
        result = {
            'timestamp': datetime.now().isoformat(),
            'status': 'healthy',
            'checks': {}
        }
        
        try:
            from app import db
            from sqlalchemy import text
            
            # 1. 连接检查
            start_time = time.time()
            with db.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            latency = time.time() - start_time
            result['checks']['connection'] = {
                'status': 'ok',
                'latency_ms': round(latency * 1000, 2)
            }
            
            # 2. 连接池检查
            pool_status = cls.get_pool_status()
            result['checks']['pool'] = {
                'status': pool_status.get('pool_status', 'unknown'),
                'details': pool_status
            }
            
            # 3. 查询性能检查
            start_time = time.time()
            with db.engine.connect() as conn:
                conn.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE()"))
            query_latency = time.time() - start_time
            result['checks']['query_performance'] = {
                'status': 'ok' if query_latency < 1.0 else 'slow',
                'latency_ms': round(query_latency * 1000, 2)
            }
            
            # 综合判断
            if pool_status.get('pool_status') in ['warning', 'critical', 'error']:
                result['status'] = 'degraded'
            if query_latency > 2.0:
                result['status'] = 'degraded'
                
        except Exception as e:
            result['status'] = 'unhealthy'
            result['error'] = str(e)
            logger.error(f"Health check failed: {e}")
        
        return result
    
    @classmethod
    def record_query(cls, query: str, duration: float, params: Dict = None):
        """
        记录查询执行情况
        
        Args:
            query: SQL查询语句
            duration: 执行时间（秒）
            params: 查询参数
        """
        # 简化查询（去除多余空白）
        simplified_query = ' '.join(query.split())
        
        with cls._lock:
            # 记录统计
            cls._query_stats[simplified_query].append(duration)
            
            # 限制统计数量
            if len(cls._query_stats[simplified_query]) > cls.MAX_STATS_PER_QUERY:
                cls._query_stats[simplified_query] = cls._query_stats[simplified_query][-cls.MAX_STATS_PER_QUERY:]
            
            # 记录慢查询
            if duration > cls.SLOW_QUERY_THRESHOLD:
                cls._slow_queries.append({
                    'query': simplified_query[:500],  # 限制长度
                    'duration': duration,
                    'timestamp': datetime.now().isoformat(),
                    'params': params
                })
                
                # 限制慢查询数量
                if len(cls._slow_queries) > cls.MAX_SLOW_QUERIES:
                    cls._slow_queries = cls._slow_queries[-cls.MAX_SLOW_QUERIES:]
    
    @classmethod
    def get_performance_stats(cls) -> Dict:
        """
        获取查询性能统计
        
        Returns:
            性能统计字典
        """
        stats = {
            'total_queries': 0,
            'unique_queries': 0,
            'avg_duration': 0,
            'slow_query_count': 0,
            'top_slow_queries': [],
            'query_details': []
        }
        
        with cls._lock:
            if not cls._query_stats:
                return stats
            
            total_duration = 0
            total_count = 0
            
            for query, durations in cls._query_stats.items():
                count = len(durations)
                avg = sum(durations) / count if count > 0 else 0
                min_dur = min(durations) if durations else 0
                max_dur = max(durations) if durations else 0
                
                total_duration += sum(durations)
                total_count += count
                
                stats['query_details'].append({
                    'query': query[:200],
                    'count': count,
                    'avg_ms': round(avg * 1000, 2),
                    'min_ms': round(min_dur * 1000, 2),
                    'max_ms': round(max_dur * 1000, 2)
                })
            
            stats['total_queries'] = total_count
            stats['unique_queries'] = len(cls._query_stats)
            stats['avg_duration'] = round(total_duration / total_count * 1000, 2) if total_count > 0 else 0
            stats['slow_query_count'] = len(cls._slow_queries)
            
            # 获取最慢的查询
            sorted_queries = sorted(stats['query_details'], 
                                   key=lambda x: x['avg_ms'], reverse=True)
            stats['top_slow_queries'] = sorted_queries[:10]
        
        return stats
    
    @classmethod
    def get_slow_queries(cls, limit: int = 20) -> List[Dict]:
        """
        获取慢查询列表
        
        Args:
            limit: 返回数量限制
            
        Returns:
            慢查询列表
        """
        with cls._lock:
            return sorted(cls._slow_queries, 
                         key=lambda x: x['duration'], 
                         reverse=True)[:limit]
    
    @classmethod
    def clear_stats(cls):
        """清空统计数据"""
        with cls._lock:
            cls._query_stats.clear()
            cls._slow_queries.clear()
        logger.info("Database stats cleared")
    
    @classmethod
    @contextmanager
    def track_query(cls, query: str, params: Dict = None):
        """
        跟踪查询执行的上下文管理器
        
        用法:
            with DBMonitor.track_query("SELECT * FROM users"):
                # 执行查询
                pass
        """
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            cls.record_query(query, duration, params)
    
    @classmethod
    def get_monitoring_dashboard_data(cls) -> Dict:
        """
        获取监控仪表盘所需的所有数据
        
        Returns:
            包含所有监控数据的字典
        """
        return {
            'pool_status': cls.get_pool_status(),
            'health_check': cls.health_check(),
            'performance_stats': cls.get_performance_stats(),
            'slow_queries': cls.get_slow_queries(10),
            'timestamp': datetime.now().isoformat()
        }


# 查询追踪装饰器
def track_db_query(func):
    """
    数据库查询追踪装饰器
    
    用法:
        @track_db_query
        def get_users():
            return User.query.all()
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            DBMonitor.record_query(
                query=f"Function: {func.__name__}",
                duration=duration
            )
            return result
        except Exception as e:
            duration = time.time() - start_time
            DBMonitor.record_query(
                query=f"Function: {func.__name__} (ERROR)",
                duration=duration
            )
            raise
    return wrapper


# Flask路由集成
def init_db_monitor_routes(app):
    """
    初始化数据库监控路由
    
    Args:
        app: Flask应用实例
    """
    from flask import jsonify
    
    @app.route('/api/db/status')
    def db_pool_status():
        """获取连接池状态API"""
        return jsonify(DBMonitor.get_pool_status())
    
    @app.route('/api/db/health')
    def db_health_check():
        """健康检查API"""
        return jsonify(DBMonitor.health_check())
    
    @app.route('/api/db/stats')
    def db_performance_stats():
        """性能统计API"""
        return jsonify(DBMonitor.get_performance_stats())
    
    @app.route('/api/db/slow-queries')
    def db_slow_queries():
        """慢查询API"""
        return jsonify(DBMonitor.get_slow_queries())
    
    @app.route('/api/db/dashboard')
    def db_dashboard():
        """监控仪表盘数据API"""
        return jsonify(DBMonitor.get_monitoring_dashboard_data())
    
    logger.info("Database monitoring routes initialized")