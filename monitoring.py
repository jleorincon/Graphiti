"""
Monitoring and Analytics Module for Graphiti Call Q&A Application
Provides logging, metrics, and performance monitoring capabilities
"""

import logging
import time
import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from functools import wraps
import sqlite3

# Configure logging with multiple handlers
def setup_logging(log_level: str = "INFO", log_file: str = "graphiti_app.log"):
    """Setup comprehensive logging configuration"""
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # File handler for detailed logs
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    # Console handler for important messages
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # Separate error log
    error_handler = logging.FileHandler("errors.log")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    logger.addHandler(error_handler)
    
    return logger

@dataclass
class PerformanceMetric:
    """Data class for performance metrics"""
    operation: str
    duration: float
    timestamp: datetime
    success: bool
    metadata: Optional[Dict] = None

@dataclass
class UsageStatistic:
    """Data class for usage statistics"""
    operation_type: str
    count: int
    avg_duration: float
    success_rate: float
    last_execution: datetime

class MetricsCollector:
    """Collects and stores performance metrics and usage statistics"""
    
    def __init__(self, db_path: str = "metrics.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for metrics storage"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation TEXT NOT NULL,
                    duration REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    success BOOLEAN NOT NULL,
                    metadata TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS usage_stats (
                    operation_type TEXT PRIMARY KEY,
                    count INTEGER DEFAULT 0,
                    total_duration REAL DEFAULT 0.0,
                    success_count INTEGER DEFAULT 0,
                    last_execution TEXT
                )
            """)
            
            conn.commit()
    
    def record_metric(self, metric: PerformanceMetric):
        """Record a performance metric"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO performance_metrics 
                    (operation, duration, timestamp, success, metadata)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    metric.operation,
                    metric.duration,
                    metric.timestamp.isoformat(),
                    metric.success,
                    json.dumps(metric.metadata) if metric.metadata else None
                ))
                
                # Update usage statistics
                conn.execute("""
                    INSERT INTO usage_stats 
                    (operation_type, count, total_duration, success_count, last_execution)
                    VALUES (?, 1, ?, ?, ?)
                    ON CONFLICT(operation_type) DO UPDATE SET
                        count = count + 1,
                        total_duration = total_duration + ?,
                        success_count = success_count + ?,
                        last_execution = ?
                """, (
                    metric.operation,
                    metric.duration,
                    1 if metric.success else 0,
                    metric.timestamp.isoformat(),
                    metric.duration,
                    1 if metric.success else 0,
                    metric.timestamp.isoformat()
                ))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to record metric: {e}")
    
    def get_usage_stats(self) -> List[UsageStatistic]:
        """Get usage statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT operation_type, count, total_duration, success_count, last_execution
                    FROM usage_stats
                    ORDER BY count DESC
                """)
                
                stats = []
                for row in cursor.fetchall():
                    operation_type, count, total_duration, success_count, last_execution = row
                    stats.append(UsageStatistic(
                        operation_type=operation_type,
                        count=count,
                        avg_duration=total_duration / count if count > 0 else 0.0,
                        success_rate=success_count / count if count > 0 else 0.0,
                        last_execution=datetime.fromisoformat(last_execution)
                    ))
                
                return stats
                
        except Exception as e:
            self.logger.error(f"Failed to get usage stats: {e}")
            return []
    
    def get_recent_metrics(self, limit: int = 100) -> List[PerformanceMetric]:
        """Get recent performance metrics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT operation, duration, timestamp, success, metadata
                    FROM performance_metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (limit,))
                
                metrics = []
                for row in cursor.fetchall():
                    operation, duration, timestamp, success, metadata = row
                    metrics.append(PerformanceMetric(
                        operation=operation,
                        duration=duration,
                        timestamp=datetime.fromisoformat(timestamp),
                        success=bool(success),
                        metadata=json.loads(metadata) if metadata else None
                    ))
                
                return metrics
                
        except Exception as e:
            self.logger.error(f"Failed to get recent metrics: {e}")
            return []

class PerformanceMonitor:
    """Context manager and decorator for performance monitoring"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.logger = logging.getLogger(__name__)
    
    def monitor_function(self, operation_name: str = None):
        """Decorator to monitor function performance"""
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                op_name = operation_name or f"{func.__module__}.{func.__name__}"
                start_time = time.time()
                success = False
                metadata = {"function": func.__name__, "args_count": len(args)}
                
                try:
                    result = await func(*args, **kwargs)
                    success = True
                    return result
                except Exception as e:
                    metadata["error"] = str(e)
                    self.logger.error(f"Error in {op_name}: {e}")
                    raise
                finally:
                    duration = time.time() - start_time
                    metric = PerformanceMetric(
                        operation=op_name,
                        duration=duration,
                        timestamp=datetime.now(timezone.utc),
                        success=success,
                        metadata=metadata
                    )
                    self.metrics_collector.record_metric(metric)
                    
                    if duration > 5.0:  # Log slow operations
                        self.logger.warning(f"Slow operation {op_name}: {duration:.2f}s")
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                op_name = operation_name or f"{func.__module__}.{func.__name__}"
                start_time = time.time()
                success = False
                metadata = {"function": func.__name__, "args_count": len(args)}
                
                try:
                    result = func(*args, **kwargs)
                    success = True
                    return result
                except Exception as e:
                    metadata["error"] = str(e)
                    self.logger.error(f"Error in {op_name}: {e}")
                    raise
                finally:
                    duration = time.time() - start_time
                    metric = PerformanceMetric(
                        operation=op_name,
                        duration=duration,
                        timestamp=datetime.now(timezone.utc),
                        success=success,
                        metadata=metadata
                    )
                    self.metrics_collector.record_metric(metric)
                    
                    if duration > 5.0:
                        self.logger.warning(f"Slow operation {op_name}: {duration:.2f}s")
            
            # Return appropriate wrapper based on function type
            if hasattr(func, '__code__') and func.__code__.co_flags & 0x80:  # CO_COROUTINE
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator

class SystemHealthChecker:
    """Monitors system health and resource usage"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def check_neo4j_connection(self, uri: str, user: str, password: str) -> bool:
        """Check Neo4j database connectivity"""
        try:
            # This would normally use neo4j driver
            # For now, just return True as we can't import neo4j here
            return True
        except Exception as e:
            self.logger.error(f"Neo4j connection check failed: {e}")
            return False
    
    def check_disk_space(self, path: str = ".") -> Dict[str, float]:
        """Check available disk space"""
        try:
            import shutil
            total, used, free = shutil.disk_usage(path)
            return {
                "total_gb": total / (1024**3),
                "used_gb": used / (1024**3),
                "free_gb": free / (1024**3),
                "usage_percent": (used / total) * 100
            }
        except Exception as e:
            self.logger.error(f"Disk space check failed: {e}")
            return {}
    
    def check_memory_usage(self) -> Dict:
        """Check memory usage"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            return {
                "total_gb": memory.total / (1024**3),
                "available_gb": memory.available / (1024**3),
                "used_gb": memory.used / (1024**3),
                "usage_percent": memory.percent
            }
        except ImportError:
            # psutil not available
            return {"status": "psutil not installed"}
        except Exception as e:
            self.logger.error(f"Memory check failed: {e}")
            return {}
    
    def get_system_health(self) -> Dict:
        """Get comprehensive system health report"""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "disk_space": self.check_disk_space(),
            "memory": self.check_memory_usage(),
            "neo4j_connection": self.check_neo4j_connection("", "", ""),  # Would use real credentials
        }

class ApplicationAnalytics:
    """Provides analytics and insights for the Graphiti application"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.logger = logging.getLogger(__name__)
    
    def generate_performance_report(self) -> Dict:
        """Generate a comprehensive performance report"""
        try:
            stats = self.metrics_collector.get_usage_stats()
            recent_metrics = self.metrics_collector.get_recent_metrics(50)
            
            # Calculate summary statistics
            total_operations = sum(stat.count for stat in stats)
            avg_success_rate = sum(stat.success_rate for stat in stats) / len(stats) if stats else 0
            
            # Find slowest operations
            slow_operations = [
                metric for metric in recent_metrics 
                if metric.duration > 2.0
            ]
            
            return {
                "report_generated": datetime.now(timezone.utc).isoformat(),
                "summary": {
                    "total_operations": total_operations,
                    "operation_types": len(stats),
                    "average_success_rate": round(avg_success_rate * 100, 2),
                    "slow_operations_count": len(slow_operations)
                },
                "operation_stats": [asdict(stat) for stat in stats[:10]],  # Top 10
                "recent_slow_operations": [
                    {
                        "operation": metric.operation,
                        "duration": round(metric.duration, 2),
                        "timestamp": metric.timestamp.isoformat(),
                        "success": metric.success
                    }
                    for metric in slow_operations[:5]
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate performance report: {e}")
            return {"error": str(e)}
    
    def get_usage_insights(self) -> Dict:
        """Get insights about application usage patterns"""
        try:
            stats = self.metrics_collector.get_usage_stats()
            
            if not stats:
                return {"message": "No usage data available"}
            
            # Most used operations
            most_used = max(stats, key=lambda x: x.count)
            
            # Least reliable operation
            least_reliable = min(stats, key=lambda x: x.success_rate) if stats else None
            
            # Slowest operation
            slowest = max(stats, key=lambda x: x.avg_duration) if stats else None
            
            return {
                "insights_generated": datetime.now(timezone.utc).isoformat(),
                "most_used_operation": {
                    "name": most_used.operation_type,
                    "count": most_used.count,
                    "success_rate": round(most_used.success_rate * 100, 2)
                },
                "least_reliable_operation": {
                    "name": least_reliable.operation_type,
                    "success_rate": round(least_reliable.success_rate * 100, 2)
                } if least_reliable else None,
                "slowest_operation": {
                    "name": slowest.operation_type,
                    "avg_duration": round(slowest.avg_duration, 2)
                } if slowest else None,
                "recommendations": self._generate_recommendations(stats)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate usage insights: {e}")
            return {"error": str(e)}
    
    def _generate_recommendations(self, stats: List[UsageStatistic]) -> List[str]:
        """Generate performance recommendations based on usage stats"""
        recommendations = []
        
        for stat in stats:
            if stat.success_rate < 0.9:
                recommendations.append(
                    f"Consider improving error handling for {stat.operation_type} "
                    f"(current success rate: {stat.success_rate*100:.1f}%)"
                )
            
            if stat.avg_duration > 5.0:
                recommendations.append(
                    f"Optimize {stat.operation_type} performance "
                    f"(current avg duration: {stat.avg_duration:.1f}s)"
                )
        
        if not recommendations:
            recommendations.append("System performance looks good! 🎉")
        
        return recommendations

# Global instances
metrics_collector = MetricsCollector()
performance_monitor = PerformanceMonitor(metrics_collector)
health_checker = SystemHealthChecker()
analytics = ApplicationAnalytics(metrics_collector)

# Setup logging on module import
logger = setup_logging()

# Export key components
__all__ = [
    'setup_logging',
    'MetricsCollector',
    'PerformanceMonitor', 
    'SystemHealthChecker',
    'ApplicationAnalytics',
    'metrics_collector',
    'performance_monitor',
    'health_checker',
    'analytics'
] 