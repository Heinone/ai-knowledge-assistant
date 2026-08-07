import argparse
import json
import os
import shutil
from tempfile import NamedTemporaryFile
from pathlib import Path
from typing import Any
from datetime import datetime, timezone
from uuid import uuid4

from app.config.company_config import PROJECT_ROOT
from app.config.config_validator import (
    validate_company_config_or_raise,
)
from app.services.company_setup_service import (
    save_company_config,
)
from app.services.document_registry_service import (
    replace_document_records_for_mode,
)
from app.services.ingestion_service import (
    build_local_index_snapshot_from_directory,
    reset_local_index,
)
from scripts.reset_app_state import reset_app_state
from app.models.assistant_mode import AssistantMode


EXAMPLES_ROOT = PROJECT_ROOT / "data" / "examples"
RUNTIME_ENV_PATH = PROJECT_ROOT / ".env.runtime"
ACTIVE_COMPANY_CONFIG_PATH = (
    PROJECT_ROOT / "data" / "company" / "company.json"
)
ACTIVE_COMPANY_ASSETS_DIRECTORY = (
    PROJECT_ROOT / "data" / "company" / "assets"
)
ALLOWED_DOCUMENT_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".md",
}

def _activate_mode_documents(
    *,
    example_directory: Path,
    company_id: str,
    mode: AssistantMode,
) -> dict[str, Any]:
    source_directory = (
        example_directory
        / "documents"
        / mode.value
    )

    if not source_directory.is_dir():
        return {
            "mode": mode.value,
            "documents": 0,
        }

    source_files = sorted(
        path
        for path in source_directory.iterdir()
        if path.is_file()
    )

    unsupported_files = [
        path.name
        for path in source_files
        if path.suffix.lower()
        not in ALLOWED_DOCUMENT_EXTENSIONS
    ]

    if unsupported_files:
        raise ValueError(
            "Unsupported example documents for "
            f"'{mode.value}': "
            + ", ".join(unsupported_files)
        )

    if not source_files:
        return {
            "mode": mode.value,
            "documents": 0,
        }

    runtime_upload_directory = (
        PROJECT_ROOT
        / "data"
        / "uploads"
        / mode.value
    )

    runtime_index_directory = (
        PROJECT_ROOT
        / "data"
        / "indexes"
        / mode.value
    )

    staging_root = (
        PROJECT_ROOT
        / "data"
        / "activation_staging"
        / uuid4().hex
    )

    staged_upload_directory = (
        staging_root
        / "uploads"
        / mode.value
    )

    staged_index_directory = (
        staging_root
        / "indexes"
        / mode.value
    )

    staged_upload_directory.mkdir(
        parents=True,
        exist_ok=False,
    )

    timestamp = datetime.now(
        timezone.utc
    )

    registry_records = []

    try:
        for source_path in source_files:
            document_id = uuid4().hex

            staged_path = (
                staged_upload_directory
                / f"{document_id}_{source_path.name}"
            )

            shutil.copy2(
                source_path,
                staged_path,
            )

            runtime_path = (
                runtime_upload_directory
                / staged_path.name
            )

            registry_records.append(
                {
                    "document_id": document_id,
                    "filename": source_path.name,
                    "stored_path": runtime_path.relative_to(
                        PROJECT_ROOT
                    ).as_posix(),
                    "size_bytes": staged_path.stat().st_size,
                    "status": "indexed",
                    "documents_loaded": None,
                    "error_message": None,
                    "uploaded_at": timestamp,
                    "updated_at": timestamp,
                }
            )

        build_local_index_snapshot_from_directory(
            source_directory=staged_upload_directory,
            persist_directory=staged_index_directory,
            chunk_size=1200,
            chunk_overlap=150,
        )

        runtime_upload_directory.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        runtime_index_directory.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.move(
            str(staged_upload_directory),
            str(runtime_upload_directory),
        )

        shutil.move(
            str(staged_index_directory),
            str(runtime_index_directory),
        )

        replace_document_records_for_mode(
            company_id=company_id,
            mode=mode,
            documents=registry_records,
        )

        reset_local_index(mode)

    except Exception:
        shutil.rmtree(
            runtime_upload_directory,
            ignore_errors=True,
        )

        shutil.rmtree(
            runtime_index_directory,
            ignore_errors=True,
        )

        reset_local_index(mode)

        raise

    finally:
        shutil.rmtree(
            staging_root,
            ignore_errors=True,
        )

    return {
        "mode": mode.value,
        "documents": len(registry_records),
    }

def _activate_company_assets(
    example_directory: Path,
) -> list[str]:
    source_directory = (
        example_directory / "assets"
    )

    if not source_directory.is_dir():
        return []

    ACTIVE_COMPANY_ASSETS_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    copied_assets: list[str] = []

    for source_path in sorted(
        source_directory.iterdir()
    ):
        if not source_path.is_file():
            continue

        destination_path = (
            ACTIVE_COMPANY_ASSETS_DIRECTORY
            / source_path.name
        )

        shutil.copy2(
            source_path,
            destination_path,
        )

        copied_assets.append(
            source_path.name
        )

    return copied_assets

def _activate_company_config(
    *,
    company: dict[str, Any],
    example_directory: Path,
    available_modes: str,
) -> dict[str, Any]:
    reset_app_state()

    try:
        _write_runtime_env(
            available_modes
        )

        save_company_config(
            company,
            ACTIVE_COMPANY_CONFIG_PATH,
        )

        activated_assets = (
            _activate_company_assets(
                example_directory
            )
        )

        enabled_modes = _get_enabled_modes(
            company
        )

        activated_modes = []

        for mode in enabled_modes:
            activated_modes.append(
                _activate_mode_documents(
                    example_directory=example_directory,
                    company_id=company["company_id"],
                    mode=mode,
                )
            )

    except Exception:
        reset_app_state()
        raise

    return {
        "assets": activated_assets,
        "modes": activated_modes,
    }

def _write_runtime_env(
    available_modes: str,
) -> None:
    runtime_env_directory = (
        RUNTIME_ENV_PATH.parent.resolve()
    )

    temporary_path: Path | None = None

    try:
        with NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=runtime_env_directory,
            prefix=".env.runtime.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(
                temporary_file.name
            )

            temporary_file.write(
                f"AVAILABLE_MODES={available_modes}\n"
            )

            temporary_file.flush()
            os.fsync(
                temporary_file.fileno()
            )

        os.replace(
            temporary_path,
            RUNTIME_ENV_PATH,
        )
    finally:
        if (
            temporary_path
            and temporary_path.exists()
        ):
            temporary_path.unlink()

def _resolve_example_directory(
    company_id: str,
) -> Path:
    examples_root = EXAMPLES_ROOT.resolve()
    example_directory = (
        EXAMPLES_ROOT / company_id
    ).resolve()

    if not example_directory.is_relative_to(
        examples_root
    ):
        raise ValueError(
            "Invalid example company path."
        )

    if not example_directory.is_dir():
        raise ValueError(
            f"Example company '{company_id}' does not exist."
        )

    return example_directory


def _load_example_config(
    example_directory: Path,
) -> dict[str, Any]:
    config_path = example_directory / "company.json"

    if not config_path.is_file():
        raise ValueError(
            f"Missing example company configuration: "
            f"'{config_path}'."
        )

    with config_path.open(
        "r",
        encoding="utf-8",
    ) as config_file:
        company = json.load(config_file)

    if not isinstance(company, dict):
        raise ValueError(
            "Example company configuration must be "
            "a JSON object."
        )

    return company


def _get_enabled_modes(
    company: dict[str, Any],
) -> tuple[AssistantMode, ...]:
    modes = company.get("modes")

    if not isinstance(modes, dict):
        raise ValueError(
            "Example company is missing assistant modes."
        )

    enabled_modes = tuple(
        mode
        for mode in AssistantMode
        if (
            isinstance(
                modes.get(mode.value),
                dict,
            )
            and modes[mode.value].get("enabled")
            is True
        )
    )

    if not enabled_modes:
        raise ValueError(
            "Example company must enable at least "
            "one assistant mode."
        )

    return enabled_modes


def build_activation_plan(
    company_id: str,
) -> dict[str, Any]:
    example_directory = (
        _resolve_example_directory(company_id)
    )

    company = _load_example_config(
        example_directory
    )

    if company.get("company_id") != company_id:
        raise ValueError(
            "Example directory name does not match "
            "company_id in company.json."
        )

    enabled_modes = _get_enabled_modes(
        company
    )

    validate_company_config_or_raise(
        company,
        available_modes=enabled_modes,
    )

    documents = {}

    for mode in enabled_modes:
        document_directory = (
            example_directory
            / "documents"
            / mode.value
        )

        mode_files = []

        if document_directory.is_dir():
            mode_files = sorted(
                path.name
                for path in document_directory.iterdir()
                if path.is_file()
            )

        documents[mode.value] = mode_files

    assets_directory = (
        example_directory / "assets"
    )

    assets = []

    if assets_directory.is_dir():
        assets = sorted(
            path.name
            for path in assets_directory.iterdir()
            if path.is_file()
        )

    return {
        "company_id": company_id,
        "company_name": company.get(
            "company_name"
        ),
        "enabled_modes": [
            mode.value
            for mode in enabled_modes
        ],
        "runtime_available_modes": ",".join(
            mode.value
            for mode in enabled_modes
        ),
        "documents": documents,
        "assets": assets,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Validate an Answer.ly example company "
            "and print its activation plan."
        )
    )

    parser.add_argument(
        "company_id",
        help=(
            "Example directory name, such as "
            "'aster_loom'."
        ),
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help=(
            "Reset current runtime state and activate "
            "the selected example company."
        ),
    )

    arguments = parser.parse_args()

    plan = build_activation_plan(
        arguments.company_id
    )

    if arguments.apply:
        example_directory = (
            _resolve_example_directory(
                arguments.company_id
            )
        )

        company = _load_example_config(
            example_directory
        )

        activation_result = (
            _activate_company_config(
                company=company,
                example_directory=example_directory,
                available_modes=plan[
                    "runtime_available_modes"
                ],
            )
        )

        plan["activated_assets"] = (
            activation_result["assets"]
        )

        plan["activated_modes"] = (
            activation_result["modes"]
    )

        plan["activated"] = True
    else:
        plan["activated"] = False

    print(
        json.dumps(
            plan,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

