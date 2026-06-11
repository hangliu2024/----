"""
轻量级异步任务队列模块

用于处理耗时操作（如AI查询），避免阻塞主线程。
无需依赖Celery/Redis，使用Python内置threading实现。

使用示例:
    from app.task_queue import TaskQueue
    
    # 创建任务
    task_id = TaskQueue.submit(long_running_function, arg1, arg2)
    
    # 查询状态
    status = TaskQueue.get_status(task_id)
    
    # 获取结果
    result = TaskQueue.get_result(task_id)
"""

import threading
import uuid
import time
import logging
from collections import defaultdict
from typing import Any, Callable, Dict, Optional, Tuple
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"       # 等待执行
    RUNNING = "running"       # 正在执行
    COMPLETED = "completed"   # 已完成
    FAILED = "failed"         # 执行失败
    TIMEOUT = "timeout"       # 执行超时


class TaskResult:
    """任务结果对象"""
    
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.status = TaskStatus.PENDING
        self.result: Any = None
        self.error: Optional[str] = None
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.progress: int = 0  # 进度百分比 0-100
        
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'task_id': self.task_id,
            'status': self.status.value,
            'result': self.result,
            'error': self.error,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'progress': self.progress,
            'elapsed_time': self._get_elapsed_time()
        }
    
    def _get_elapsed_time(self) -> Optional[float]:
        """获取已用时间（秒）"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        elif self.started_at:
            return (datetime.now() - self.started_at).total_seconds()
        return None


class TaskQueue:
    """
    轻量级异步任务队列
    
    特点:
    1. 基于threading实现，无需额外依赖
    2. 支持任务状态跟踪
    3. 支持任务超时
    4. 自动清理过期任务
    """
    
    # 任务存储
    _tasks: Dict[str, TaskResult] = {}
    _lock = threading.Lock()
    
    # 配置
    MAX_TASKS = 1000          # 最大任务数
    TASK_TIMEOUT = 300        # 任务超时时间（秒）
    CLEANUP_INTERVAL = 60     # 清理间隔（秒）
    MAX_TASK_AGE = 3600       # 任务最大保留时间（秒）
    
    _last_cleanup = time.time()
    
    @classmethod
    def submit(cls, func: Callable, *args, timeout: int = None, **kwargs) -> str:
        """
        提交任务到队列
        
        Args:
            func: 要执行的函数
            *args: 函数参数
            timeout: 超时时间（秒）
            **kwargs: 函数关键字参数
            
        Returns:
            task_id: 任务ID
        """
        # 清理过期任务
        cls._cleanup_if_needed()
        
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 创建任务结果对象
        task_result = TaskResult(task_id)
        
        with cls._lock:
            # 检查任务数量限制
            if len(cls._tasks) >= cls.MAX_TASKS:
                # 移除最旧的任务
                oldest_id = min(cls._tasks.keys(), 
                              key=lambda x: cls._tasks[x].created_at)
                del cls._tasks[oldest_id]
            
            cls._tasks[task_id] = task_result
        
        # 启动工作线程
        thread = threading.Thread(
            target=cls._execute_task,
            args=(task_id, func, args, kwargs, timeout or cls.TASK_TIMEOUT),
            daemon=True
        )
        thread.start()
        
        logger.info(f"Task submitted: {task_id}")
        return task_id
    
    @classmethod
    def _execute_task(cls, task_id: str, func: Callable, 
                      args: Tuple, kwargs: Dict, timeout: int):
        """执行任务的工作线程"""
        with cls._lock:
            task = cls._tasks.get(task_id)
        if not task:
            return
        
        try:
            with cls._lock:
                task.status = TaskStatus.RUNNING
                task.started_at = datetime.now()
            
            # 执行任务（不持锁，避免死锁）
            result = func(*args, **kwargs)
            
            with cls._lock:
                task.status = TaskStatus.COMPLETED
                task.result = result
                task.completed_at = datetime.now()
                task.progress = 100
                
            logger.info(f"Task completed: {task_id}")
            
        except Exception as e:
            logger.error(f"Task failed: {task_id}, error: {str(e)}")
            with cls._lock:
                task.status = TaskStatus.FAILED
                task.error = str(e)
                task.completed_at = datetime.now()
    
    @classmethod
    def get_status(cls, task_id: str) -> Optional[Dict]:
        """
        获取任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务状态字典，如果任务不存在返回None
        """
        with cls._lock:
            task = cls._tasks.get(task_id)
            if task:
                return task.to_dict()
        return None
    
    @classmethod
    def get_result(cls, task_id: str, wait: bool = False, 
                   timeout: int = None) -> Tuple[Optional[Any], Optional[str]]:
        """
        获取任务结果
        
        Args:
            task_id: 任务ID
            wait: 是否等待任务完成
            timeout: 等待超时时间（秒）
            
        Returns:
            (result, error) 元组
        """
        if wait:
            cls._wait_for_task(task_id, timeout)
        
        with cls._lock:
            task = cls._tasks.get(task_id)
            if task:
                if task.status == TaskStatus.COMPLETED:
                    return task.result, None
                elif task.status == TaskStatus.FAILED:
                    return None, task.error
                else:
                    return None, f"Task is {task.status.value}"
        return None, "Task not found"
    
    @classmethod
    def _wait_for_task(cls, task_id: str, timeout: int = None) -> TaskStatus:
        """等待任务完成"""
        start_time = time.time()
        timeout = timeout or cls.TASK_TIMEOUT
        
        while True:
            with cls._lock:
                task = cls._tasks.get(task_id)
                if task and task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.TIMEOUT]:
                    return task.status
            
            if time.time() - start_time > timeout:
                return TaskStatus.TIMEOUT
            
            time.sleep(0.1)
    
    @classmethod
    def update_progress(cls, task_id: str, progress: int):
        """更新任务进度"""
        with cls._lock:
            task = cls._tasks.get(task_id)
            if task:
                task.progress = min(100, max(0, progress))
    
    @classmethod
    def cancel_task(cls, task_id: str) -> bool:
        """取消任务（仅对PENDING状态有效）"""
        with cls._lock:
            task = cls._tasks.get(task_id)
            if task and task.status == TaskStatus.PENDING:
                task.status = TaskStatus.FAILED
                task.error = "Task cancelled"
                return True
        return False
    
    @classmethod
    def _cleanup_if_needed(cls):
        """定期清理过期任务"""
        current_time = time.time()
        
        with cls._lock:
            if current_time - cls._last_cleanup < cls.CLEANUP_INTERVAL:
                return
            cls._last_cleanup = current_time
        
        with cls._lock:
            expired_ids = []
            for task_id, task in cls._tasks.items():
                age = (datetime.now() - task.created_at).total_seconds()
                if age > cls.MAX_TASK_AGE:
                    expired_ids.append(task_id)
            
            for task_id in expired_ids:
                del cls._tasks[task_id]
                
            if expired_ids:
                logger.info(f"Cleaned up {len(expired_ids)} expired tasks")
    
    @classmethod
    def get_queue_stats(cls) -> Dict:
        """获取队列统计信息"""
        with cls._lock:
            stats = {
                'total_tasks': len(cls._tasks),
                'by_status': defaultdict(int),
                'oldest_task': None,
                'newest_task': None
            }
            
            for task in cls._tasks.values():
                stats['by_status'][task.status.value] += 1
            
            if cls._tasks:
                oldest = min(cls._tasks.values(), key=lambda x: x.created_at)
                newest = max(cls._tasks.values(), key=lambda x: x.created_at)
                stats['oldest_task'] = oldest.created_at.isoformat()
                stats['newest_task'] = newest.created_at.isoformat()
            
            stats['by_status'] = dict(stats['by_status'])
            return stats
    
    @classmethod
    def clear_all(cls):
        """清空所有任务"""
        with cls._lock:
            cls._tasks.clear()
        logger.info("All tasks cleared")


# 便捷函数
def submit_task(func: Callable, *args, **kwargs) -> str:
    """提交任务的便捷函数"""
    return TaskQueue.submit(func, *args, **kwargs)


def get_task_status(task_id: str) -> Optional[Dict]:
    """获取任务状态的便捷函数"""
    return TaskQueue.get_status(task_id)


def get_task_result(task_id: str, wait: bool = False, timeout: int = None) -> Tuple[Optional[Any], Optional[str]]:
    """获取任务结果的便捷函数"""
    return TaskQueue.get_result(task_id, wait, timeout)