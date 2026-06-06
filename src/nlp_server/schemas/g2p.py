from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

JaG2pMode = Literal["default", "prosody"]


class JaG2pRequestBody(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        json_schema_extra={
            "examples": [
                {
                    "text": "こんにちは。",
                    "mode": "default",
                }
            ]
        },
    )

    text: str = Field(min_length=1, description="Japanese text to convert to phonemes")
    mode: JaG2pMode = Field(
        default="default",
        description="G2P mode: default (basic phonemes) or prosody (with ^ $ [ ] etc.)",
    )


class JaG2pResponseBody(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        json_schema_extra={
            "examples": [
                {
                    "phones": ["k", "o", "N", "n", "i", "ch", "i", "w", "a"],
                }
            ]
        },
    )

    phones: list[str] = Field(description="Phoneme token list")
