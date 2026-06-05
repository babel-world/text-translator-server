"""从全语境标签提取日语音素与韵律符号（`[` `]` `#` 等）。

算法源自 ESPnet phoneme_tokenizer.py 的 pyopenjtalk_g2p_prosody：
https://github.com/espnet/espnet/blob/master/espnet2/text/phoneme_tokenizer.py

依赖 pyopenjtalk-plus 提供 OpenJTalk 前端。
"""

import re

import pyopenjtalk


def _numeric_feature_by_regex(regex: str, s: str) -> int:
    match = re.search(regex, s)
    if match is None:
        return -50
    return int(match.group(1))


def extract_prosody(text: str, drop_unvoiced_vowels: bool = True) -> list[str]:
    """从日语文本提取音素序列，并插入韵律标记。

    Args:
        text: 日语文本（建议含句读如 。 以得到 sil 边界）
        drop_unvoiced_vowels: 将无声音素 AEIOU 转为小写

    Returns:
        音素与韵律符号列表，例如 ['^', 'k', 'o', '[', 'N', 'n', 'i', 'ch', 'i', 'w', 'a', '$']
    """
    labels = pyopenjtalk.extract_fullcontext(text)
    n_labels = len(labels)
    phones: list[str] = []

    for n in range(n_labels):
        lab_curr = labels[n]
        p3_match = re.search(r"\-(.*?)\+", lab_curr)
        if p3_match is None:
            continue
        p3 = p3_match.group(1)

        if drop_unvoiced_vowels and p3 in "AEIOU":
            p3 = p3.lower()

        if p3 == "sil":
            if n == 0:
                phones.append("^")
            elif n == n_labels - 1:
                e3 = _numeric_feature_by_regex(r"!(\d+)_", lab_curr)
                if e3 == 0:
                    phones.append("$")
                elif e3 == 1:
                    phones.append("?")
            continue
        if p3 == "pau":
            phones.append("_")
            continue

        phones.append(p3)

        a1 = _numeric_feature_by_regex(r"/A:([0-9\-]+)\+", lab_curr)
        a2 = _numeric_feature_by_regex(r"\+(\d+)\+", lab_curr)
        a3 = _numeric_feature_by_regex(r"\+(\d+)/", lab_curr)
        f1 = _numeric_feature_by_regex(r"/F:(\d+)_", lab_curr)
        a2_next = _numeric_feature_by_regex(r"\+(\d+)\+", labels[n + 1])

        if a3 == 1 and a2_next == 1 and p3 in "aeiouAEIOUNcl":
            phones.append("#")
        elif a1 == 0 and a2_next == a2 + 1 and a2 != f1:
            phones.append("]")
        elif a2 == 1 and a2_next == 2:
            phones.append("[")

    return phones
