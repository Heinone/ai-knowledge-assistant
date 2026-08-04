from enum import Enum


class AssistantMode(str, Enum):
    CUSTOMER_SUPPORT = "customer_support"
    INTERNAL_KNOWLEDGE = "internal_knowledge"