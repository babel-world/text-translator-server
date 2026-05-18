from typing import Final, Literal

LANG_CODE = Literal["zh", "en", "ja"]

LANG_NAMES: Final[dict[LANG_CODE, str]] = {
    "zh": "Chinese",
    "en": "English",
    "ja": "Japanese",
}

TRANSLATE_PROMPT = """
You are a professional {SOURCE_LANG} ({SOURCE_CODE}) to {TARGET_LANG} ({TARGET_CODE}) translator. Your goal is to accurately convey the meaning and nuances of the original {SOURCE_LANG} text while adhering to {TARGET_LANG} grammar, vocabulary, and cultural sensitivities.
Produce only the {TARGET_LANG} translation, without any additional explanations or commentary. Please translate the following {SOURCE_LANG} text into {TARGET_LANG}:


{TEXT}
"""

TRANSLATE_MODEL = "translategemma:latest"
