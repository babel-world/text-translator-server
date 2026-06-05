from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from nlp_server.config.settings import LangCode


class TranslateRequestBody(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        json_schema_extra={
            "examples": [
                {
                    "sourceLang": "en",
                    "targetLang": "zh",
                    "sourceText": "Hello, world! This is a test translation.",
                }
            ]
        },
    )

    source_lang: LangCode = Field(description="Source language code (e.g., 'en', 'zh', 'ja')")
    target_lang: LangCode = Field(description="Target language code (e.g., 'en', 'zh', 'ja')")
    source_text: str = Field(
        min_length=1, 
        max_length=2048,
        description="The text to be translated. Maximum 2048 characters."
    )


class TranslateResponseBody(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True, 
        alias_generator=to_camel,
        json_schema_extra={
            "examples": [
                {
                    "translatedText": "你好，世界！这是一次测试翻译。",
                }
            ]
        },
    )

    translated_text: str = Field(description="The resulting translated text")
