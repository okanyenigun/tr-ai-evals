"""Structured-output schemas. Never edit a published class; add a new version."""

from enum import Enum
from pydantic import BaseModel, Field


class ChoiceEnum(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"


class ModelAnswerV1(BaseModel):
    id: str = Field(description="Sorunun benzersiz tanımlayıcısı, ID.")
    code: ChoiceEnum = Field(description="Sorunun doğru cevap kodu.")


class ModelAnswerV2(BaseModel):
    id: str = Field(description="Sorunun benzersiz tanımlayıcısı, ID.")
    code: ChoiceEnum = Field(description="Sorunun doğru cevap kodu.")
    explanation: str = Field(description="Doğru cevabın kısa açıklaması.")


SCHEMAS: dict[tuple[str, str], type[BaseModel]] = {
    ("tr_uni_exam_answer", "v1"): ModelAnswerV1,
    ("tr_uni_exam_answer", "v2"): ModelAnswerV2,
}
