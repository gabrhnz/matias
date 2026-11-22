"""Siguiente práctica de una lección.

Cada lección tiene prácticas fáciles, una normal y una difícil.
Con cuatro prácticas, las dos primeras son fáciles, la tercera es normal
y la última es difícil.

1. Se empieza por la normal.
2. Dos errores seguidos: la siguiente es la más fácil que todavía no salió.
3. Tres aciertos seguidos: la siguiente es la más difícil que todavía no salió.
4. En otro caso: una que no sea más difícil que la última.
"""

from __future__ import annotations


def levels_for(count: int) -> list[int]:
    levels = [1] * count
    if count == 0:
        return levels
    levels[-1] = 3
    if count >= 3:
        levels[-2] = 2
    elif count == 2:
        levels[0] = 2
    else:
        levels[0] = 2
    return levels


def opening_index(levels: list[int]) -> int:
    for index, level in enumerate(levels):
        if level == 2:
            return index
    return 0


def _runs(results: list[bool]) -> tuple[int, int]:
    if not results:
        return 0, 0
    if results[-1]:
        streak = 0
        for item in reversed(results):
            if not item:
                break
            streak += 1
        return streak, 0
    streak = 0
    for item in reversed(results):
        if item:
            break
        streak += 1
    return 0, streak


def next_index(levels: list[int], shown: list[int], results: list[bool]) -> int | None:
    if len(shown) >= len(levels):
        return None
    used = set(shown)
    remaining = [index for index in range(len(levels)) if index not in used]
    if not remaining:
        return None
    if not shown:
        return opening_index(levels)
    right, wrong = _runs(results)
    if wrong >= 2:
        return min(remaining, key=lambda index: (levels[index], index))
    if right >= 3:
        return max(remaining, key=lambda index: (levels[index], index))
    last_level = levels[shown[-1]]
    easier = [index for index in remaining if levels[index] <= last_level]
    pool = easier or remaining
    return min(pool, key=lambda index: (abs(levels[index] - last_level), levels[index], index))
