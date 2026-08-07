import json
import shutil
from pathlib import Path

from app.config.company_config import PROJECT_ROOT
from app.config.env_config import VECTOR_STORE


RUNTIME_DIRECTORIES = (
    "data/uploads",
    "data/indexes",
    "data/deletion_staging",
    "data/rebuild_staging",
    "data/rebuild_backups",
    "data/processed",
)

RUNTIME_FILES = (
    "data/company/company.json",
    "data/documents/document_registry.sqlite3",
    "data/documents/document_registry.sqlite3-wal",
    "data/documents/document_registry.sqlite3-shm",
)

COMPANY_ASSETS_DIRECTORY = "data/company/assets"


def _resolve_runtime_path(
    relative_path: str,
    *,
    project_root: Path,
) -> Path:
    resolved_root = project_root.resolve()
    resolved_path = (
        project_root
        / relative_path
    ).resolve()

    if not resolved_path.is_relative_to(resolved_root):
        raise RuntimeError(
            f"Refusing to reset path outside project root: "
            f"{resolved_path}"
        )

    return resolved_path


def _remove_file(
    relative_path: str,
    *,
    project_root: Path,
) -> bool:
    path = _resolve_runtime_path(
        relative_path,
        project_root=project_root,
    )

    if not path.exists():
        return False

    if not path.is_file():
        raise RuntimeError(
            f"Expected runtime file but found something else: "
            f"{path}"
        )

    path.unlink()

    return True


def _remove_directory(
    relative_path: str,
    *,
    project_root: Path,
) -> bool:
    path = _resolve_runtime_path(
        relative_path,
        project_root=project_root,
    )

    if not path.exists():
        return False

    if not path.is_dir():
        raise RuntimeError(
            f"Expected runtime directory but found something else: "
            f"{path}"
        )

    shutil.rmtree(path)

    return True


def reset_app_state(
    *,
    project_root: Path = PROJECT_ROOT,
) -> dict:
    if VECTOR_STORE != "local":
        raise RuntimeError(
            "App-state reset currently supports only "
            "VECTOR_STORE=local. Refusing to leave a "
            "remote vector store partially reset."
        )

    removed: list[str] = []

    if _remove_directory(
        COMPANY_ASSETS_DIRECTORY,
        project_root=project_root,
    ):
        removed.append(COMPANY_ASSETS_DIRECTORY)

    for relative_path in RUNTIME_DIRECTORIES:
        if _remove_directory(
            relative_path,
            project_root=project_root,
        ):
            removed.append(relative_path)

    for relative_path in RUNTIME_FILES:
        if _remove_file(
            relative_path,
            project_root=project_root,
        ):
            removed.append(relative_path)

    company_directory = (
        project_root
        / "data"
        / "company"
    )

    company_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    return {
        "status": "reset",
        "vector_store": VECTOR_STORE,
        "removed": removed,
        "preserved": [
            "data/examples",
            "data/answerly",
            "data/evals",
        ],
    }


def main() -> None:
    result = reset_app_state()

    print(
        json.dumps(
            result,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()