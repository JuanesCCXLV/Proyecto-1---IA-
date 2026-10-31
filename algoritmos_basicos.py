"""Implementaciones didácticas de BFS y DFS sobre un grafo genérico.

El programa principal usa las versiones instrumentadas de ``algoritmos.py``
para resolver el 8-puzzle; este módulo se conserva como material auxiliar.
"""

from collections import deque


def bfs_camino(grafo, inicio, objetivo):
    """Busca una ruta utilizando una cola FIFO."""
    cola = deque([inicio])
    visitados = {inicio}
    predecesor = {inicio: None}

    while cola:
        nodo = cola.popleft()

        if nodo == objetivo:
            camino = []

            while nodo is not None:
                camino.append(nodo)
                nodo = predecesor[nodo]

            return list(reversed(camino))

        for vecino in grafo[nodo]:
            if vecino not in visitados:
                visitados.add(vecino)
                predecesor[vecino] = nodo
                cola.append(vecino)

    return None


def dfs_camino(grafo, inicio, objetivo):
    """Busca una ruta utilizando una pila LIFO."""
    pila = [inicio]
    visitados = {inicio}
    predecesor = {inicio: None}

    while pila:
        nodo = pila.pop()

        if nodo == objetivo:
            camino = []

            while nodo is not None:
                camino.append(nodo)
                nodo = predecesor[nodo]

            return list(reversed(camino))

        for vecino in grafo[nodo]:
            if vecino not in visitados:
                visitados.add(vecino)
                predecesor[vecino] = nodo
                pila.append(vecino)

    return None