"""Boustrophedon (lawn-mower) coverage with BFS detours around obstacles."""
from collections import deque


def _bfs(grid, start, goal):
    prev, q = {start: None}, deque([start])
    while q:
        cur = q.popleft()
        if cur == goal:
            path = []
            while cur:
                path.append(cur)
                cur = prev[cur]
            return path[::-1][1:]
        x, y = cur
        for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if n not in prev and grid.passable(*n):
                prev[n] = cur
                q.append(n)
    return None


def plan_coverage(grid, start):
    """Return ordered list of (x, y) cells visiting every reachable free cell."""
    order = []
    for x in range(grid.w):
        ys = range(grid.h) if x % 2 == 0 else range(grid.h - 1, -1, -1)
        order += [(x, y) for y in ys if grid.passable(x, y)]
    path, pos = [], start
    for cell in order:
        if cell == pos:
            continue
        if abs(cell[0] - pos[0]) + abs(cell[1] - pos[1]) == 1:
            path.append(cell)
        else:
            detour = _bfs(grid, pos, cell)
            if detour is None:
                continue  # unreachable pocket
            path += detour
        pos = cell
    return path
