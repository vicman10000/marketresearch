"""
Health check system for monitoring service dependencies

Provides health checks for database, API, disk space, and memory.
"""
import os
import psutil
import time
from typing import Dict, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import requests


@dataclass
class HealthStatus:
    """Health check status"""
    service: str
    status: str  # 'healthy', 'degraded', 'unhealthy'
    timestamp: datetime
    latency_ms: Optional[float] = None
    message: Optional[str] = None
    details: Optional[Dict] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class HealthCheck:
    """Health check manager"""
    
    def __init__(self):
        self.checks = {}
    
    def check_database(self, database_url: str = None) -> HealthStatus:
        """
        Check database connectivity
        
        Args:
            database_url: Database connection string
            
        Returns:
            HealthStatus object
        """
        start = time.time()
        
        try:
            from .database import get_database
            
            if database_url is None:
                try:
                    from .config_settings import get_settings
                    settings = get_settings()
                    database_url = settings.database_url
                except ImportError:
                    database_url = "sqlite:///./data/market_viz.db"
            
            db = get_database(database_url)
            
            # Try a simple query
            with db.get_session() as session:
                session.execute("SELECT 1")
            
            latency = (time.time() - start) * 1000
            
            return HealthStatus(
                service='database',
                status='healthy',
                timestamp=datetime.now(),
                latency_ms=round(latency, 2),
                message='Database connection successful'
            )
        except Exception as e:
            latency = (time.time() - start) * 1000
            return HealthStatus(
                service='database',
                status='unhealthy',
                timestamp=datetime.now(),
                latency_ms=round(latency, 2),
                message=f'Database check failed: {str(e)}'
            )
    
    def check_api(self, url: str = 'https://finance.yahoo.com', timeout: int = 5) -> HealthStatus:
        """
        Check external API availability
        
        Args:
            url: API URL to check
            timeout: Request timeout in seconds
            
        Returns:
            HealthStatus object
        """
        start = time.time()
        
        try:
            response = requests.head(url, timeout=timeout, allow_redirects=True)
            latency = (time.time() - start) * 1000
            
            if response.status_code < 500:
                status = 'healthy'
                message = f'API accessible (status {response.status_code})'
            else:
                status = 'degraded'
                message = f'API returned {response.status_code}'
            
            return HealthStatus(
                service='api',
                status=status,
                timestamp=datetime.now(),
                latency_ms=round(latency, 2),
                message=message,
                details={'status_code': response.status_code}
            )
        except requests.Timeout:
            latency = (time.time() - start) * 1000
            return HealthStatus(
                service='api',
                status='degraded',
                timestamp=datetime.now(),
                latency_ms=round(latency, 2),
                message='API request timed out'
            )
        except Exception as e:
            latency = (time.time() - start) * 1000
            return HealthStatus(
                service='api',
                status='unhealthy',
                timestamp=datetime.now(),
                latency_ms=round(latency, 2),
                message=f'API check failed: {str(e)}'
            )
    
    def check_disk_space(self, path: str = '.', min_free_gb: float = 1.0) -> HealthStatus:
        """
        Check available disk space
        
        Args:
            path: Path to check
            min_free_gb: Minimum free space in GB
            
        Returns:
            HealthStatus object
        """
        try:
            stat = psutil.disk_usage(path)
            free_gb = stat.free / (1024 ** 3)
            used_percent = stat.percent
            
            if free_gb < min_free_gb:
                status = 'unhealthy'
                message = f'Low disk space: {free_gb:.2f} GB free'
            elif used_percent > 90:
                status = 'degraded'
                message = f'Disk usage high: {used_percent}%'
            else:
                status = 'healthy'
                message = f'Sufficient disk space: {free_gb:.2f} GB free'
            
            return HealthStatus(
                service='disk',
                status=status,
                timestamp=datetime.now(),
                message=message,
                details={
                    'free_gb': round(free_gb, 2),
                    'used_percent': used_percent,
                    'total_gb': round(stat.total / (1024 ** 3), 2)
                }
            )
        except Exception as e:
            return HealthStatus(
                service='disk',
                status='unhealthy',
                timestamp=datetime.now(),
                message=f'Disk check failed: {str(e)}'
            )
    
    def check_memory(self, max_usage_percent: float = 90) -> HealthStatus:
        """
        Check memory usage
        
        Args:
            max_usage_percent: Maximum acceptable memory usage percentage
            
        Returns:
            HealthStatus object
        """
        try:
            memory = psutil.virtual_memory()
            used_gb = memory.used / (1024 ** 3)
            total_gb = memory.total / (1024 ** 3)
            percent = memory.percent
            
            if percent > max_usage_percent:
                status = 'unhealthy'
                message = f'High memory usage: {percent}%'
            elif percent > 80:
                status = 'degraded'
                message = f'Memory usage elevated: {percent}%'
            else:
                status = 'healthy'
                message = f'Memory usage normal: {percent}%'
            
            return HealthStatus(
                service='memory',
                status=status,
                timestamp=datetime.now(),
                message=message,
                details={
                    'used_gb': round(used_gb, 2),
                    'total_gb': round(total_gb, 2),
                    'percent': percent
                }
            )
        except Exception as e:
            return HealthStatus(
                service='memory',
                status='unhealthy',
                timestamp=datetime.now(),
                message=f'Memory check failed: {str(e)}'
            )
    
    def check_cache(self, cache_dir: str = './data/cache') -> HealthStatus:
        """
        Check cache directory status
        
        Args:
            cache_dir: Cache directory path
            
        Returns:
            HealthStatus object
        """
        try:
            if not os.path.exists(cache_dir):
                return HealthStatus(
                    service='cache',
                    status='degraded',
                    timestamp=datetime.now(),
                    message='Cache directory does not exist'
                )
            
            # Count cache files
            cache_files = [f for f in os.listdir(cache_dir) if f.endswith('.csv')]
            
            # Calculate cache size
            total_size = sum(
                os.path.getsize(os.path.join(cache_dir, f))
                for f in cache_files
            )
            size_mb = total_size / (1024 ** 2)
            
            return HealthStatus(
                service='cache',
                status='healthy',
                timestamp=datetime.now(),
                message=f'Cache operational with {len(cache_files)} files',
                details={
                    'file_count': len(cache_files),
                    'size_mb': round(size_mb, 2)
                }
            )
        except Exception as e:
            return HealthStatus(
                service='cache',
                status='degraded',
                timestamp=datetime.now(),
                message=f'Cache check failed: {str(e)}'
            )
    
    def get_overall_health(self) -> Dict:
        """
        Run all health checks and return overall status
        
        Returns:
            Dictionary with overall health status and individual checks
        """
        checks = {
            'database': self.check_database(),
            'api': self.check_api(),
            'disk': self.check_disk_space(),
            'memory': self.check_memory(),
            'cache': self.check_cache()
        }
        
        # Determine overall status
        statuses = [check.status for check in checks.values()]
        
        if 'unhealthy' in statuses:
            overall_status = 'unhealthy'
        elif 'degraded' in statuses:
            overall_status = 'degraded'
        else:
            overall_status = 'healthy'
        
        return {
            'status': overall_status,
            'timestamp': datetime.now().isoformat(),
            'checks': {name: check.to_dict() for name, check in checks.items()}
        }


# Global health check instance
_health_check: Optional[HealthCheck] = None


def get_health_check() -> HealthCheck:
    """Get global health check instance (singleton)"""
    global _health_check
    if _health_check is None:
        _health_check = HealthCheck()
    return _health_check
