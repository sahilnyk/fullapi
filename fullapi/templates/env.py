"""Environment file template."""

ENV_EXAMPLE = '''# App
DEBUG=false

# Database
DATABASE_URL=sqlite:///./app.db
# For PostgreSQL: DATABASE_URL=postgresql://user:password@localhost/dbname
# For MySQL: DATABASE_URL=mysql+pymysql://user:password@localhost/dbname

# JWT
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
'''
