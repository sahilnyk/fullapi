from fastapi import FastAPI

app = FastAPI(title="custom_app")


@app.get("/")
def root():
    return {"app": "custom_app", "status": "running"}
