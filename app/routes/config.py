import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.config.answerly_branding import load_answerly_branding
from app.config.company_config import (
    get_company_config_path,
    load_company_config,
    has_active_company_config,
)


router = APIRouter()

ALLOWED_ASSETS = {
    "logo",
    "favicon",
    "assistant_avatar",
}

@router.get("/config/status")
def get_company_config_status():
    has_active_company = has_active_company_config()

    return {
        "has_active_company": has_active_company,
        "source": "company" if has_active_company else "answerly",
    }

@router.get("/config/company.json")
def get_company_config():
    try:
        return load_company_config()
    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error
    except (json.JSONDecodeError, ValueError) as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error

@router.get("/config/answerly/branding.json")
def get_answerly_branding():
    try:
        return load_answerly_branding()
    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error
    except json.JSONDecodeError as error:
        raise HTTPException(
            status_code=500,
            detail="Answer.ly branding configuration contains invalid JSON.",
        ) from error

@router.get("/config/assets/{asset_name}")
def get_company_asset(asset_name: str):
    if asset_name not in ALLOWED_ASSETS:
        raise HTTPException(
            status_code=404,
            detail="Unknown branding asset.",
        )

    try:
        company = load_company_config()
        config_path = get_company_config_path()
    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error
    except (json.JSONDecodeError, ValueError) as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error

    relative_asset_path = (
        company.get("branding", {})
        .get("assets", {})
        .get(asset_name)
    )

    if not relative_asset_path:
        raise HTTPException(
            status_code=404,
            detail=f"No {asset_name} has been configured.",
        )

    config_directory = config_path.parent.resolve()
    asset_path = (
        config_directory / Path(relative_asset_path)
    ).resolve()

    if not asset_path.is_relative_to(config_directory):
        raise HTTPException(
            status_code=400,
            detail="Invalid branding asset path.",
        )

    if not asset_path.is_file():
        raise HTTPException(
            status_code=404,
            detail=f"Configured {asset_name} file was not found.",
        )

    return FileResponse(asset_path)