"""Main.py template for basic mode."""

TEMPLATE = '''from fastapi import FastAPI
from routers.health import router as health_router

app = FastAPI(title="${project_name}")

app.include_router(health_router, tags=["health"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
