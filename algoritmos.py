"""Algoritmos de búsqueda para resolver el 8-puzzle con costos por ficha.

Todos los algoritmos devuelven el mismo diccionario de resultados:

- ``camino``: lista de estados desde el inicial hasta el objetivo.
- ``costo_total``: suma de los costos de las acciones del camino.
- ``longitud_camino``: cantidad de movimientos (profundidad de la solución).
- ``nodos_expandidos``: estados sacados de la frontera y procesados.
- ``memoria``: estados distintos almacenados (frontera + alcanzados).
- ``max_frontera``: tamaño máximo que alcanzó la frontera.
- ``tiempo_ejecucion_ms``: tiempo de ejecución en milisegundos.
- ``encontrado``: indica si se encontró una solución.
"""

from collections import deque
import heapq
import time
from typing import Callable, Dict, List, Optional

from mapa import Estado, Puzzle


Resultado = Dict[str, object]
Heuristica = Callable[[Estado, Estado], int]
INFINITO = float("inf")


def reconstruir_camino(
    predecesor: Dict[Estado, Optional[Estado]],
    objetivo: Estado,
) -> List[Estado]:
    """Reconstruye la secuencia de estados desde el inicio."""
    camino = []
    actual: Optional[Estado] = objetivo

    while actual is not None:
        camino.append(actual)
        actual = predecesor[actual]

    camino.reverse()
    return camino


def construir_resultado(
    puzzle: Puzzle,
    camino: Optional[List[Estado]],
    nodos_expandidos: int,
    memoria: int,
    max_frontera: int,
    inicio_tiempo: float,
) -> Resultado:
    """Crea el formato común de resultados."""
    camino_final = camino or []
    return {
        "camino": camino_final,
        "costo_total": puzzle.costo_camino(camino_final),
        "longitud_camino": max(len(camino_final) - 1, 0),
        "nodos_expandidos": nodos_expandidos,
        "memoria": memoria,
        "max_frontera": max_frontera,
        "tiempo_ejecucion_ms": (time.perf_counter() - inicio_tiempo) * 1000,
        "encontrado": bool(camino_final),
    }


# ---------------------------------------------------------------------------
# Heurísticas
# ---------------------------------------------------------------------------

def _posiciones_objetivo(objetivo: Estado) -> Dict[int, int]:
    """Índice de cada ficha en el estado objetivo."""
    return {valor: indice for indice, valor in enumerate(objetivo)}


def heuristica_manhattan(estado: Estado, objetivo: Estado) -> int:
    """Suma la distancia Manhattan de cada ficha a su posición objetivo.

    Es admisible con costos por ficha porque cada movimiento cuesta al
    menos 1, pero ignora que las fichas grandes son más caras de mover.
    """
    posiciones = _posiciones_objetivo(objetivo)
    return sum(
        abs(indice // 3 - posiciones[valor] // 3)
        + abs(indice % 3 - posiciones[valor] % 3)
        for indice, valor in enumerate(estado)
        if valor != 0
    )


def heuristica_manhattan_ponderada(estado: Estado, objetivo: Estado) -> int:
    """Heurística propia: distancia Manhattan de cada ficha por su costo.

    h(n) = suma sobre cada ficha t de  t * distancia_manhattan(t).

    La ficha t debe moverse al menos distancia_manhattan(t) veces y cada
    movimiento suyo cuesta t, por lo que h nunca sobreestima el costo real
    (admisible). Un movimiento cambia la distancia de una sola ficha t en
    exactamente una unidad, así que h varía como mucho en t, que es el costo
    de la acción (consistente).
    """
    posiciones = _posiciones_objetivo(objetivo)
    return sum(
        valor * (
            abs(indice // 3 - posiciones[valor] // 3)
            + abs(indice % 3 - posiciones[valor] % 3)
        )
        for indice, valor in enumerate(estado)
        if valor != 0
    )


# ---------------------------------------------------------------------------
# Búsqueda no informada
# ---------------------------------------------------------------------------

def bfs_camino(puzzle: Puzzle) -> Resultado:
    """Búsqueda en amplitud: frontera FIFO (cola).

    Encuentra la solución con menos movimientos, pero no necesariamente
    la de menor costo, porque ignora el costo de las acciones.
    """
    inicio_tiempo = time.perf_counter()
    cola = deque([puzzle.inicio])
    visitados = {puzzle.inicio}
    predecesor = {puzzle.inicio: None}
    nodos_expandidos = 0
    max_frontera = 1

    while cola:
        estado = cola.popleft()
        nodos_expandidos += 1
        if estado == puzzle.objetivo:
            return construir_resultado(
                puzzle, reconstruir_camino(predecesor, estado),
                nodos_expandidos, len(visitados), max_frontera, inicio_tiempo,
            )
        for vecino in puzzle.vecinos(estado):
            if vecino not in visitados:
                visitados.add(vecino)
                predecesor[vecino] = estado
                cola.append(vecino)
        max_frontera = max(max_frontera, len(cola))

    return construir_resultado(
        puzzle, None, nodos_expandidos, len(visitados), max_frontera,
        inicio_tiempo,
    )


def dfs_camino(puzzle: Puzzle) -> Resultado:
    """Búsqueda en profundidad: frontera LIFO (pila).

    Los sucesores se apilan en orden inverso de su distancia Manhattan
    para que la pila explore primero los estados que parecen acercarse
    al objetivo. Esto no convierte DFS en A*: la estructura sigue siendo
    una pila y no se usa el costo acumulado, así que la solución no tiene
    que ser óptima.
    """
    inicio_tiempo = time.perf_counter()
    pila = [puzzle.inicio]
    visitados = {puzzle.inicio}
    predecesor = {puzzle.inicio: None}
    nodos_expandidos = 0
    max_frontera = 1

    while pila:
        estado = pila.pop()
        nodos_expandidos += 1
        if estado == puzzle.objetivo:
            return construir_resultado(
                puzzle, reconstruir_camino(predecesor, estado),
                nodos_expandidos, len(visitados), max_frontera, inicio_tiempo,
            )
        vecinos_ordenados = sorted(
            puzzle.vecinos(estado),
            key=lambda vecino: heuristica_manhattan(vecino, puzzle.objetivo),
            reverse=True,
        )

        for vecino in vecinos_ordenados:
            if vecino not in visitados:
                visitados.add(vecino)
                predecesor[vecino] = estado
                pila.append(vecino)
        max_frontera = max(max_frontera, len(pila))

    return construir_resultado(
        puzzle, None, nodos_expandidos, len(visitados), max_frontera,
        inicio_tiempo,
    )


# ---------------------------------------------------------------------------
# Búsqueda con costos e informada
# ---------------------------------------------------------------------------

def _busqueda_por_prioridad(
    puzzle: Puzzle,
    heuristica: Optional[Heuristica],
) -> Resultado:
    """Núcleo común de costo uniforme (sin heurística) y A* (con heurística).

    La frontera es una cola de prioridad (``heapq``) ordenada por
    f(n) = g(n) + h(n). Con ``heuristica=None`` se usa h(n) = 0 y el
    algoritmo es búsqueda de costo uniforme. Cuando se encuentra un camino
    más barato a un estado se inserta una entrada nueva; las entradas
    obsoletas se descartan al sacarlas.
    """
    inicio_tiempo = time.perf_counter()

    def h(estado: Estado) -> int:
        return heuristica(estado, puzzle.objetivo) if heuristica else 0

    contador = 0
    costos = {puzzle.inicio: 0}
    predecesor = {puzzle.inicio: None}
    cola = [(h(puzzle.inicio), 0, contador, puzzle.inicio)]
    nodos_expandidos = 0
    max_frontera = 1

    while cola:
        _, costo, _, estado = heapq.heappop(cola)
        if costo != costos.get(estado):
            continue  # Entrada obsoleta: ya existe un camino más barato.
        nodos_expandidos += 1
        if estado == puzzle.objetivo:
            return construir_resultado(
                puzzle, reconstruir_camino(predecesor, estado),
                nodos_expandidos, len(costos), max_frontera, inicio_tiempo,
            )
        for vecino in puzzle.vecinos(estado):
            nuevo_costo = costo + puzzle.costo_movimiento(estado, vecino)
            if nuevo_costo < costos.get(vecino, INFINITO):
                costos[vecino] = nuevo_costo
                predecesor[vecino] = estado
                contador += 1
                prioridad = nuevo_costo + h(vecino)
                heapq.heappush(cola, (prioridad, nuevo_costo, contador, vecino))
        max_frontera = max(max_frontera, len(cola))

    return construir_resultado(
        puzzle, None, nodos_expandidos, len(costos), max_frontera,
        inicio_tiempo,
    )


def bcu_camino(puzzle: Puzzle) -> Resultado:
    """Búsqueda de costo uniforme: prioridad por g(n)."""
    return _busqueda_por_prioridad(puzzle, None)


def astar_generico(puzzle: Puzzle, heuristica: Heuristica) -> Resultado:
    """A* con la heurística indicada: prioridad por g(n) + h(n)."""
    return _busqueda_por_prioridad(puzzle, heuristica)


def astar_manhattan_camino(puzzle: Puzzle) -> Resultado:
    """A* con la distancia Manhattan clásica (línea base)."""
    return astar_generico(puzzle, heuristica_manhattan)


def astar_propia_camino(puzzle: Puzzle) -> Resultado:
    """A* con la heurística propia: Manhattan ponderada por ficha."""
    return astar_generico(puzzle, heuristica_manhattan_ponderada)
