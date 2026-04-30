"""Requirements templates."""

BASIC = '''fastapi
uvicorn
pydantic-settings
'''

FULL = '''fastapi
uvicorn
pydantic
pydantic[email]
pydantic-settings
sqlalchemy
'''

FULL_SQLITE = FULL + '''
'''

FULL_POSTGRESQL = FULL + '''
psycopg2-binary
'''

FULL_MYSQL = FULL + '''
pymysql
'''

FULL_AUTH = '''python-jose[cryptography]
passlib[bcrypt]
'''
