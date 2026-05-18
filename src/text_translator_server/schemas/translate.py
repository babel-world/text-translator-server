from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from text_translator_server.config.index import LANG_CODE


class TranslateRequestBody(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    source_lang: LANG_CODE
    target_lang: LANG_CODE
    source_text: str = Field(min_length=1, max_length=2048)


class TranslateResponseBody(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    translated_text: str = Field(min_length=1, max_length=2048)
