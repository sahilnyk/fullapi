"""Logging templates."""

LOGGING_CONFIG = '''"""Logging configuration."""

import os
import logging
import logging.config
from typing import Optional, Dict, Any
from pathlib import Path


class LoggingConfig:
    """Logging configuration settings."""
    
    def __init__(self):
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()
        self.log_format: str = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.log_date_format: str = os.getenv("LOG_DATE_FORMAT", "%Y-%m-%d %H:%M:%S")
        self.log_file_path: str = os.getenv("LOG_FILE_PATH", "app.log")
        self.log_max_bytes: int = int(os.getenv("LOG_MAX_BYTES", "10485760"))  # 10MB
        self.log_backup_count: int = int(os.getenv("LOG_BACKUP_COUNT", "5"))
        self.log_rotation: str = os.getenv("LOG_ROTATION", "daily")  # daily, weekly, monthly, size
        
        # Console logging
        self.console_log_level: str = os.getenv("CONSOLE_LOG_LEVEL", "INFO").upper()
        self.console_log_format: str = os.getenv("CONSOLE_LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.console_colors_enabled: bool = os.getenv("CONSOLE_COLORS_ENABLED", "true").lower() == "true"
        
        # File logging
        self.file_log_level: str = os.getenv("FILE_LOG_LEVEL", "DEBUG").upper()
        self.file_log_format: str = os.getenv("FILE_LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)d")
        self.file_log_date_format: str = os.getenv("FILE_LOG_DATE_FORMAT", "%Y-%m-%d")
        
        # JSON logging
        self.json_log_enabled: bool = os.getenv("JSON_LOG_ENABLED", "false").lower() == "true"
        self.json_log_file: str = os.getenv("JSON_LOG_FILE", "app.json")
        self.json_log_format: str = os.getenv("JSON_LOG_FORMAT", "%(asctime)s %(name)s %(levelname)s %(message)s")
        
        # Structured logging
        self.structured_logging_enabled: bool = os.getenv("STRUCTURED_LOGGING_ENABLED", "false").lower() == "true"
        self.structured_log_format: str = os.getenv("STRUCTURED_LOG_FORMAT", "json")
        
        # Request logging
        self.request_logging_enabled: bool = os.getenv("REQUEST_LOGGING_ENABLED", "true").lower() == "true"
        self.request_log_format: str = os.getenv("REQUEST_LOG_FORMAT", "%(method)s %(url)s %(status)s %(duration_ms)dms")
        self.request_log_headers: list = os.getenv("REQUEST_LOG_HEADERS", "User-Agent,Content-Type,Accept").split(",") if os.getenv("REQUEST_LOG_HEADERS") else []
        self.request_log_exclude_paths: list = os.getenv("REQUEST_LOG_EXCLUDE_PATHS", "/health,/metrics,/static").split(",") if os.getenv("REQUEST_LOG_EXCLUDE_PATHS") else ["/health", "/metrics", "/static"]
        
        # Error logging
        self.error_log_enabled: bool = os.getenv("ERROR_LOG_ENABLED", "true").lower() == "true"
        self.error_log_file: str = os.getenv("ERROR_LOG_FILE", "errors.log")
        self.error_log_format: str = os.getenv("ERROR_LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.error_log_max_bytes: int = int(os.getenv("ERROR_LOG_MAX_BYTES", "5242880"))  # 5MB
        self.error_log_backup_count: int = int(os.getenv("ERROR_LOG_BACKUP_COUNT", "3"))
        
        # Performance logging
        self.performance_logging_enabled: bool = os.getenv("PERFORMANCE_LOGGING_ENABLED", "false").lower() == "true"
        self.performance_log_file: str = os.getenv("PERFORMANCE_LOG_FILE", "performance.log")
        self.performance_log_format: str = os.getenv("PERFORMANCE_LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(duration_ms)dms - %(memory_mb)dMB")
        
        # Security logging
        self.security_logging_enabled: bool = os.getenv("SECURITY_LOGGING_ENABLED", "true").lower() == "true"
        self.security_log_file: str = os.getenv("SECURITY_LOG_FILE", "security.log")
        self.security_log_format: str = os.getenv("SECURITY_LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(ip)s - %(user_id)s - %(action)s")
        
        # Database logging
        self.db_logging_enabled: bool = os.getenv("DB_LOGGING_ENABLED", "false").lower() == "true"
        self.db_log_file: str = os.getenv("DB_LOG_FILE", "db.log")
        self.db_log_format: str = os.getenv("DB_LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(query_time)fms - %(rows_affected)d")
        
        # Audit logging
        self.audit_logging_enabled: bool = os.getenv("AUDIT_LOGGING_ENABLED", "false").lower() == "true"
        self.audit_log_file: str = os.getenv("AUDIT_LOG_FILE", "audit.log")
        self.audit_log_format: str = os.getenv("AUDIT_LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(user_id)s - %(action)s - %(resource)s - %(details)s")
'''


LOGGING_SETUP = '''"""Logging setup and configuration."""

import logging
import logging.config
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
from core.logging_config import LoggingConfig


def setup_logging(config: Optional[LoggingConfig] = None) -> logging.Logger:
    """Setup comprehensive logging configuration."""
    if config is None:
        config = LoggingConfig()
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    logging.getLogger().handlers.clear()
    
    # Set log level
    log_level = getattr(logging, config.log_level.upper(), logging.INFO)
    
    # Create formatters
    console_formatter = logging.Formatter(config.console_log_format)
    file_formatter = logging.Formatter(config.file_log_format)
    json_formatter = logging.Formatter(config.json_log_format) if config.json_log_enabled else None
    error_formatter = logging.Formatter(config.error_log_format)
    
    # Create handlers
    handlers = []
    
    # Console handler
    if config.console_log_level:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, config.console_log_level.upper(), logging.INFO))
        console_handler.setFormatter(console_formatter)
        if config.console_colors_enabled:
            console_handler.addFilter(ColorFilter())
        handlers.append(console_handler)
    
    # File handler
    if config.file_log_level:
        # Create rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            filename=config.log_file_path,
            maxBytes=config.log_max_bytes,
            backupCount=config.log_backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, config.file_log_level.upper(), logging.DEBUG))
        file_handler.setFormatter(file_formatter)
        handlers.append(file_handler)
    
    # Error file handler
    if config.error_log_enabled:
        error_handler = logging.handlers.RotatingFileHandler(
            filename=config.error_log_file,
            maxBytes=config.error_log_max_bytes,
            backupCount=config.error_log_backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(error_formatter)
        error_handler.addFilter(ErrorOnlyFilter())
        handlers.append(error_handler)
    
    # JSON file handler
    if config.json_log_enabled:
        json_handler = logging.handlers.RotatingFileHandler(
            filename=config.json_log_file,
            maxBytes=config.log_max_bytes,
            backupCount=config.log_backup_count,
            encoding='utf-8'
        )
        json_handler.setLevel(getattr(logging, config.log_level.upper(), logging.INFO))
        json_handler.setFormatter(json_formatter)
        handlers.append(json_handler)
    
    # Performance handler
    if config.performance_logging_enabled:
        performance_handler = logging.handlers.RotatingFileHandler(
            filename=config.performance_log_file,
            maxBytes=config.log_max_bytes,
            backupCount=config.log_backup_count,
            encoding='utf-8'
        )
        performance_handler.setLevel(logging.INFO)
        performance_handler.setFormatter(logging.Formatter(config.performance_log_format))
        handlers.append(performance_handler)
    
    # Security handler
    if config.security_logging_enabled:
        security_handler = logging.handlers.RotatingFileHandler(
            filename=config.security_log_file,
            maxBytes=config.error_log_max_bytes,
            backupCount=config.error_log_backup_count,
            encoding='utf-8'
        )
        security_handler.setLevel(logging.INFO)
        security_handler.setFormatter(logging.Formatter(config.security_log_format))
        handlers.append(security_handler)
    
    # Database handler
    if config.db_logging_enabled:
        db_handler = logging.handlers.RotatingFileHandler(
            filename=config.db_log_file,
            maxBytes=config.log_max_bytes,
            backupCount=config.log_backup_count,
            encoding='utf-8'
        )
        db_handler.setLevel(getattr(logging, config.db_log_level.upper(), logging.DEBUG))
        db_handler.setFormatter(logging.Formatter(config.db_log_format))
        handlers.append(db_handler)
    
    # Audit handler
    if config.audit_logging_enabled:
        audit_handler = logging.handlers.RotatingFileHandler(
            filename=config.audit_log_file,
            maxBytes=config.error_log_max_bytes,
            backupCount=config.error_log_backup_count,
            encoding='utf-8'
        )
        audit_handler.setLevel(logging.INFO)
        audit_handler.setFormatter(logging.Formatter(config.audit_log_format))
        handlers.append(audit_handler)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers = handlers
    
    # Configure specific loggers
    loggers = {
        'uvicorn': logging.getLogger('uvicorn'),
        'fastapi': logging.getLogger('fastapi'),
        'sqlalchemy': logging.getLogger('sqlalchemy.engine'),
        'app': logging.getLogger('app'),
        'security': logging.getLogger('security'),
        'performance': logging.getLogger('performance'),
        'database': logging.getLogger('database'),
        'audit': logging.getLogger('audit'),
    }
    
    for name, logger in loggers.items():
        logger.setLevel(log_level)
        logger.handlers = handlers
        logger.propagate = False
    
    return root_logger


class ColorFilter(logging.Filter):
    """Filter to add colors to console output."""
    
    def __init__(self):
        self.colors = {
            logging.DEBUG: '\033[36m',  # Gray
            logging.INFO: '\033[32m',  # Green
            logging.WARNING: '\033[33m',  # Yellow
            logging.ERROR: '\033[31m',  # Red
            logging.CRITICAL: '\033[35m',  # Magenta
        }
        self.reset = '\033[0m'  # Reset
    
    def filter(self, record):
        """Add color based on log level."""
        if record.levelno in self.colors:
            record.msg = f"{self.colors[record.levelno]}{record.msg}\033[0m"
        return True


class ErrorOnlyFilter(logging.Filter):
    """Filter to only allow error level messages."""
    
    def filter(self, record):
        """Only allow error level messages."""
        return record.levelno >= logging.ERROR


def get_logger(name: str) -> logging.Logger:
    """Get a specific logger."""
    return logging.getLogger(name)


def log_request(request_id: str, method: str, url: str, status_code: int, 
                duration_ms: float = None, user_id: str = None, 
                ip_address: str = None, user_agent: str = None):
    """Log request information."""
    logger = get_logger('app')
    logger.info(
        f"Request: {method} {url} - {status_code} - {duration_ms}ms - "
        f"ID:{request_id} - IP:{ip_address} - UA:{user_agent}"
    )


def log_security_event(user_id: str, action: str, resource: str, 
                   ip_address: str = None, details: str = None):
    """Log security events."""
    logger = get_logger('security')
    logger.info(
        f"Security Event: {action} - User:{user_id} - "
        f"Resource:{resource} - IP:{ip_address} - Details:{details}"
    )


def log_performance(operation: str, duration_ms: float, memory_mb: float = None, 
                   rows_affected: int = None, query_time_ms: float = None):
    """Log performance metrics."""
    logger = get_logger('performance')
    logger.info(
        f"Performance: {operation} - {duration_ms}ms - "
        f"Memory:{memory_mb}MB - Rows:{rows_affected} - Query:{query_time_ms}ms"
    )


def log_database_operation(operation: str, table: str, rows_affected: int = None, 
                        query_time_ms: float = None, error: str = None):
    """Log database operations."""
    logger = get_logger('database')
    if error:
        logger.error(f"Database Error: {operation} - Table:{table} - Error:{error}")
    else:
        logger.info(
            f"Database: {operation} - Table:{table} - "
            f"Rows:{rows_affected} - Query:{query_time_ms}ms"
        )


def log_audit(user_id: str, action: str, resource: str, 
            old_values: Optional[Dict[str, Any]] = None, 
            new_values: Optional[Dict[str, Any]] = None, 
            success: bool = True):
    """Log audit events."""
    logger = get_logger('audit')
    
    status = "SUCCESS" if success else "FAILED"
    log_msg = f"Audit: {action} - User:{user_id} - Resource:{resource} - Status:{status}"
    
    if old_values:
        old_str = ", ".join([f"{k}:{v}" for k, v in old_values.items()])
        log_msg += f" - Old: {old_str}"
    
    if new_values:
        new_str = ", ".join([f"{k}:{v}" for k, v in new_values.items()])
        log_msg += f" - New: {new_str}"
    
    logger.info(log_msg)


def setup_uvicorn_logging():
    """Setup uvicorn specific logging configuration."""
    logging.getLogger('uvicorn').setLevel(logging.INFO)
    logging.getLogger('uvicorn.error').setLevel(logging.ERROR)
    
    # Configure uvicorn to use our logging
    os.environ['UVICORN_LOG_CONFIG'] = 'logging'
    os.environ['UVICORN_LOG_LEVEL'] = 'info'
    os.environ['UVICORN_LOG_FORMAT'] = '%(asctime)s - %(levelname)s - %(message)s'


def create_log_directories():
    """Create log directories if they don't exist."""
    directories = ['logs', 'logs/app', 'logs/errors', 'logs/performance', 'logs/security', 'logs/database', 'logs/audit']
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)


def get_log_config() -> LoggingConfig:
    """Get logging configuration from environment."""
    return LoggingConfig()
'''


REQUIREMENTS_LOGGING = """
"""
