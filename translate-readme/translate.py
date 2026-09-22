"""Translate a markdown file using DeepL API, preserving code blocks."""

import re
import sys
import httpx

DEEPL_URL = "https://api-free.deepl.com/v2/translate"  # paid: api.deepl.com

LANG_CODES = {"ja": "JA", "en": "EN"}

src_path, dst_path, target_lang = sys.argv[1], sys.argv[2], sys.argv[3]
api_key = sys.argv[4] if len(sys.argv) > 4 else __import__("os").environ["DEEPL_API_KEY"]

source = open(src_path).read()

# Extract code blocks and replace with placeholders to prevent translation
blocks: list[str] = []
placeholder_re = re.compile(r"(```[\s\S]*?```|`[^`]+`)", re.MULTILINE)

def replace_block(m: re.Match) -> str:
    blocks.append(m.group(0))
    return f"CODEBLOCK{len(blocks) - 1}END"

protected = placeholder_re.sub(replace_block, source)

resp = httpx.post(
    DEEPL_URL,
    headers={"Authorization": f"DeepL-Auth-Key {api_key}"},
    data={
        "text": protected,
        "target_lang": LANG_CODES.get(target_lang, target_lang.upper()),
        "preserve_formatting": "1",
    },
    timeout=30,
)
resp.raise_for_status()
translated = resp.json()["translations"][0]["text"]

# Restore code blocks
for i, block in enumerate(blocks):
    translated = translated.replace(f"CODEBLOCK{i}END", block)

open(dst_path, "w").write(translated)
print(f"Written: {dst_path}")
