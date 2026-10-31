"""Casos de prueba reproducibles para comparar algoritmos de 8-puzzle."""

from typing import Callable, Dict

from mapa import Estado, Puzzle


OBJETIVO: Estado = (1, 2, 3, 4, 5, 6, 7, 8, 0)


def puzzle_facil() -> Puzzle:
    """Estado que requiere pocos movimientos y permite una demostración rápida."""
    return Puzzle((1, 2, 3, 4, 5, 6, 0, 7, 8), OBJETIVO)


def puzzle_medio() -> Puzzle:
    """Estado con suficiente profundidad para diferenciar las búsquedas."""
    return Puzzle((1, 3, 6, 5, 0, 2, 4, 7, 8), OBJETIVO)


def puzzle_dificil() -> Puzzle:
    """Estado válido que requiere una búsqueda más amplia."""
    return Puzzle((7, 2, 4, 5, 0, 6, 8, 3, 1), OBJETIVO)


def puzzle_sin_solucion() -> Puzzle:
    """Estado imposible: intercambiar dos fichas cambia la paridad."""
    return Puzzle((1, 2, 3, 4, 5, 6, 8, 7, 0), OBJETIVO)


PUZZLES: Dict[str, Callable[[], Puzzle]] = {
    "8-puzzle fácil": puzzle_facil,
    "8-puzzle medio": puzzle_medio,
    "8-puzzle difícil": puzzle_dificil,
    "8-puzzle sin solución": puzzle_sin_solucion,
}
