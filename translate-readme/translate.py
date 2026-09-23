"""Translate a markdown file using DeepL API, preserving code blocks."""

import os
import re
import sys
import httpx

DEEPL_URL = "https://api-free.deepl.com/v2/translate"  # paid: api.deepl.com

LANG_CODES = {"ja": "JA", "en": "EN"}

src_path, dst_path, target_lang = sys.argv[1], sys.argv[2], sys.argv[3]
api_key = sys.argv[4] if len(sys.argv) > 4 else os.environ["DEEPL_API_KEY"]

source = open(src_path).read()

# The language-switcher line (e.g. "**English** | [日本語](README.ja.md)") needs to be
# reversed, not translated — DeepL would translate "English" as text and leave the
# link pointing at itself. Strip it and rebuild it pointing back at the source file.
switcher_re = re.compile(r"^\*\*(.+?)\*\* \| \[(.+?)\]\(.+?\)\s*\n+")
switcher_match = switcher_re.match(source)
switcher_line_out = None
if switcher_match:
    source_label, target_label = switcher_match.groups()
    switcher_line_out = f"[{source_label}]({os.path.basename(src_path)}) | **{target_label}**"
    source = source[switcher_match.end():]

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

if switcher_line_out:
    translated = f"{switcher_line_out}\n\n{translated.lstrip(chr(13) + chr(10))}"

open(dst_path, "w").write(translated)
print(f"Written: {dst_path}")
