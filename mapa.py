"""Modelo del estado de un 8-puzzle."""

from typing import Iterable, List, Optional, Tuple


Estado = Tuple[int, ...]


class Puzzle:
    """Representa un 8-puzzle y sus estados inicial y objetivo.

    El valor ``0`` representa el espacio vacío. Cada movimiento tiene
    costo 1, por lo que el problema es adecuado para comparar DFS, BFS,
    búsqueda de costo uniforme y A*.
    """

    ANCHO = 3

    def __init__(self, inicial: Estado, objetivo: Estado) -> None:
        if len(inicial) != 9 or len(objetivo) != 9:
            raise ValueError("Cada estado debe tener exactamente 9 valores.")
        if set(inicial) != set(range(9)) or set(objetivo) != set(range(9)):
            raise ValueError("Los estados deben contener los valores del 0 al 8.")

        self.inicio = inicial
        self.objetivo = objetivo

    def vecinos(self, estado: Estado) -> Iterable[Estado]:
        """Genera los estados que se obtienen moviendo una ficha."""
        posicion_vacio = estado.index(0)
        fila, columna = divmod(posicion_vacio, self.ANCHO)
        desplazamientos = ((-1, 0), (1, 0), (0, -1), (0, 1))

        for desplazamiento_fila, desplazamiento_columna in desplazamientos:
            nueva_fila = fila + desplazamiento_fila
            nueva_columna = columna + desplazamiento_columna

            if 0 <= nueva_fila < self.ANCHO and 0 <= nueva_columna < self.ANCHO:
                nueva_posicion = nueva_fila * self.ANCHO + nueva_columna
                siguiente = list(estado)
                siguiente[posicion_vacio], siguiente[nueva_posicion] = (
                    siguiente[nueva_posicion],
                    siguiente[posicion_vacio],
                )
                yield tuple(siguiente)

    def costo_movimiento(self, estado: Estado) -> int:
        """Retorna el costo de llegar a cualquier estado sucesor."""
        return 1

    def imprimir(self, estado: Optional[Estado] = None) -> None:
        """Imprime un estado del tablero."""
        estado = estado or self.inicio

        for fila in range(self.ANCHO):
            valores = estado[fila * self.ANCHO:(fila + 1) * self.ANCHO]
            print(" ".join(" " if valor == 0 else str(valor) for valor in valores))
