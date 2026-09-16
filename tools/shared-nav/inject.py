#!/usr/bin/env python3
"""Replace the shared nav (inner) and footer in the given pages with _build/nav.html and _build/footer.html.
The page keeps its own <nav ...> opening tag (transparent vs solid)."""
import re,sys,pathlib
here=pathlib.Path(__file__).parent
NAV=here.joinpath('nav.html').read_text(); FOOT=here.joinpath('footer.html').read_text()
for f in sys.argv[1:]:
    p=pathlib.Path(f); s=p.read_text(); o=s
    s=re.sub(r'(<nav class="nav[^>]*>).*?</nav>', lambda m: m.group(1)+'\n'+NAV.rstrip('\n')+'\n  </nav>', s, count=1, flags=re.S)
    s=re.sub(r'  <footer class="footer"[^>]*>.*?</footer>', FOOT.rstrip('\n'), s, count=1, flags=re.S)
    if s==o: print('  UNCHANGED', f)
    else: p.write_text(s); print('  ok', f)
