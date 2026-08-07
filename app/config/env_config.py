import os
from pathlib import Path

from dotenv import load_dotenv

from app.models.assistant_mode import AssistantMode


PROJECT_ROOT = Path(__file__).resolve().parents[2]

ENV_PATH = PROJECT_ROOT / ".env"
RUNTIME_ENV_PATH = PROJECT_ROOT / ".env.runtime"

load_dotenv(
    ENV_PATH,
    override=False,
)

if RUNTIME_ENV_PATH.is_file():
    load_dotenv(
        RUNTIME_ENV_PATH,
        override=True,
    )


class EnvironmentConfigurationError(RuntimeError):
    pass


def _parse_available_modes(
    raw_value: str | None,
) -> tuple[AssistantMode, ...]:
    if raw_value is None or not raw_value.strip():
        raise EnvironmentConfigurationError(
            "AVAILABLE_MODES must contain at least one "
            "assistant mode."
        )

    raw_modes = raw_value.split(",")

    if any(not value.strip() for value in raw_modes):
        raise EnvironmentConfigurationError(
            "AVAILABLE_MODES contains an empty value."
        )

    mode_names = [
        value.strip()
        for value in raw_modes
    ]

    if len(set(mode_names)) != len(mode_names):
        raise EnvironmentConfigurationError(
            "AVAILABLE_MODES must not contain duplicate modes."
        )

    available_modes: list[AssistantMode] = []

    for mode_name in mode_names:
        try:
            available_modes.append(
                AssistantMode(mode_name)
            )
        except ValueError as error:
            supported_modes = ", ".join(
                mode.value
                for mode in AssistantMode
            )

            raise EnvironmentConfigurationError(
                f"Unsupported assistant mode "
                f"'{mode_name}' in AVAILABLE_MODES. "
                f"Supported modes: {supported_modes}."
            ) from error

    return tuple(available_modes)


def _parse_vector_store(
    raw_value: str | None,
) -> str:
    vector_store = (
        raw_value or "local"
    ).strip().lower()

    if vector_store not in {
        "local",
        "supabase",
    }:
        raise EnvironmentConfigurationError(
            "VECTOR_STORE must be either "
            "'local' or 'supabase'."
        )

    return vector_store


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

DEFAULT_MODEL = (
    os.getenv(
        "DEFAULT_MODEL",
        "gpt-5-mini",
    ).strip()
    or "gpt-5-mini"
)

VECTOR_STORE = _parse_vector_store(
    os.getenv("VECTOR_STORE")
)

AVAILABLE_MODES = _parse_available_modes(
    os.getenv("AVAILABLE_MODES")
)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv(
    "SUPABASE_SERVICE_KEY"
)

if VECTOR_STORE == "supabase":
    missing_supabase_settings = [
        name
        for name, value in (
            ("SUPABASE_URL", SUPABASE_URL),
            (
                "SUPABASE_SERVICE_KEY",
                SUPABASE_SERVICE_KEY,
            ),
        )
        if not value
    ]

    if missing_supabase_settings:
        raise EnvironmentConfigurationError(
            "Missing required Supabase settings: "
            + ", ".join(missing_supabase_settings)
            + "."
        )