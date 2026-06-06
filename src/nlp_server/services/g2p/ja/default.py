import pyopenjtalk


def extract(text: str) -> list[str]:
    """Extract basic Japanese phonemes via pyopenjtalk.g2p."""
    return pyopenjtalk.g2p(text).split()
