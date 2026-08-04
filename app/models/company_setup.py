from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from app.models.assistant_mode import AssistantMode


class SetupRequestModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class AssistantSetupRequest(SetupRequestModel):
    name: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=100)
    mode: Literal["customer_support", "internal_knowledge"]
    default_language: str = Field(min_length=1, max_length=50)
    supported_languages: list[str] = Field(min_length=1)


class ConversationSetupRequest(SetupRequestModel):
    tone: Literal["friendly", "professional", "formal"]
    response_length: Literal["concise", "balanced", "detailed"]


class CompanyDetailsRequest(SetupRequestModel):
    description: str = Field(default="", max_length=2000)


class BrandingColorsRequest(SetupRequestModel):
    primary: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    secondary: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    accent: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    background: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    text: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")


class BrandingSetupRequest(SetupRequestModel):
    colors: BrandingColorsRequest

class BrandingSettingsUpdateRequest(SetupRequestModel):
    colors: BrandingColorsRequest

class CompanySetupRequest(SetupRequestModel):
    company_name: str = Field(min_length=1, max_length=150)
    industry: str = Field(min_length=1, max_length=150)
    assistant: AssistantSetupRequest
    conversation: ConversationSetupRequest
    company_details: CompanyDetailsRequest
    branding: BrandingSetupRequest

class CompanySettingsUpdateRequest(SetupRequestModel):
    company_name: str = Field(min_length=1, max_length=150)
    industry: str = Field(min_length=1, max_length=150)
    assistant: AssistantSetupRequest
    conversation: ConversationSetupRequest
    company_details: CompanyDetailsRequest

class AssistantProfileSettingsRequest(SetupRequestModel):
    name: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=100)
    default_language: str = Field(
        min_length=1,
        max_length=50,
    )
    supported_languages: list[str] = Field(
        min_length=1,
        max_length=20,
    )


class GreetingSettingsRequest(SetupRequestModel):
    enabled: bool
    message: str = Field(max_length=500)


class ModeConversationSettingsRequest(SetupRequestModel):
    tone: Literal[
        "friendly",
        "professional",
        "formal",
    ]
    response_length: Literal[
        "concise",
        "balanced",
        "detailed",
    ]
    greeting: GreetingSettingsRequest


class ModeChatSettingsRequest(SetupRequestModel):
    chat_headline: str = Field(
        min_length=1,
        max_length=150,
    )
    chat_description: str = Field(
        min_length=1,
        max_length=500,
    )
    placeholder: str = Field(
        min_length=1,
        max_length=150,
    )
    loading_message: str = Field(
        min_length=1,
        max_length=250,
    )
    fallback_message: str = Field(
        min_length=1,
        max_length=1000,
    )


class AssistantModeSettingsUpdateRequest(
    SetupRequestModel
    ):
    display_name: str = Field(
        min_length=1,
        max_length=150,
    )
    assistant: AssistantProfileSettingsRequest
    conversation: ModeConversationSettingsRequest
    chat: ModeChatSettingsRequest
    prompt_guide: str = Field(
        default="",
        max_length=10_000,
    )
    show_citations: bool

class AssistantModesUpdateRequest(SetupRequestModel):
    enabled_modes: list[AssistantMode] = Field(
        min_length=1,
        max_length=len(AssistantMode),
    )
    default_mode: AssistantMode

    @model_validator(mode="after")
    def validate_mode_selection(self):
        unique_modes = set(self.enabled_modes)

        if len(unique_modes) != len(self.enabled_modes):
            raise ValueError(
                "Enabled assistant modes must not contain duplicates."
            )

        if self.default_mode not in unique_modes:
            raise ValueError(
                "The default assistant mode must be enabled."
            )

        return self