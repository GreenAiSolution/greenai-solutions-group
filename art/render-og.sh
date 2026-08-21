#!/bin/sh
# Rebuilds og-card.jpg (1200x630) from art/og-card.src.html.
#
# Why it is not a plain screenshot: headless Chrome on macOS reports a viewport
# ~87px shorter than --window-size and clamps windows to a 500px minimum width,
# so the raw PNG is never the size you asked for. We render the card as
# 100vw x 100vh at 2x, detect where the card ends (first all-white row from the
# bottom), crop to that, then resize to exactly 1200x630.
#
# Usage:  cd ~/greenai-solutions-group && sh art/render-og.sh
set -e
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PORT=8299
python3 -m http.server $PORT >/dev/null 2>&1 &
SRV=$!
trap 'kill $SRV 2>/dev/null' EXIT
sleep 1
TMP=$(mktemp -d)
"$CHROME" --headless=old --disable-gpu --hide-scrollbars \
  --force-device-scale-factor=2 --window-size=1200,717 --virtual-time-budget=9000 \
  --screenshot="$TMP/raw.png" "http://localhost:$PORT/art/og-card.src.html" 2>/dev/null
python3 - "$TMP/raw.png" <<'PY'
import sys
from PIL import Image
im = Image.open(sys.argv[1]).convert('RGB'); W, H = im.size; px = im.load()
white = lambda y: all(sum(px[x, y]) > 735 for x in range(0, W, W // 24))
bottom = next((y + 1 for y in range(H - 1, -1, -1) if not white(y)), H)
im.crop((0, 0, W, bottom)).resize((1200, 630), Image.LANCZOS) \
  .save('og-card.jpg', quality=88, optimize=True, progressive=True)
print('og-card.jpg written from a', W, 'x', bottom, 'render')
PY
