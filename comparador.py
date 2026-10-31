"""Ejecución y comparación de algoritmos para el 8-puzzle."""

from typing import Callable, Dict, List, Optional

from algoritmos import (
    Resultado,
    astar_manhattan_camino,
    astar_propia_camino,
    bcu_camino,
    bfs_camino,
    dfs_camino,
)
from mapa import Puzzle

# Catálogo: nombre que se muestra -> función que ejecuta el algoritmo.
ALGORITMOS: Dict[str, Callable[[Puzzle], Resultado]] = {
    "DFS": dfs_camino,
    "BFS": bfs_camino,
    "BCU": bcu_camino,
    "A* Manhattan": astar_manhattan_camino,
    "A* Propia": astar_propia_camino,
}
 
# Cuántas veces se repite cada algoritmo para promediar el tiempo.
REPETICIONES_TIEMPO = 20
 
ANCHO_TABLA = 86
 
 
def ejecutar_algoritmo(
    nombre: str,
    puzzle: Puzzle,
    repeticiones: int = REPETICIONES_TIEMPO,
) -> Resultado:
    """Ejecuta un algoritmo varias veces y promedia su tiempo.
 
    El camino, el costo y los nodos expandidos son deterministas, así
    que se conserva el resultado de la última ejecución. Solo el tiempo
    se promedia, porque varía entre ejecuciones.
    """
    algoritmo = ALGORITMOS[nombre]
    tiempos: List[float] = []
    resultado: Resultado = {}
 
    for _ in range(max(repeticiones, 1)):
        resultado = algoritmo(puzzle)
        tiempos.append(resultado["tiempo_ejecucion_ms"])
 
    resultado["tiempo_ejecucion_ms"] = sum(tiempos) / len(tiempos)
    return resultado
 
 
def ejecutar_comparacion(
    puzzle: Puzzle,
    nombres: Optional[List[str]] = None,
    repeticiones: int = REPETICIONES_TIEMPO,
) -> Dict[str, Resultado]:
    """Ejecuta los algoritmos indicados sobre el mismo estado inicial."""
    if nombres is None:
        nombres = list(ALGORITMOS)
 
    return {
        nombre: ejecutar_algoritmo(nombre, puzzle, repeticiones)
        for nombre in nombres
    }

def mostrar_resultados(
    resultados: Dict[str, Resultado],
    puzzle: Puzzle,
) -> None:
    """Imprime una tabla comparativa de resultados.

    ``Costo`` es la suma de los costos de las fichas movidas, ``Pasos`` la
    profundidad de la solución y ``Memoria`` el número de estados
    almacenados. ``Óptimo`` indica si el costo coincide con el menor costo
    encontrado entre los algoritmos ejecutados.
    """
    print("=" * ANCHO_TABLA)
    print("RESULTADOS DE BÚSQUEDA DEL 8-PUZZLE")
    print("=" * ANCHO_TABLA)

    encabezado = (
        f"{'Algoritmo':<13} | "
        f"{'Ruta':>4} | "
        f"{'Nodos exp.':>10} | "
        f"{'Memoria':>8} | "
        f"{'Pasos':>5} | "
        f"{'Costo':>5} | "
        f"{'Óptimo':>6} | "
        f"{'Tiempo (ms)':>11}"
    )

    print(encabezado)
    print("-" * ANCHO_TABLA)

    costos_validos = [r["costo_total"] for r in resultados.values() if r["encontrado"]]
    costo_minimo = min(costos_validos) if costos_validos else None

    for nombre, resultado in resultados.items():
        ruta = "SÍ" if resultado["encontrado"] else "NO"

        if not resultado["encontrado"] or len(resultados) == 1:
            optimo = "-"
        else:
            optimo = "Sí" if resultado["costo_total"] == costo_minimo else "No"

        pasos = resultado["longitud_camino"] if resultado["encontrado"] else "-"
        costo = resultado["costo_total"] if resultado["encontrado"] else "-"

        print(
            f"{nombre:<13} | "
            f"{ruta:>4} | "
            f"{resultado['nodos_expandidos']:>10} | "
            f"{resultado['memoria']:>8} | "
            f"{pasos:>5} | "
            f"{costo:>5} | "
            f"{optimo:>6} | "
            f"{resultado['tiempo_ejecucion_ms']:>11.4f}"
        )

    print("=" * ANCHO_TABLA)


def mostrar_solucion(
    nombre: str,
    resultado: Resultado,
    puzzle: Puzzle,
    mostrar_tableros: bool = True,
) -> None:
    """Imprime la solución: fichas movidas, costo y, opcionalmente, tableros."""
    print(f"\nALGORITMO: {nombre}")

    if not resultado["encontrado"]:
        print("No se encontró una solución: el estado objetivo no es alcanzable.")
        return

    camino = resultado["camino"]
    fichas = [
        Puzzle.ficha_movida(actual, siguiente)
        for actual, siguiente in zip(camino, camino[1:])
    ]
    print(f"Pasos (profundidad): {resultado['longitud_camino']}")
    print(f"Costo total: {resultado['costo_total']}")
    print(f"Nodos expandidos: {resultado['nodos_expandidos']}")
    print("Fichas movidas: " + (" ".join(map(str, fichas)) or "(ninguna)"))

    if not mostrar_tableros:
        return

    costo_acumulado = 0
    for paso, estado in enumerate(camino):
        if paso == 0:
            print("\nEstado inicial:")
        else:
            costo_acumulado += fichas[paso - 1]
            print(f"\nPaso {paso}: mover {fichas[paso - 1]} "
                  f"(costo acumulado {costo_acumulado})")
        puzzle.imprimir(estado)
