"""Genera gráficas y un CSV con el desempeño de los algoritmos del 8-puzzle.

Uso:
    python graficas.py

Requiere matplotlib:
    pip install matplotlib

Produce, en la carpeta ``resultados/``:
    - resultados.csv
    - nodos_expandidos.png
    - costo_total.png
    - tiempo_ejecucion.png
"""

import csv
from pathlib import Path
from typing import Dict, List

import matplotlib

matplotlib.use("Agg")  # Permite guardar imágenes sin ventana gráfica.
import matplotlib.pyplot as plt

from comparador import ALGORITMOS, ejecutar_comparacion
from mapas_prueba import PUZZLES


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
                    f"{r['tiempo_ejecucion_ms']:.4f}",
                ])


def graficar_barras(
    datos: Datos,
    clave: str,
    titulo: str,
    etiqueta_y: str,
    ruta: Path,
) -> None:
    """Crea un gráfico de barras agrupadas: un grupo por puzzle."""
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
    eje.set_ylabel(etiqueta_y)
    eje.set_title(titulo)
    eje.legend()
    eje.grid(axis="y", alpha=0.3)

    figura.tight_layout()
    figura.savefig(ruta, dpi=150)
    plt.close(figura)


def main() -> None:
    """Genera el CSV y las tres gráficas."""
    CARPETA_SALIDA.mkdir(exist_ok=True)
    datos = recolectar_datos()

    guardar_csv(datos, CARPETA_SALIDA / "resultados.csv")

    graficar_barras(
        datos,
        "nodos_expandidos",
        "Nodos expandidos por algoritmo y puzzle",
        "Nodos expandidos",
        CARPETA_SALIDA / "nodos_expandidos.png",
    )
    graficar_barras(
        datos,
        "costo_total",
        "Movimientos por algoritmo y puzzle",
        "Costo total",
        CARPETA_SALIDA / "costo_total.png",
    )
    graficar_barras(
        datos,
        "tiempo_ejecucion_ms",
        "Tiempo de ejecución promedio por algoritmo y puzzle",
        "Tiempo (ms)",
        CARPETA_SALIDA / "tiempo_ejecucion.png",
    )

    print(f"Archivos generados en la carpeta '{CARPETA_SALIDA}/'.")


if __name__ == "__main__":
    main()