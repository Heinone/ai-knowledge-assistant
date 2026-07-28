from fastapi import APIRouter
from fastapi.responses import FileResponse
from pathlib import Path

router = APIRouter()

COMPANY_CONFIG_PATH = Path(
    "data/company/company.json"
)


@router.get("/config/company.json")
def get_company_config():
    return FileResponse(
        COMPANY_CONFIG_PATH
    )