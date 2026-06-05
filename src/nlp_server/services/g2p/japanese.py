"""Japanese text to VITS-compatible phoneme pipeline.

OpenJTalk consumes punctuation during full-context extraction. GPT-SoVITS
preserves explicit pause/emotion marks by splitting on punctuation, running
prosody G2P on each text chunk, then stitching marks back before alignment.

Reference: GPT-SoVITS GPT_SoVITS/text/japanese.py preprocess_jap()
"""

import re
from typing import TypedDict

from nlp_server.services.g2p.constants.symbols2 import symbols
from nlp_server.services.g2p.utils.prosody_g2p import extract_prosody
from nlp_server.services.g2p.utils.symbol_alignment import align_to_vits_symbols

_SYMBOL_TO_ID = {symbol: index for index, symbol in enumerate(symbols)}

_japanese_characters = re.compile(
    r"[A-Za-z\d\u3005\u3040-\u30ff\u4e00-\u9fff\uff11-\uff19\uff21-\uff3a\uff41-\uff5a\uff66-\uff9d]"
)
_japanese_marks = re.compile(
    r"[^A-Za-z\d\u3005\u3040-\u30ff\u4e00-\u9fff\uff11-\uff19\uff21-\uff3a\uff41-\uff5a\uff66-\uff9d]"
)


class JapaneseTextInput(TypedDict):
    text: str
    phones: list[str]
    phone_ids: list[int]


def text_to_vits_phones(text: str) -> list[str]:
    """Split, stitch, and align Japanese text into VITS-compatible phonemes."""
    text = text.lower()

    sentences = re.split(_japanese_marks, text)
    marks = re.findall(_japanese_marks, text)

    raw_phones: list[str] = []

    for i, sentence in enumerate(sentences):
        if re.match(_japanese_characters, sentence):
            raw_phones.extend(extract_prosody(sentence))

        if i < len(marks):
            if marks[i] == " ":
                continue
            raw_phones.append(marks[i].replace(" ", ""))

    return align_to_vits_symbols(raw_phones)


def get_japanese_text_input(text: str) -> JapaneseTextInput:
    """Convert Japanese text to aligned phonemes and symbol IDs."""
    aligned_phones = text_to_vits_phones(text)

    phone_ids: list[int] = []
    for phone in aligned_phones:
        symbol_id = _SYMBOL_TO_ID.get(phone)
        if symbol_id is None:
            print(f"[Warning] Unknown symbol detected: {phone}")
            continue
        phone_ids.append(symbol_id)

    return {
        "text": text,
        "phones": aligned_phones,
        "phone_ids": phone_ids,
    }
