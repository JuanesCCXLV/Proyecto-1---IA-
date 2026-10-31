"""Modelo del estado de un 8-puzzle con costos por ficha."""

from typing import Iterable, Optional, Tuple


Estado = Tuple[int, ...]


class Puzzle:
    """Representa un 8-puzzle y sus estados inicial y objetivo.

    El valor ``0`` representa el espacio vacío. Una acción desliza una
    ficha adyacente hacia el espacio vacío.

    Costo de las acciones: mover una ficha cuesta el número de esa ficha
    (mover el 1 cuesta 1, mover el 8 cuesta 8). Así los costos no son todos
    iguales y la solución con menos movimientos no siempre es la más barata,
    lo que permite diferenciar BFS de la búsqueda de costo uniforme y A*.
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
        """Genera los estados que se obtienen moviendo una ficha.

        El espacio vacío se intercambia con la ficha de arriba, abajo,
        izquierda o derecha, siempre que exista dentro del tablero.
        """
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

    @staticmethod
    def ficha_movida(estado: Estado, siguiente: Estado) -> int:
        """Devuelve la ficha que se desliza al pasar de ``estado`` a ``siguiente``.

        La ficha movida ocupa, en ``siguiente``, la casilla donde estaba el
        espacio vacío en ``estado``.
        """
        return siguiente[estado.index(0)]

    def costo_movimiento(self, estado: Estado, siguiente: Estado) -> int:
        """Costo de la acción: el número de la ficha que se mueve (1 a 8)."""
        return self.ficha_movida(estado, siguiente)

    def costo_camino(self, camino: list) -> int:
        """Suma los costos de todas las acciones de un camino."""
        return sum(
            self.costo_movimiento(actual, siguiente)
            for actual, siguiente in zip(camino, camino[1:])
        )

    def imprimir(self, estado: Optional[Estado] = None) -> None:
        """Imprime un estado del tablero."""
        estado = estado or self.inicio

        for fila in range(self.ANCHO):
            valores = estado[fila * self.ANCHO:(fila + 1) * self.ANCHO]
            print(" ".join("_" if valor == 0 else str(valor) for valor in valores))
