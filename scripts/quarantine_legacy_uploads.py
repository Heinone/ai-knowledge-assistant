import argparse
import hashlib
import shutil
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

UPLOAD_ROOT = PROJECT_ROOT / "data" / "uploads"

MODE_DIRECTORIES = (
    UPLOAD_ROOT / "customer_support",
    UPLOAD_ROOT / "internal_knowledge",
)

DUPLICATE_ARCHIVE = (
    PROJECT_ROOT
    / "data"
    / "archive"
    / "legacy_upload_duplicates"
)

UNASSIGNED_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "migration"
    / "unassigned_uploads"
)


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def unique_destination(
    directory: Path,
    filename: str,
) -> Path:
    destination = directory / filename

    if not destination.exists():
        return destination

    source_path = Path(filename)
    counter = 2

    while True:
        candidate = directory / (
            f"{source_path.stem}_{counter}"
            f"{source_path.suffix}"
        )

        if not candidate.exists():
            return candidate

        counter += 1


def move_file(
    source: Path,
    destination_directory: Path,
) -> Path:
    destination_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination = unique_destination(
        destination_directory,
        source.name,
    )

    shutil.move(
        str(source),
        str(destination),
    )

    return destination


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Quarantine legacy root-level uploads without "
            "deleting any files."
        )
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Move files. Without this flag, only show the plan.",
    )

    arguments = parser.parse_args()

    mode_files = [
        path
        for mode_directory in MODE_DIRECTORIES
        if mode_directory.is_dir()
        for path in mode_directory.rglob("*")
        if path.is_file()
    ]

    mode_hashes = {
        file_digest(path)
        for path in mode_files
    }

    legacy_files = sorted(
        path
        for path in UPLOAD_ROOT.iterdir()
        if path.is_file()
    )

    duplicates = []
    unassigned = []

    for legacy_file in legacy_files:
        if file_digest(legacy_file) in mode_hashes:
            duplicates.append(legacy_file)
        else:
            unassigned.append(legacy_file)

    print(
        {
            "legacy_files": len(legacy_files),
            "duplicate_files": len(duplicates),
            "unassigned_files": len(unassigned),
            "apply": arguments.apply,
        }
    )

    print("\nDuplicate legacy files:")

    for file_path in duplicates:
        print(f"  {file_path.relative_to(PROJECT_ROOT)}")

    print("\nUnassigned legacy files:")

    for file_path in unassigned:
        print(f"  {file_path.relative_to(PROJECT_ROOT)}")

    if not arguments.apply:
        print(
            "\nDry run only. Run again with --apply "
            "to move the files."
        )
        return

    for file_path in duplicates:
        destination = move_file(
            file_path,
            DUPLICATE_ARCHIVE,
        )

        print(
            "Archived duplicate: "
            f"{destination.relative_to(PROJECT_ROOT)}"
        )

    for file_path in unassigned:
        destination = move_file(
            file_path,
            UNASSIGNED_DIRECTORY,
        )

        print(
            "Quarantined unassigned file: "
            f"{destination.relative_to(PROJECT_ROOT)}"
        )

    print("\nLegacy upload quarantine completed.")


if __name__ == "__main__":
    main()