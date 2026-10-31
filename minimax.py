"""Juego de triqui contra la máquina mediante Minimax con poda alfa-beta."""

from typing import Optional, Tuple


Tablero = Tuple[str, ...]
VACIO = " "
HUMANO = "X"
MAQUINA = "O"


def ganador(tablero: Tablero) -> Optional[str]:
    """Devuelve el jugador ganador o ``None`` si la partida continúa."""
    combinaciones = (
        (0, 1, 2), (3, 4, 5), (6, 7, 8),
        (0, 3, 6), (1, 4, 7), (2, 5, 8),
        (0, 4, 8), (2, 4, 6),
    )
    for a, b, c in combinaciones:
        if tablero[a] != VACIO and tablero[a] == tablero[b] == tablero[c]:
            return tablero[a]
    return None


def movimientos_disponibles(tablero: Tablero) -> Tuple[int, ...]:
    """Indica las casillas libres del tablero."""
    return tuple(indice for indice, valor in enumerate(tablero) if valor == VACIO)


def minimax(
    tablero: Tablero,
    turno: str,
    alfa: int = -100,
    beta: int = 100,
) -> int:
    """Evalúa un estado desde la perspectiva de la máquina."""
    resultado = ganador(tablero)
    if resultado == MAQUINA:
        return 10
    if resultado == HUMANO:
        return -10
    disponibles = movimientos_disponibles(tablero)
    if not disponibles:
        return 0

    if turno == MAQUINA:
        mejor = -100
        for movimiento in disponibles:
            siguiente = list(tablero)
            siguiente[movimiento] = MAQUINA
            mejor = max(mejor, minimax(tuple(siguiente), HUMANO, alfa, beta))
            alfa = max(alfa, mejor)
            if beta <= alfa:
                break
        return mejor

    mejor = 100
    for movimiento in disponibles:
        siguiente = list(tablero)
        siguiente[movimiento] = HUMANO
        mejor = min(mejor, minimax(tuple(siguiente), MAQUINA, alfa, beta))
        beta = min(beta, mejor)
        if beta <= alfa:
            break
    return mejor


def mejor_movimiento(tablero: Tablero) -> int:
    """Elige el movimiento óptimo para la máquina."""
    puntuaciones = []
    for movimiento in movimientos_disponibles(tablero):
        siguiente = list(tablero)
        siguiente[movimiento] = MAQUINA
        puntuaciones.append((
            minimax(tuple(siguiente), HUMANO),
            movimiento,
        ))
    return max(puntuaciones)[1]


def imprimir_tablero(tablero: Tablero) -> None:
    """Imprime el tablero con posiciones numéricas para las casillas libres."""
    valores = [
        str(indice + 1) if valor == VACIO else valor
        for indice, valor in enumerate(tablero)
    ]
    for fila in range(3):
        print(f" {valores[fila * 3]} | {valores[fila * 3 + 1]} | {valores[fila * 3 + 2]}")
        if fila < 2:
            print("---+---+---")


def jugar() -> None:
    """Ejecuta una partida interactiva de triqui contra Minimax."""
    tablero: Tablero = (VACIO,) * 9
    print("\nTRIQUI CONTRA MINIMAX")
    print("Tú juegas con X. Elige una posición del 1 al 9.")

    while True:
        imprimir_tablero(tablero)
        disponibles = movimientos_disponibles(tablero)
        if not disponibles:
            print("Empate.")
            return

        while True:
            entrada = input("Tu movimiento: ").strip()
            if entrada.isdigit() and int(entrada) - 1 in disponibles:
                posicion = int(entrada) - 1
                break
            print("Movimiento inválido.")

        tablero_lista = list(tablero)
        tablero_lista[posicion] = HUMANO
        tablero = tuple(tablero_lista)
        if ganador(tablero) == HUMANO:
            imprimir_tablero(tablero)
            print("Ganaste.")
            return

        disponibles = movimientos_disponibles(tablero)
        if not disponibles:
            imprimir_tablero(tablero)
            print("Empate.")
            return

        posicion = mejor_movimiento(tablero)
        tablero_lista = list(tablero)
        tablero_lista[posicion] = MAQUINA
        tablero = tuple(tablero_lista)
        print(f"La máquina juega en la posición {posicion + 1}.")
        if ganador(tablero) == MAQUINA:
            imprimir_tablero(tablero)
            print("Ganó la máquina.")
            return
