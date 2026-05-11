"""Environment file template."""

ENV_EXAMPLE = '''# App
DEBUG=false

# Database Configuration
DATABASE_URL=sqlite:///./app.db
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=password
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
CORS_ALLOW_HEADERS=*
CORS_EXPOSE_HEADERS=

# Rate Limiting Configuration
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

# JWT
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
'''
