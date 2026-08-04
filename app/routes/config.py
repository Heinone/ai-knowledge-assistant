import json

from pathlib import Path
from shutil import rmtree
from uuid import uuid4
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
from app.models.company_setup import (
    AssistantModeSettingsUpdateRequest,
    AssistantModesUpdateRequest,
    BrandingSettingsUpdateRequest,
    CompanySettingsUpdateRequest,
    CompanySetupRequest,
)
from app.models.assistant_mode import AssistantMode
from app.services.brand_asset_service import (
    BrandAssetValidationError,
    delete_brand_asset_file,
    save_brand_asset_upload,
    validate_brand_asset_upload,
)
from app.services.company_setup_service import (
    apply_assistant_mode_settings_update,
    apply_assistant_modes_update,
    apply_company_branding_update,
    apply_company_settings_update,
    build_company_config,
    save_company_config,
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

@router.put("/config/company/settings")
def update_company_settings(
    request: CompanySettingsUpdateRequest,
) -> dict:
    try:
        existing_config = load_company_config()
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

    updated_config = apply_company_settings_update(
        existing_config,
        request,
    )

    try:
        validate_company_config_or_raise(updated_config)
    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    try:
        save_company_config(
            updated_config,
            ACTIVE_COMPANY_CONFIG_PATH,
        )
    except (OSError, ValueError) as error:
        raise HTTPException(
            status_code=500,
            detail="Could not save company settings.",
        ) from error

    return {
        "updated": True,
        "company_config": updated_config,
    }

@router.put("/config/company/modes")
def update_assistant_modes(
    request: AssistantModesUpdateRequest,
) -> dict:
    try:
        existing_config = load_company_config()
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

    try:
        updated_config = apply_assistant_modes_update(
            existing_config,
            request,
        )

        validate_company_config_or_raise(
            updated_config
        )
    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    try:
        save_company_config(
            updated_config,
            ACTIVE_COMPANY_CONFIG_PATH,
        )
    except (OSError, ValueError) as error:
        raise HTTPException(
            status_code=500,
            detail="Could not save assistant mode settings.",
        ) from error

    return {
        "updated": True,
        "enabled_modes": [
            mode.value
            for mode in request.enabled_modes
        ],
        "default_mode": request.default_mode.value,
        "modes": updated_config["modes"],
    }

@router.put(
    "/config/company/assistants/{mode}"
)
def update_assistant_mode_settings(
    mode: AssistantMode,
    request: AssistantModeSettingsUpdateRequest,
) -> dict:
    try:
        existing_config = load_company_config()
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

    updated_config = (
        apply_assistant_mode_settings_update(
            existing_config,
            mode=mode,
            request=request,
        )
    )

    try:
        validate_company_config_or_raise(
            updated_config
        )
    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    try:
        save_company_config(
            updated_config,
            ACTIVE_COMPANY_CONFIG_PATH,
        )
    except (OSError, ValueError) as error:
        raise HTTPException(
            status_code=500,
            detail="Could not save assistant settings.",
        ) from error

    return {
        "updated": True,
        "mode": mode.value,
        "assistant_config": (
            updated_config["modes"][mode.value]
        ),
    }

@router.put("/config/company/branding")
async def update_company_branding(
    branding_json: str = Form(...),
    logo: UploadFile | None = File(default=None),
    favicon: UploadFile | None = File(default=None),
    assistant_avatar: UploadFile | None = File(default=None),
) -> dict:
    try:
        existing_config = load_company_config()
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

    try:
        request = BrandingSettingsUpdateRequest.model_validate_json(
            branding_json,
        )
    except ValidationError as error:
        raise HTTPException(
            status_code=422,
            detail=json.loads(error.json()),
        ) from error

    uploads = {
        "logo": logo,
        "favicon": favicon,
        "assistant_avatar": assistant_avatar,
    }

    try:
        validated_files = {
            asset_name: await validate_brand_asset_upload(
                asset_name,
                upload,
            )
            for asset_name, upload in uploads.items()
        }
    except BrandAssetValidationError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    updated_config = apply_company_branding_update(
        existing_config,
        request,
    )

    replaced_asset_names = [
        asset_name
        for asset_name, upload in uploads.items()
        if upload is not None
    ]

    version_directory: Path | None = None

    try:
        if replaced_asset_names:
            version_name = uuid4().hex

            relative_assets_directory = (
                Path("assets")
                / "versions"
                / version_name
            )

            version_directory = (
                ACTIVE_COMPANY_CONFIG_PATH.parent
                / relative_assets_directory
            )

            for asset_name in replaced_asset_names:
                saved_path = await save_brand_asset_upload(
                    uploads[asset_name],
                    validated_files[asset_name],
                    version_directory,
                    relative_assets_directory,
                )

                updated_config["branding"]["assets"][
                    asset_name
                ] = saved_path

        validate_company_config_or_raise(updated_config)

        save_company_config(
            updated_config,
            ACTIVE_COMPANY_CONFIG_PATH,
        )
    except (OSError, ValueError) as error:
        if version_directory is not None:
            rmtree(
                version_directory,
                ignore_errors=True,
            )

        raise HTTPException(
            status_code=500,
            detail="Could not save company branding.",
        ) from error

    existing_assets = (
        existing_config
        .get("branding", {})
        .get("assets", {})
    )

    config_directory = ACTIVE_COMPANY_CONFIG_PATH.parent

    for asset_name in replaced_asset_names:
        old_asset_path = existing_assets.get(asset_name)

        try:
            delete_brand_asset_file(
                old_asset_path,
                config_directory,
            )
        except (OSError, ValueError):
            # The update already succeeded. Old asset cleanup is best effort.
            pass

    return {
        "updated": True,
        "company_config": updated_config,
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