from ollama import AsyncClient

from text_translator_server.config.settings import (
    LangCode,
    LANG_NAMES,
    TEXT_END_MARKER,
    TEXT_START_MARKER,
    TRANSLATE_MODEL,
    TRANSLATE_PROMPT,
)


def _sanitize_user_text(text: str) -> str:
    # Defuse any boundary marker the user might inject to "break out" of the
    # content section. Replacing with a visually similar but inert variant
    # preserves the user's intent without exposing the real markers.
    return text.replace(TEXT_END_MARKER, "<< END >>").replace(
        TEXT_START_MARKER, "<< TEXT >>"
    )


def _build_prompt(source: LangCode, target: LangCode, text: str) -> str:
    return TRANSLATE_PROMPT.format(
        SOURCE_LANG=LANG_NAMES[source],
        SOURCE_CODE=source,
        TARGET_LANG=LANG_NAMES[target],
        TARGET_CODE=target,
        START_MARKER=TEXT_START_MARKER,
        END_MARKER=TEXT_END_MARKER,
        TEXT=_sanitize_user_text(text),
    )


async def translate(
    client: AsyncClient,
    source: LangCode,
    target: LangCode,
    text: str,
) -> str:
    response = await client.chat(
        model=TRANSLATE_MODEL,
        messages=[{"role": "user", "content": _build_prompt(source, target, text)}],
    )

    translated_text = (response.message.content or "").strip()

    return translated_text


async def stop_model(client: AsyncClient) -> None:
    await client.generate(model=TRANSLATE_MODEL, keep_alive=0)
