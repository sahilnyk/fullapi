"""Logging configuration."""

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
