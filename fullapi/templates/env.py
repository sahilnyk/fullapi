"""Environment file template."""

ENV_EXAMPLE = '''# App
DEBUG=false

# Database Configuration
DATABASE_URL=sqlite:///./app.db
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=CHANGE_ME_STRONG_PASSWORD_HERE
DB_NAME=app

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_SSL=false
REDIS_DECODE_RESPONSES=true
REDIS_SOCKET_TIMEOUT=5
REDIS_SOCKET_CONNECT_TIMEOUT=5
REDIS_HEALTH_CHECK_INTERVAL=30
REDIS_MAX_CONNECTIONS=10

# Middleware Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
CORS_ALLOW_CREDENTIALS=false
CORS_ALLOW_METHODS=GET,POST,PUT,DELETE,OPTIONS
CORS_ALLOW_HEADERS=Content-Type,Authorization,X-Request-ID
CORS_EXPOSE_HEADERS=

# Rate Limiting Configuration - ENABLED by default for security
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Security Headers Configuration
SECURITY_HEADERS_ENABLED=true
X-Content-Type-Options=nosniff
X-Frame-Options=DENY
X-XSS-Protection=1; mode=block
Strict-Transport-Security=max-age=31536000; includeSubDomains

# Gzip Configuration
GZIP_ENABLED=true
GZIP_MINIMUM_SIZE=1000

# Request Logging Configuration
REQUEST_LOGGING_ENABLED=true
REQUEST_LOGGING_FORMAT=%(asctime)s - %(levelname)s - %(message)s
REQUEST_LOGGING_EXCLUDE_PATHS=/health,/metrics

# Trusted Proxy Configuration
TRUSTED_PROXY_HEADERS=X-Forwarded-For,X-Forwarded-Proto,X-Forwarded-Host

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
LOG_DATE_FORMAT=%Y-%m-%d %H:%M:%S
LOG_FILE_PATH=app.log
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5
LOG_ROTATION=daily
CONSOLE_LOG_LEVEL=INFO
CONSOLE_COLORS_ENABLED=true
FILE_LOG_LEVEL=DEBUG
JSON_LOG_ENABLED=false
STRUCTURED_LOGGING_ENABLED=false
ERROR_LOG_ENABLED=true

# JWT - REQUIRED: Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=CHANGE_ME_GENERATE_RANDOM_SECRET_KEY
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
'''
