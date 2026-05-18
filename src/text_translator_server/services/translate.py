from ollama import AsyncClient

from text_translator_server.config.index import (
    LANG_CODE,
    LANG_NAMES,
    TRANSLATE_MODEL,
    TRANSLATE_PROMPT,
)

client = AsyncClient(host="http://127.0.0.1:11434")


def _build_prompt(source: LANG_CODE, target: LANG_CODE, text: str) -> str:
    return TRANSLATE_PROMPT.format(
        SOURCE_LANG=LANG_NAMES[source],
        SOURCE_CODE=source,
        TARGET_LANG=LANG_NAMES[target],
        TARGET_CODE=target,
        TEXT=text,
    )


async def translate(source: LANG_CODE, target: LANG_CODE, text: str) -> str:
    response = await client.chat(
        model=TRANSLATE_MODEL,
        messages=[{"role": "user", "content": _build_prompt(source, target, text)}],
    )

    translated_text = (response.message.content or "").strip()

    return translated_text
