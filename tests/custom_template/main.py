from fastapi import FastAPI

app = FastAPI(title="${project_name}")


@app.get("/")
def root():
    return {"app": "${project_name}", "status": "running"}
