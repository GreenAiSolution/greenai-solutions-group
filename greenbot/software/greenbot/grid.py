"""Occupancy grid. 0 = free, 1 = obstacle, 2 = cliff/no-go. Cleaned state tracked separately."""
FREE, OBSTACLE, NOGO = 0, 1, 2


class Grid:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.cells = [[FREE] * w for _ in range(h)]
        self.cleaned = [[False] * w for _ in range(h)]

    def inside(self, x, y):
        return 0 <= x < self.w and 0 <= y < self.h

    def set(self, x, y, v):
        if self.inside(x, y):
            self.cells[y][x] = v

    def passable(self, x, y):
        return self.inside(x, y) and self.cells[y][x] == FREE

    def mark_cleaned(self, x, y):
        if self.inside(x, y):
            self.cleaned[y][x] = True

    def coverage(self):
        free = done = 0
        for y in range(self.h):
            for x in range(self.w):
                if self.cells[y][x] == FREE:
                    free += 1
                    done += self.cleaned[y][x]
        return done / free if free else 1.0

    @classmethod
    def from_ascii(cls, rows):
        g = cls(len(rows[0]), len(rows))
        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                g.cells[y][x] = {"#": OBSTACLE, "X": NOGO}.get(ch, FREE)
        return g
