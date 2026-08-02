import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import UploadFile


MAX_BRAND_ASSET_SIZE_BYTES = 5 * 1024 * 1024

ALLOWED_ASSET_FORMATS = {
    "logo": {
        ".png": {"image/png"},
        ".jpg": {"image/jpeg"},
        ".jpeg": {"image/jpeg"},
        ".webp": {"image/webp"},
    },
    "favicon": {
        ".png": {"image/png"},
        ".ico": {
            "image/x-icon",
            "image/vnd.microsoft.icon",
            "image/ico",
        },
    },
    "assistant_avatar": {
        ".png": {"image/png"},
        ".jpg": {"image/jpeg"},
        ".jpeg": {"image/jpeg"},
        ".webp": {"image/webp"},
    },
}


class BrandAssetValidationError(ValueError):
    pass


async def validate_brand_asset_upload(
    asset_name: str,
    upload: UploadFile | None,
) -> dict | None:
    if upload is None:
        return None

    filename = upload.filename or ""
    extension = Path(filename).suffix.lower()

    allowed_formats = ALLOWED_ASSET_FORMATS[asset_name]

    if extension not in allowed_formats:
        allowed_extensions = ", ".join(sorted(allowed_formats))

        raise BrandAssetValidationError(
            f"Invalid {asset_name} file extension. "
            f"Allowed extensions: {allowed_extensions}."
        )

    if upload.content_type not in allowed_formats[extension]:
        raise BrandAssetValidationError(
            f"Invalid {asset_name} content type: "
            f"{upload.content_type or 'unknown'}."
        )

    content = await upload.read(MAX_BRAND_ASSET_SIZE_BYTES + 1)
    await upload.seek(0)

    file_size = len(content)

    if file_size == 0:
        raise BrandAssetValidationError(
            f"The uploaded {asset_name} file is empty."
        )

    if file_size > MAX_BRAND_ASSET_SIZE_BYTES:
        raise BrandAssetValidationError(
            f"The uploaded {asset_name} exceeds the 5 MB limit."
        )

    return {
        "original_filename": filename,
        "content_type": upload.content_type,
        "size": file_size,
        "target_filename": f"{asset_name}{extension}",
    }

ASSET_COPY_CHUNK_SIZE_BYTES = 1024 * 1024


async def save_brand_asset_upload(
    upload: UploadFile | None,
    validated_file: dict | None,
    assets_directory: Path,
) -> str | None:
    if upload is None or validated_file is None:
        return None

    assets_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    resolved_assets_directory = assets_directory.resolve()
    target_filename = validated_file["target_filename"]

    target_path = (
        resolved_assets_directory / target_filename
    ).resolve()

    if not target_path.is_relative_to(resolved_assets_directory):
        raise ValueError("Invalid branding asset target path.")

    temporary_path: Path | None = None

    try:
        with NamedTemporaryFile(
            mode="wb",
            dir=resolved_assets_directory,
            prefix=f".{target_filename}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)

            while True:
                chunk = await upload.read(
                    ASSET_COPY_CHUNK_SIZE_BYTES,
                )

                if not chunk:
                    break

                temporary_file.write(chunk)

            temporary_file.flush()
            os.fsync(temporary_file.fileno())

        os.replace(
            temporary_path,
            target_path,
        )
    finally:
        await upload.seek(0)

        if temporary_path and temporary_path.exists():
            temporary_path.unlink()

    return (
        Path("assets") / target_filename
    ).as_posix()