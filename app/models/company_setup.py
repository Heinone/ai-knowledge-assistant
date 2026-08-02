from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


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


class CompanySetupRequest(SetupRequestModel):
    company_name: str = Field(min_length=1, max_length=150)
    industry: str = Field(min_length=1, max_length=150)
    assistant: AssistantSetupRequest
    conversation: ConversationSetupRequest
    company_details: CompanyDetailsRequest
    branding: BrandingSetupRequest