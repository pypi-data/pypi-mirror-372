from enum import Enum

from pydantic import BaseModel


class PromptTemplateType(str, Enum):
    AI_SYSTEM = "ai_system"
    JUDGE = "judge"


class PromptTemplate(BaseModel):
    prompt_template_type: PromptTemplateType
    template: str
