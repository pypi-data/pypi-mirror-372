"""Monitoring Generator - Generates monitoring configuration"""

from ...generators.base_generator import BaseGenerator


class MonitoringGenerator(BaseGenerator):
    """Generates monitoring configuration files"""

    def should_generate(self):
        return self.config.include_monitoring

    def generate(self):
        """Generate monitoring files"""
        if not self.config.include_monitoring:
            return

        # Generate Prometheus configuration
        prometheus_content = self._get_prometheus_template()
        self.write_file(
            f"{self.config.path}/monitoring/prometheus.yml", prometheus_content
        )

        # Generate monitoring utilities
        monitoring_content = self._get_monitoring_template()
        self.write_file(
            f"{self.config.path}/app/core/monitoring.py", monitoring_content
        )

    def _get_prometheus_template(self) -> str:
        """Get Prometheus configuration template"""
        template = f"""global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: '{self.config.name}'
    static_configs:
      - targets: ['web:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
"""
        return template

    def _get_monitoring_template(self) -> str:
        """Get monitoring utilities template"""
        template = f'''"""
Monitoring utilities for {self.config.name}
"""

import time
import logging
from functools import wraps
from typing import Optional, Dict, Any
from prometheus_client import Counter, Histogram, Gauge, Info
import structlog

# Configure structured logging
logger = structlog.get_logger()

# Prometheus metrics
REQUEST_COUNT = Counter(
    'requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'active_connections',
    'Number of active connections'
)

APPLICATION_INFO = Info(
    'application_info',
    'Application information'
)

# Set application info
APPLICATION_INFO.info({{
    'name': '{self.config.name}',
    'version': '1.0.0',
    'python_version': '{self.config.python_version}'
}})


def monitor_requests(func):
    """
    Decorator to monitor request metrics
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        method = kwargs.get('method', 'GET')
        endpoint = kwargs.get('endpoint', 'unknown')
        
        try:
            result = await func(*args, **kwargs)
            status_code = getattr(result, 'status_code', 200)
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
            return result
        except Exception as e:
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=500).inc()
            logger.error("Request failed", error=str(e), endpoint=endpoint)
            raise
        finally:
            REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(time.time() - start_time)
    
    return wrapper


def log_performance(operation: str):
    """
    Decorator to log performance metrics
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            logger.info(f"Starting {{operation}}")
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"Completed {{operation}}", duration=duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"Failed {{operation}}", error=str(e), duration=duration)
                raise
        
        return wrapper
    return decorator


class HealthChecker:
    """
    Health check utilities
    """
    
    def __init__(self):
        self.checks = {{}}
    
    def add_check(self, name: str, check_func):
        """Add a health check"""
        self.checks[name] = check_func
    
    async def run_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        results = {{}}
        
        for name, check_func in self.checks.items():
            try:
                result = await check_func() if callable(check_func) else check_func
                results[name] = {{"status": "healthy", "details": result}}
            except Exception as e:
                results[name] = {{"status": "unhealthy", "error": str(e)}}
        
        return results


# Global health checker instance
health_checker = HealthChecker()


async def database_health_check():
    """Database health check"""
    # Implement database connectivity check
    return {{"message": "Database is accessible"}}


async def external_service_health_check():
    """External service health check"""
    # Implement external service checks
    return {{"message": "External services are accessible"}}


# Register default health checks
health_checker.add_check("database", database_health_check)
health_checker.add_check("external_services", external_service_health_check)
'''
        return template
