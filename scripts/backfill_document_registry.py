import json

from app.config.company_config import load_company_config
from app.services.document_backfill_service import (
    backfill_document_registry,
)


def main() -> None:
    company = load_company_config()

    result = backfill_document_registry(
        company_id=company["company_id"],
    )

    print(
        json.dumps(
            result,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()