"""Requirements templates."""

BASIC = '''fastapi>=0.100.0
uvicorn[standard]>=0.22.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
python-multipart>=0.0.6
python-dotenv>=1.0.0
'''

FULL_BASE = '''fastapi>=0.100.0
uvicorn[standard]>=0.22.0
pydantic>=2.0.0
email-validator>=2.0.0
pydantic-settings>=2.0.0
sqlalchemy>=2.0.0
python-multipart>=0.0.6
python-dotenv>=1.0.0

# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
httpx>=0.24.0
'''

FULL_POSTGRESQL = '''psycopg2-binary>=2.9.0
'''

FULL_MYSQL = '''pymysql>=1.0.0
'''

FULL_AUTH = '''python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.0
'''
