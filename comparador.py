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
 
ANCHO_TABLA = 90
 
 
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
    
    La columna de costo permite comparar la calidad de las soluciones.
    """
    print("=" * ANCHO_TABLA)
    print("RESULTADOS DE BÚSQUEDA DEL 8-PUZZLE")
    print("=" * ANCHO_TABLA)

    encabezado = (
        f"{'Algoritmo':<15} | "
        f"{'Nodos':>8} | "
        f"{'Costo':>8} | "
        f"{'Pasos':>8} | "
        f"{'Ruta':>8} | "
        f"{'Tiempo (ms)':>12}"
    )

    print(encabezado)
    print("-" * ANCHO_TABLA)

    costos_validos = [r["costo_total"] for r in resultados.values() if r["encontrado"]]
    costo_minimo = min(costos_validos) if costos_validos else None

    for nombre, resultado in resultados.items():
        ruta = "SÍ" if resultado["encontrado"] else "NO"

        if not resultado["encontrado"]:
            optimo = "-"
        elif len(resultados) == 1:
            optimo = "-"
        else:
            optimo = (
                "Si"
                if resultado["costo_total"] == costo_minimo
                else "No"
            )

        print(
            f"{nombre:<15} | "
            f"{resultado['nodos_expandidos']:>8} | "
            f"{resultado['costo_total']:>8} | "
            f"{resultado['longitud_camino']:>8} | "
            f"{ruta:>8} | "
            f"{resultado['tiempo_ejecucion_ms']:>12.4f}"
        )

    print("=" * ANCHO_TABLA)


def mostrar_solucion(
    nombre: str,
    resultado: Resultado,
    puzzle: Puzzle,
) -> None:
    """Imprime los estados de la solución encontrada."""
    print(f"\nALGORITMO: {nombre}")

    if not resultado["encontrado"]:
        print("No se encontró una solución.")
        return

    camino = resultado["camino"]
    print(f"Costo total: {resultado['costo_total']}")
    print(f"Pasos: {resultado['longitud_camino']}")
    print(f"Movimientos: {len(camino) - 1}")
    for paso, estado in enumerate(camino):
        print(f"\nPaso {paso}:")
        puzzle.imprimir(estado)
