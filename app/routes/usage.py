from fastapi import APIRouter

from app.services.usage_service import get_recent_usage

router = APIRouter()


@router.get("/usage")
def usage():
    return {
        "events": get_recent_usage(),
    }