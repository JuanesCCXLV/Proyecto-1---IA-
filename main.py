"""Punto de entrada del laboratorio de búsqueda y juegos."""

from comparador import (
    ejecutar_comparacion, 
    mostrar_resultados,
    mostrar_solucion, 
    ALGORITMOS,

)

from mapas_prueba import PUZZLES
from minimax import jugar



def pedir_opcion(titulo: str, opciones: list[str]) -> int:
    """Muestra un menú numerado y devuelve el índice elegido (base 0)."""
    print(f"\n{titulo}")
 
    for numero, opcion in enumerate(opciones, start=1):
        print(f"  {numero}. {opcion}")
 
    while True:
        entrada = input("Elige una opción: ").strip()
 
        if entrada.isdigit() and 1 <= int(entrada) <= len(opciones):
            return int(entrada) - 1
 
        print(f"Opción inválida. Escribe un número entre 1 y {len(opciones)}.")



def main() -> None:
    """Ejecuta la aplicación con menú de selección."""
    nombres_algoritmos = list(ALGORITMOS)

    while True:
        opciones_principales = ["Resolver un 8-puzzle", "Jugar triqui contra Minimax"]
        indice_principal = pedir_opcion("Selecciona una aplicación:", opciones_principales)

        if indice_principal == 1:
            jugar()
            otra = input("\n¿Volver al menú? (s/n): ").strip().lower()
            if otra != "s":
                break
            continue

        nombres_puzzles = list(PUZZLES)
        indice_puzzle = pedir_opcion("Selecciona un caso de 8-puzzle:", nombres_puzzles)
        nombre_puzzle = nombres_puzzles[indice_puzzle]
        puzzle = PUZZLES[nombre_puzzle]()

        opciones = nombres_algoritmos + ["Todos (comparación)"]
        indice_algoritmo = pedir_opcion("Selecciona un algoritmo:", opciones)

        if indice_algoritmo == len(nombres_algoritmos):
            seleccionados = nombres_algoritmos
        else:
            seleccionados = [nombres_algoritmos[indice_algoritmo]]

        print("\nESTADO INICIAL (0 = espacio vacío)")
        print("-" * 30)
        puzzle.imprimir()
        print()
 
        resultados = ejecutar_comparacion(puzzle, seleccionados)
        mostrar_resultados(resultados, puzzle)
 
        print("\nSOLUCIONES ENCONTRADAS")
        print("-" * 30)
 
        for nombre, resultado in resultados.items():
            mostrar_solucion(nombre, resultado, puzzle)
 
        otra = input("\n¿Ejecutar otra búsqueda? (s/n): ").strip().lower()
 
        if otra != "s":
            break
 
    print("Fin del programa.")





if __name__ == "__main__":
    main()