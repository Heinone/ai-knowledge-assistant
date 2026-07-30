import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]

ANSWERLY_BRANDING_PATH = (
    PROJECT_ROOT
    / "data"
    / "answerly"
    / "branding.json"
)


def load_answerly_branding() -> dict[str, Any]:
    if not ANSWERLY_BRANDING_PATH.is_file():
        raise FileNotFoundError(
            "Answer.ly branding configuration was not found."
        )

    with ANSWERLY_BRANDING_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)