import argparse
import json

from app.config.company_config import load_company_config
from app.models.assistant_mode import AssistantMode
from app.services.mode_rebuild_service import (
    rebuild_mode_runtime,
)


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--mode",
        required=True,
        choices=[
            mode.value
            for mode in AssistantMode
        ],
    )

    arguments = parser.parse_args()

    company = load_company_config()
    mode = AssistantMode(arguments.mode)

    result = rebuild_mode_runtime(
        company_id=company["company_id"],
        mode=mode,
    )

    print(
        json.dumps(
            result,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()