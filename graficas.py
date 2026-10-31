"""Genera gráficas y un CSV con el desempeño de los algoritmos del 8-puzzle.

Uso:
    python graficas.py

Requiere matplotlib:
    pip install matplotlib

Produce, en la carpeta ``resultados/``:
    - resultados.csv          (8-puzzle: todos los algoritmos y casos)
    - minimax.csv             (triqui: nodos evaluados con y sin poda)
    - nodos_expandidos.png
    - costo_total.png
    - memoria.png
    - tiempo_ejecucion.png
    - minimax_poda.png
"""

import csv
from pathlib import Path
from typing import Dict, List

import matplotlib

matplotlib.use("Agg")  # Permite guardar imágenes sin ventana gráfica.
import matplotlib.pyplot as plt

from comparador import ALGORITMOS, ejecutar_comparacion
from mapas_prueba import PUZZLES
from minimax import HUMANO, MAQUINA, VACIO, comparar_poda


# Tableros del triqui en los que juega la máquina (O), para medir la poda.
# Se leen fila por fila; "." es una casilla vacía.
ESCENARIOS_MINIMAX = {
    "Tablero vacío": ".........",
    "X en una esquina": "X........",
    "X centro, O esquina, X esquina": "O...X...X",
}
PROFUNDIDADES_MINIMAX = (2, 4, 6, 9)


CARPETA_SALIDA = Path("resultados")

# Puzzles en los que ningún algoritmo encuentra solución no se grafican,
# porque el costo y los pasos no tienen significado.
Datos = Dict[str, Dict[str, dict]]


def recolectar_datos() -> Datos:
    """Ejecuta todos los algoritmos sobre todos los casos de puzzle."""
    datos: Datos = {}

    for nombre_puzzle, crear_puzzle in PUZZLES.items():
        puzzle = crear_puzzle()
        datos[nombre_puzzle] = ejecutar_comparacion(puzzle)

    return datos


def guardar_csv(datos: Datos, ruta: Path) -> None:
    """Guarda todos los resultados en un archivo CSV."""
    with open(ruta, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow([
            "puzzle",
            "algoritmo",
            "ruta_encontrada",
            "nodos_expandidos",
            "costo_total",
            "pasos",
            "memoria",
            "max_frontera",
            "tiempo_ms",
        ])

        for nombre_puzzle, resultados in datos.items():
            for algoritmo, r in resultados.items():
                escritor.writerow([
                    nombre_puzzle,
                    algoritmo,
                    "SI" if r["encontrado"] else "NO",
                    r["nodos_expandidos"],
                    r["costo_total"],
                    r["longitud_camino"],
                    r["memoria"],
                    r["max_frontera"],
                    f"{r['tiempo_ejecucion_ms']:.4f}",
                ])


def graficar_barras(
    datos: Datos,
    clave: str,
    titulo: str,
    etiqueta_y: str,
    ruta: Path,
    escala_log: bool = False,
) -> None:
    """Crea un gráfico de barras agrupadas: un grupo por puzzle.

    Con ``escala_log=True`` el eje Y es logarítmico, para que se vean a la
    vez valores pequeños (decenas) y grandes (decenas de miles).
    """
    puzzles = [
        nombre
        for nombre, resultados in datos.items()
        if any(r["encontrado"] for r in resultados.values())
    ]
    algoritmos = list(ALGORITMOS)

    ancho_barra = 0.8 / len(algoritmos)
    figura, eje = plt.subplots(figsize=(11, 6))

    for indice, algoritmo in enumerate(algoritmos):
        valores = [datos[puzzle][algoritmo][clave] for puzzle in puzzles]
        posiciones = [
            i + indice * ancho_barra - 0.4 + ancho_barra / 2
            for i in range(len(puzzles))
        ]
        barras = eje.bar(
            posiciones,
            valores,
            ancho_barra,
            label=algoritmo,
        )

        for barra, valor in zip(barras, valores):
            texto = (
                f"{valor:.2f}" if clave == "tiempo_ejecucion_ms"
                else str(valor)
            )
            eje.annotate(
                texto,
                (barra.get_x() + barra.get_width() / 2, valor),
                ha="center",
                va="bottom",
                fontsize=7,
            )

    eje.set_xticks(range(len(puzzles)))
    eje.set_xticklabels(puzzles, fontsize=9)
    if escala_log:
        eje.set_yscale("log")
        etiqueta_y += " (escala log)"
    eje.set_ylabel(etiqueta_y)
    eje.set_title(titulo)
    eje.legend(fontsize=8)
    eje.grid(axis="y", alpha=0.3)

    figura.tight_layout()
    figura.savefig(ruta, dpi=150)
    plt.close(figura)


def tablero_desde_texto(texto: str) -> tuple:
    """Convierte "X...O...." en una tupla de tablero."""
    equivalencias = {"X": HUMANO, "O": MAQUINA, ".": VACIO}
    return tuple(equivalencias[c] for c in texto)


def recolectar_minimax() -> list:
    """Mide nodos evaluados con y sin poda en varios tableros y profundidades."""
    filas = []
    for escenario, texto in ESCENARIOS_MINIMAX.items():
        tablero = tablero_desde_texto(texto)
        for profundidad in PROFUNDIDADES_MINIMAX:
            m = comparar_poda(tablero, profundidad)
            filas.append({"escenario": escenario, "profundidad": profundidad, **m})
    return filas


def guardar_csv_minimax(filas: list, ruta: Path) -> None:
    """Guarda las métricas de Minimax en un CSV."""
    with open(ruta, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow([
            "escenario", "profundidad", "jugada", "valor",
            "nodos_sin_poda", "nodos_con_poda", "reduccion_pct",
            "tiempo_sin_ms", "tiempo_con_ms", "misma_decision",
        ])
        for f in filas:
            escritor.writerow([
                f["escenario"], f["profundidad"], f["posicion"] + 1, f["valor"],
                f["nodos_sin_poda"], f["nodos_con_poda"],
                f"{f['reduccion_pct']:.1f}",
                f"{f['tiempo_sin_ms']:.3f}", f"{f['tiempo_con_ms']:.3f}",
                "SI" if f["misma_decision"] else "NO",
            ])


def graficar_minimax(filas: list, ruta: Path) -> None:
    """Barras de nodos evaluados con y sin poda (escala logarítmica)."""
    vacio = [f for f in filas if f["escenario"] == "Tablero vacío"]
    etiquetas = [f"Prof. {f['profundidad']}" for f in vacio]
    posiciones = range(len(vacio))
    figura, eje = plt.subplots(figsize=(9, 5))
    barras_sin = eje.bar([p - 0.2 for p in posiciones],
                         [f["nodos_sin_poda"] for f in vacio], 0.4,
                         label="Sin poda")
    barras_con = eje.bar([p + 0.2 for p in posiciones],
                         [f["nodos_con_poda"] for f in vacio], 0.4,
                         label="Con poda alfa-beta")
    for barra in list(barras_sin) + list(barras_con):
        eje.annotate(f"{int(barra.get_height()):,}".replace(",", "."),
                     (barra.get_x() + barra.get_width() / 2, barra.get_height()),
                     ha="center", va="bottom", fontsize=8)
    eje.set_yscale("log")
    eje.set_xticks(list(posiciones))
    eje.set_xticklabels(etiquetas)
    eje.set_ylabel("Nodos evaluados (escala log)")
    eje.set_title("Minimax desde el tablero vacío: nodos con y sin poda")
    eje.legend()
    eje.grid(axis="y", alpha=0.3)
    figura.tight_layout()
    figura.savefig(ruta, dpi=150)
    plt.close(figura)


def main() -> None:
    """Genera los CSV y las gráficas."""
    CARPETA_SALIDA.mkdir(exist_ok=True)
    datos = recolectar_datos()

    guardar_csv(datos, CARPETA_SALIDA / "resultados.csv")

    graficar_barras(
        datos,
        "nodos_expandidos",
        "Nodos expandidos por algoritmo y puzzle",
        "Nodos expandidos",
        CARPETA_SALIDA / "nodos_expandidos.png",
        escala_log=True,
    )
    graficar_barras(
        datos,
        "costo_total",
        "Costo total de la solución por algoritmo y puzzle",
        "Costo total",
        CARPETA_SALIDA / "costo_total.png",
    )
    graficar_barras(
        datos,
        "memoria",
        "Estados almacenados en memoria por algoritmo y puzzle",
        "Estados almacenados",
        CARPETA_SALIDA / "memoria.png",
        escala_log=True,
    )
    graficar_barras(
        datos,
        "tiempo_ejecucion_ms",
        "Tiempo de ejecución promedio por algoritmo y puzzle",
        "Tiempo (ms)",
        CARPETA_SALIDA / "tiempo_ejecucion.png",
        escala_log=True,
    )

    filas_minimax = recolectar_minimax()
    guardar_csv_minimax(filas_minimax, CARPETA_SALIDA / "minimax.csv")
    graficar_minimax(filas_minimax, CARPETA_SALIDA / "minimax_poda.png")

    print(f"Archivos generados en la carpeta '{CARPETA_SALIDA}/'.")


if __name__ == "__main__":
    main()