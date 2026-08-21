#!/usr/bin/env python3
"""Regenerate MAVEN's voice clips for call.html.

Reads the LINES block out of call.html (single source of truth) and renders
one mp3 per line with Microsoft Edge's free neural TTS (pip install edge-tts).
Run whenever a line in call.html changes:

    SSL_CERT_FILE=$(python3 -c "import certifi;print(certifi.where())") \
        python3 voice/gen_voice.py

$0 to generate, $0 to serve — the clips are static files on GitHub Pages.
"""
import asyncio, os, re, sys

VOICE = "en-US-JennyNeural"   # warm, natural US female — MAVEN's voice
RATE  = "+4%"                 # a touch quicker than default; reads as alert

HERE = os.path.dirname(os.path.abspath(__file__))
CALL = os.path.join(HERE, "..", "call.html")

def read_lines():
    src = open(CALL, encoding="utf-8").read()
    block = re.search(r"var LINES = \{(.*?)\n    \};", src, re.S)
    if not block:
        sys.exit("LINES block not found in call.html")
    # the |$ matters: the last entry has no trailing newline inside the block
    pairs = re.findall(r"'([\w-]+)':\s*\"(.*?)\",?\s*(?:/\*|\n|$)", block.group(1))
    if len(pairs) < 30:
        sys.exit(f"only parsed {len(pairs)} lines — check the regex")
    return dict(pairs)

async def render(lines):
    import edge_tts
    for lid, text in lines.items():
        out = os.path.join(HERE, f"{lid}.mp3")
        # em dashes read as pauses when written as commas; strip markup-ish bits
        spoken = text.replace("—", ",").replace("A.I.", "A I")
        tts = edge_tts.Communicate(spoken, VOICE, rate=RATE)
        await tts.save(out)
        print(f"{lid}.mp3  {os.path.getsize(out)//1024}KB  {text[:56]}")

if __name__ == "__main__":
    lines = read_lines()
    print(f"{len(lines)} lines -> {VOICE} rate {RATE}")
    asyncio.run(render(lines))
    total = sum(os.path.getsize(os.path.join(HERE, f)) for f in os.listdir(HERE) if f.endswith(".mp3"))
    print(f"total audio: {total//1024}KB")
