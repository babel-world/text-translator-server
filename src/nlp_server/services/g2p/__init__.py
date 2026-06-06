from typing import Literal

from nlp_server.services.g2p.ja.default import extract
from nlp_server.services.g2p.ja.prosody import extract_prosody

JaG2pMode = Literal["default", "prosody"]


def g2p_ja(text: str, mode: JaG2pMode = "default") -> list[str]:
    """Convert Japanese text to a phoneme list."""
    if mode == "prosody":
        return extract_prosody(text)
    return extract(text)
