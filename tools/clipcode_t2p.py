"""text -> svg path d using fontTools. usage: path_for(font, text, size, x, y, tracking_em, wght=None)"""
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

_cache = {}
def load(path, wght=None):
    key = (path, wght)
    if key in _cache: return _cache[key]
    f = TTFont(path)
    if wght is not None and 'fvar' in f:
        from fontTools.varLib.instancer import instantiateVariableFont
        f = instantiateVariableFont(f, {'wght': wght})
    _cache[key] = f
    return f

def path_for(fontpath, text, size, x=0, y=0, tracking=0.0, wght=None):
    f = load(fontpath, wght)
    upm = f['head'].unitsPerEm
    gs = f.getGlyphSet(); cmap = f.getBestCmap(); hmtx = f['hmtx']
    s = size / upm
    pen = SVGPathPen(gs)
    cx = 0.0
    for ch in text:
        g = cmap[ord(ch)]
        tp = TransformPen(pen, (s, 0, 0, -s, x + cx, y))
        gs[g].draw(tp)
        cx += hmtx[g][0] * s + tracking * size
    return pen.getCommands(), cx - tracking * size

if __name__ == '__main__':
    import sys
    d, w = path_for(sys.argv[1], sys.argv[2], 100)
    print(w)
