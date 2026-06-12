"""Router templates."""

HEALTH_ROUTER = '''from fastapi import APIRouter

router = APIRouter()

@router.get("/health", summary="Health check")
def health_check():
    return {"status": "ok"}
'''