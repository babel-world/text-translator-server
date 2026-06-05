from typing import Final, Literal

G2pStatus = Literal["ok", "skip", "error"]

INPUT_COLUMNS: Final[tuple[str, ...]] = (
    "filename",
    "speaker",
    "language",
    "text",
    "probability",
)

G2P_COLUMNS: Final[tuple[str, ...]] = (
    "norm_text",
    "phones",
    "phone_count",
    "word2ph",
    "status",
    "error",
)

OUTPUT_COLUMNS: Final[tuple[str, ...]] = INPUT_COLUMNS + G2P_COLUMNS

PRIVACY_ALLOWED_LANGUAGE: Final[str] = "ja"
PRIVACY_MIN_PROBABILITY: Final[float] = 0.95
