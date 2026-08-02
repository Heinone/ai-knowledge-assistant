import json
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import ValidationError

from app.config.answerly_branding import load_answerly_branding
from app.config.company_config import (
    ACTIVE_COMPANY_CONFIG_PATH,
    get_company_config_path,
    has_active_company_config,
    load_company_config,
)
from app.config.config_validator import validate_company_config_or_raise
from app.models.company_setup import CompanySetupRequest
from app.services.brand_asset_service import (
    BrandAssetValidationError,
    save_brand_asset_upload,
    validate_brand_asset_upload,
)
from app.services.company_setup_service import build_company_config,  save_company_config


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


@router.post("/config/company/setup/validate")
def validate_company_setup(request: CompanySetupRequest) -> dict:
    company_config = build_company_config(request)

    validate_company_config_or_raise(company_config)

    return {
        "valid": True,
        "company_config": company_config,
    }


@router.post("/config/company/setup/validate-multipart")
async def validate_company_setup_multipart(
    setup_json: str = Form(...),
    logo: UploadFile | None = File(default=None),
    favicon: UploadFile | None = File(default=None),
    assistant_avatar: UploadFile | None = File(default=None),
) -> dict:
    try:
        request = CompanySetupRequest.model_validate_json(setup_json)
    except ValidationError as error:
        raise HTTPException(
            status_code=422,
            detail=json.loads(error.json()),
        ) from error

    company_config = build_company_config(request)

    validate_company_config_or_raise(company_config)

    try:
        validated_files = {
            "logo": await validate_brand_asset_upload(
                "logo",
                logo,
            ),
            "favicon": await validate_brand_asset_upload(
                "favicon",
                favicon,
            ),
            "assistant_avatar": await validate_brand_asset_upload(
                "assistant_avatar",
                assistant_avatar,
            ),
        }
    except BrandAssetValidationError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    return {
        "valid": True,
        "company_config": company_config,
        "files": validated_files,
    }

@router.post("/config/company/setup")
async def create_company_setup(
    setup_json: str = Form(...),
    logo: UploadFile | None = File(default=None),
    favicon: UploadFile | None = File(default=None),
    assistant_avatar: UploadFile | None = File(default=None),
) -> dict:
    if has_active_company_config():
        raise HTTPException(
            status_code=409,
            detail="An active company configuration already exists.",
        )

    try:
        request = CompanySetupRequest.model_validate_json(setup_json)
    except ValidationError as error:
        raise HTTPException(
            status_code=422,
            detail=json.loads(error.json()),
        ) from error

    company_config = build_company_config(request)

    try:
        validated_files = {
            "logo": await validate_brand_asset_upload(
                "logo",
                logo,
            ),
            "favicon": await validate_brand_asset_upload(
                "favicon",
                favicon,
            ),
            "assistant_avatar": await validate_brand_asset_upload(
                "assistant_avatar",
                assistant_avatar,
            ),
        }
    except BrandAssetValidationError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    assets_directory = ACTIVE_COMPANY_CONFIG_PATH.parent / "assets"

    try:
        saved_assets = {
            "logo": await save_brand_asset_upload(
                logo,
                validated_files["logo"],
                assets_directory,
            ),
            "favicon": await save_brand_asset_upload(
                favicon,
                validated_files["favicon"],
                assets_directory,
            ),
            "assistant_avatar": await save_brand_asset_upload(
                assistant_avatar,
                validated_files["assistant_avatar"],
                assets_directory,
            ),
        }

        company_config["branding"]["assets"] = saved_assets

        validate_company_config_or_raise(company_config)

        save_company_config(
            company_config,
            ACTIVE_COMPANY_CONFIG_PATH,
        )
    except (OSError, ValueError) as error:
        raise HTTPException(
            status_code=500,
            detail="Could not save the company setup.",
        ) from error

    return {
        "created": True,
        "company_id": company_config["company_id"],
        "company_config": company_config,
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
            detail=(
                "Answer.ly branding configuration contains invalid JSON."
            ),
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