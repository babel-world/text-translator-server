# G2P 模块（`services/g2p`）

日语 G2P 语言学能力黑盒。对外仅暴露 `g2p_ja(text, mode)`。

## Public API

```python
from nlp_server.services.g2p import g2p_ja

phones = g2p_ja("こんにちは。", mode="default")
phones = g2p_ja("こんにちは。", mode="prosody")
```

HTTP：`POST /api/g2p/ja`

## 目录结构

```text
services/g2p/
├── __init__.py       # g2p_ja 门面
├── ja/
│   ├── default.py    # extract() -> pyopenjtalk.g2p
│   └── prosody.py    # extract_prosody() -> 韵律符号
├── zh/               # 预留
└── en/               # 预留
```

## mode 语义

| mode | 函数 | 输出特征 |
|------|------|----------|
| `default` | `extract` | 纯音素，无 `^` `$` `[` `]` |
| `prosody` | `extract_prosody` | 含 OpenJTalk/ESPnet 韵律符号 |

## 不在本模块职责内

- symbols2 词表对齐、manifest CSV、隐私过滤
- 标点 split-stitch、训练格式导出

上述胶水代码已归档至 `.local/g2p/`，由 Prefect 等外部项目负责。
