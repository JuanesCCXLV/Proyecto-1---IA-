"""Algoritmos de búsqueda para resolver el 8-puzzle."""

from collections import deque
import heapq
import time
from typing import Callable, Dict, List, Optional

from mapa import Estado, Puzzle


Resultado = Dict[str, object]
Heuristica = Callable[[Estado], float]
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
    inicio_tiempo: float,
) -> Resultado:
    """Crea el formato común de resultados."""
    camino_final = camino or []
    return {
        "camino": camino_final,
        "costo_total": max(len(camino_final) - 1, 0),
        "longitud_camino": max(len(camino_final) - 1, 0),
        "nodos_expandidos": nodos_expandidos,
        "tiempo_ejecucion_ms": (time.perf_counter() - inicio_tiempo) * 1000,
        "encontrado": bool(camino_final),
    }


def bfs_camino(puzzle: Puzzle) -> Resultado:
    """Resuelve el puzzle con búsqueda en amplitud."""
    inicio_tiempo = time.perf_counter()
    cola = deque([puzzle.inicio])
    visitados = {puzzle.inicio}
    predecesor = {puzzle.inicio: None}
    nodos_expandidos = 0

    while cola:
        estado = cola.popleft()
        nodos_expandidos += 1
        if estado == puzzle.objetivo:
            return construir_resultado(
                puzzle, reconstruir_camino(predecesor, estado),
                nodos_expandidos, inicio_tiempo,
            )
        for vecino in puzzle.vecinos(estado):
            if vecino not in visitados:
                visitados.add(vecino)
                predecesor[vecino] = estado
                cola.append(vecino)

    return construir_resultado(puzzle, None, nodos_expandidos, inicio_tiempo)


def dfs_camino(puzzle: Puzzle) -> Resultado:
    """Resuelve el puzzle con búsqueda en profundidad.

    Los sucesores se apilan en orden inverso de su distancia Manhattan
    para que la pila explore primero los estados que parecen acercarse
    al objetivo. Esto no convierte DFS en A*: la solución no tiene que
    ser óptima, pero evita recorridos innecesariamente extensos en los
    casos de demostración.
    """
    inicio_tiempo = time.perf_counter()
    pila = [puzzle.inicio]
    visitados = {puzzle.inicio}
    predecesor = {puzzle.inicio: None}
    nodos_expandidos = 0

    while pila:
        estado = pila.pop()
        nodos_expandidos += 1
        if estado == puzzle.objetivo:
            return construir_resultado(
                puzzle, reconstruir_camino(predecesor, estado),
                nodos_expandidos, inicio_tiempo,
            )
        vecinos_ordenados = sorted(
            puzzle.vecinos(estado),
            key=lambda vecino: heuristica_manhattan(
                vecino,
                puzzle.objetivo,
            ),
            reverse=True,
        )

        for vecino in vecinos_ordenados:
            if vecino not in visitados:
                visitados.add(vecino)
                predecesor[vecino] = estado
                pila.append(vecino)

    return construir_resultado(puzzle, None, nodos_expandidos, inicio_tiempo)


def bcu_camino(puzzle: Puzzle) -> Resultado:
    """Resuelve el puzzle con búsqueda de costo uniforme."""
    inicio_tiempo = time.perf_counter()
    contador = 0
    cola = [(0, contador, puzzle.inicio)]
    costos = {puzzle.inicio: 0}
    predecesor = {puzzle.inicio: None}
    nodos_expandidos = 0

    while cola:
        costo, _, estado = heapq.heappop(cola)
        if costo != costos.get(estado):
            continue
        nodos_expandidos += 1
        if estado == puzzle.objetivo:
            return construir_resultado(
                puzzle, reconstruir_camino(predecesor, estado),
                nodos_expandidos, inicio_tiempo,
            )
        for vecino in puzzle.vecinos(estado):
            nuevo_costo = costo + puzzle.costo_movimiento(vecino)
            if nuevo_costo < costos.get(vecino, INFINITO):
                costos[vecino] = nuevo_costo
                predecesor[vecino] = estado
                contador += 1
                heapq.heappush(cola, (nuevo_costo, contador, vecino))

    return construir_resultado(puzzle, None, nodos_expandidos, inicio_tiempo)


def heuristica_manhattan(estado: Estado, objetivo: Estado) -> int:
    """Suma la distancia Manhattan de cada ficha a su posición objetivo."""
    posiciones = {valor: indice for indice, valor in enumerate(objetivo)}
    return sum(
        abs(indice // 3 - posiciones[valor] // 3)
        + abs(indice % 3 - posiciones[valor] % 3)
        for indice, valor in enumerate(estado)
        if valor != 0
    )


def heuristica_fichas_fuera_de_lugar(estado: Estado, objetivo: Estado) -> int:
    """Cuenta las fichas que no están en su posición final."""
    return sum(
        valor != esperado and valor != 0
        for valor, esperado in zip(estado, objetivo)
    )


def astar_generico(
    puzzle: Puzzle,
    heuristica: Callable[[Estado, Estado], int],
) -> Resultado:
    """Resuelve el puzzle con A* y la heurística indicada."""
    inicio_tiempo = time.perf_counter()
    contador = 0
    costos = {puzzle.inicio: 0}
    predecesor = {puzzle.inicio: None}
    cola = [(
        heuristica(puzzle.inicio, puzzle.objetivo),
        0,
        contador,
        puzzle.inicio,
    )]
    nodos_expandidos = 0

    while cola:
        _, costo, _, estado = heapq.heappop(cola)
        if costo != costos.get(estado):
            continue
        nodos_expandidos += 1
        if estado == puzzle.objetivo:
            return construir_resultado(
                puzzle, reconstruir_camino(predecesor, estado),
                nodos_expandidos, inicio_tiempo,
            )
        for vecino in puzzle.vecinos(estado):
            nuevo_costo = costo + 1
            if nuevo_costo < costos.get(vecino, INFINITO):
                costos[vecino] = nuevo_costo
                predecesor[vecino] = estado
                contador += 1
                prioridad = nuevo_costo + heuristica(vecino, puzzle.objetivo)
                heapq.heappush(cola, (prioridad, nuevo_costo, contador, vecino))

    return construir_resultado(puzzle, None, nodos_expandidos, inicio_tiempo)


def astar_manhattan_camino(puzzle: Puzzle) -> Resultado:
    """A* con la heurística Manhattan."""
    return astar_generico(puzzle, heuristica_manhattan)


def astar_propia_camino(puzzle: Puzzle) -> Resultado:
    """A* con la heurística admisible de fichas fuera de lugar."""
    return astar_generico(puzzle, heuristica_fichas_fuera_de_lugar)
