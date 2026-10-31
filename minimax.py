"""Juego de triqui contra la máquina mediante Minimax con poda alfa-beta.

El jugador humano usa ``X`` y la máquina usa ``O``. La máquina es el
jugador MAX y el humano el jugador MIN.

- Estados terminales: un jugador completa una línea o el tablero se llena.
- Utilidad terminal: +100 si gana la máquina, -100 si gana el humano y 0 en
  empate. A la victoria se le resta la profundidad a la que ocurre (y a la
  derrota se le suma) para preferir ganar pronto y perder tarde.
- Profundidad límite: si la búsqueda llega al límite sin un estado terminal,
  el tablero se valora con la función de evaluación heurística ``evaluar``.
"""

import time
from typing import Dict, List, Optional, Tuple


Tablero = Tuple[str, ...]
VACIO = " "
HUMANO = "X"
MAQUINA = "O"

UTILIDAD_VICTORIA = 100
PROFUNDIDAD_POR_DEFECTO = 4

LINEAS = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # filas
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # columnas
    (0, 4, 8), (2, 4, 6),             # diagonales
)

# Puntos de una línea abierta según cuántas fichas propias tiene.
PESO_LINEA = {0: 0, 1: 1, 2: 10}


def ganador(tablero: Tablero) -> Optional[str]:
    """Devuelve el jugador ganador o ``None`` si nadie ha completado una línea."""
    for a, b, c in LINEAS:
        if tablero[a] != VACIO and tablero[a] == tablero[b] == tablero[c]:
            return tablero[a]
    return None


def movimientos_disponibles(tablero: Tablero) -> Tuple[int, ...]:
    """Indica las casillas libres del tablero (índices de 0 a 8)."""
    return tuple(indice for indice, valor in enumerate(tablero) if valor == VACIO)


def aplicar(tablero: Tablero, posicion: int, jugador: str) -> Tablero:
    """Función de transición: coloca la ficha del jugador en la posición."""
    nuevo = list(tablero)
    nuevo[posicion] = jugador
    return tuple(nuevo)


def evaluar(tablero: Tablero) -> int:
    """Función de evaluación heurística para estados no terminales.

    Recorre las 8 líneas del tablero. Una línea que solo contiene fichas de
    la máquina suma 1 punto (una ficha) o 10 puntos (dos fichas: amenaza de
    victoria). Una línea que solo contiene fichas del humano resta lo mismo.
    Las líneas con fichas de ambos jugadores ya no pueden ganarse y valen 0.
    El resultado siempre está entre -80 y 80, por debajo de la utilidad de
    una victoria real.
    """
    puntaje = 0
    for linea in LINEAS:
        valores = [tablero[i] for i in linea]
        fichas_maquina = valores.count(MAQUINA)
        fichas_humano = valores.count(HUMANO)
        if fichas_humano == 0:
            puntaje += PESO_LINEA[fichas_maquina]
        elif fichas_maquina == 0:
            puntaje -= PESO_LINEA[fichas_humano]
    return puntaje


def minimax(
    tablero: Tablero,
    turno: str,
    profundidad_restante: int,
    alfa: float,
    beta: float,
    usar_poda: bool,
    contador: Dict[str, int],
    profundidad: int = 1,
) -> int:
    """Valor Minimax de ``tablero`` desde la perspectiva de la máquina.

    ``contador["nodos"]`` acumula cuántos estados se evalúan. Con
    ``usar_poda=False`` se recorre el árbol completo hasta el límite; con
    ``usar_poda=True`` se descartan las ramas en las que ``beta <= alfa``.
    """
    contador["nodos"] += 1

    resultado = ganador(tablero)
    if resultado == MAQUINA:
        return UTILIDAD_VICTORIA - profundidad
    if resultado == HUMANO:
        return -UTILIDAD_VICTORIA + profundidad
    disponibles = movimientos_disponibles(tablero)
    if not disponibles:
        return 0
    if profundidad_restante == 0:
        return evaluar(tablero)

    if turno == MAQUINA:  # Nodo MAX
        mejor = -float("inf")
        for movimiento in disponibles:
            valor = minimax(
                aplicar(tablero, movimiento, MAQUINA), HUMANO,
                profundidad_restante - 1, alfa, beta, usar_poda, contador,
                profundidad + 1,
            )
            mejor = max(mejor, valor)
            alfa = max(alfa, mejor)
            if usar_poda and beta <= alfa:
                break  # Poda beta: MIN nunca permitirá llegar aquí.
        return mejor

    mejor = float("inf")  # Nodo MIN
    for movimiento in disponibles:
        valor = minimax(
            aplicar(tablero, movimiento, HUMANO), MAQUINA,
            profundidad_restante - 1, alfa, beta, usar_poda, contador,
            profundidad + 1,
        )
        mejor = min(mejor, valor)
        beta = min(beta, mejor)
        if usar_poda and beta <= alfa:
            break  # Poda alfa: MAX ya tiene una opción mejor.
    return mejor


def mejor_movimiento(
    tablero: Tablero,
    profundidad_limite: int = PROFUNDIDAD_POR_DEFECTO,
    usar_poda: bool = True,
) -> Tuple[int, int, int]:
    """Elige la jugada de la máquina.

    Devuelve ``(posición, valor, nodos_evaluados)``. La raíz cuenta como un
    nodo evaluado. Ante empates se conserva la primera jugada encontrada,
    por lo que la decisión con poda y sin poda es la misma.
    """
    contador = {"nodos": 1}
    alfa, beta = -float("inf"), float("inf")
    mejor_valor = -float("inf")
    mejor_posicion = -1

    for movimiento in movimientos_disponibles(tablero):
        valor = minimax(
            aplicar(tablero, movimiento, MAQUINA), HUMANO,
            profundidad_limite - 1, alfa, beta, usar_poda, contador,
        )
        if valor > mejor_valor:
            mejor_valor, mejor_posicion = valor, movimiento
        if usar_poda:
            alfa = max(alfa, mejor_valor)

    return mejor_posicion, int(mejor_valor), contador["nodos"]


def comparar_poda(
    tablero: Tablero,
    profundidad_limite: int = PROFUNDIDAD_POR_DEFECTO,
) -> Dict[str, float]:
    """Ejecuta Minimax con y sin poda sobre el mismo tablero y compara."""
    inicio = time.perf_counter()
    posicion_sin, valor_sin, nodos_sin = mejor_movimiento(
        tablero, profundidad_limite, usar_poda=False,
    )
    tiempo_sin = (time.perf_counter() - inicio) * 1000

    inicio = time.perf_counter()
    posicion_con, valor_con, nodos_con = mejor_movimiento(
        tablero, profundidad_limite, usar_poda=True,
    )
    tiempo_con = (time.perf_counter() - inicio) * 1000

    return {
        "posicion": posicion_con,
        "valor": valor_con,
        "misma_decision": posicion_sin == posicion_con and valor_sin == valor_con,
        "nodos_sin_poda": nodos_sin,
        "nodos_con_poda": nodos_con,
        "reduccion_pct": 100 * (1 - nodos_con / nodos_sin) if nodos_sin else 0.0,
        "tiempo_sin_ms": tiempo_sin,
        "tiempo_con_ms": tiempo_con,
    }


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


def _pedir_entero(mensaje: str, minimo: int, maximo: int, defecto: int) -> int:
    """Pide un entero en un rango; Enter devuelve el valor por defecto."""
    while True:
        entrada = input(mensaje).strip()
        if entrada == "":
            return defecto
        if entrada.isdigit() and minimo <= int(entrada) <= maximo:
            return int(entrada)
        print(f"Escribe un número entre {minimo} y {maximo}.")


def turno_maquina(tablero: Tablero, profundidad: int) -> Tuple[Tablero, Dict]:
    """Calcula y aplica la jugada de la máquina mostrando las métricas."""
    metricas = comparar_poda(tablero, profundidad)
    posicion = int(metricas["posicion"])

    print(f"\nLa máquina juega en la posición {posicion + 1} "
          f"(valor Minimax {metricas['valor']}).")
    print(f"  Nodos evaluados sin poda: {metricas['nodos_sin_poda']:>7}"
          f"   ({metricas['tiempo_sin_ms']:.2f} ms)")
    print(f"  Nodos evaluados con poda: {metricas['nodos_con_poda']:>7}"
          f"   ({metricas['tiempo_con_ms']:.2f} ms)")
    print(f"  Reducción por la poda alfa-beta: {metricas['reduccion_pct']:.1f} %")

    return aplicar(tablero, posicion, MAQUINA), metricas


def jugar() -> None:
    """Ejecuta una partida interactiva de triqui contra Minimax."""
    print("\nTRIQUI CONTRA MINIMAX CON PODA ALFA-BETA")
    print("Tú juegas con X y la máquina con O.")
    profundidad = _pedir_entero(
        f"Profundidad límite de Minimax (1-9, Enter = {PROFUNDIDAD_POR_DEFECTO}): ",
        1, 9, PROFUNDIDAD_POR_DEFECTO,
    )
    quien_inicia = _pedir_entero(
        "¿Quién empieza? 1 = tú, 2 = la máquina (Enter = 1): ", 1, 2, 1,
    )

    tablero: Tablero = (VACIO,) * 9
    turno = HUMANO if quien_inicia == 1 else MAQUINA
    historial: List[Dict] = []

    while ganador(tablero) is None and movimientos_disponibles(tablero):
        if turno == MAQUINA:
            tablero, metricas = turno_maquina(tablero, profundidad)
            historial.append(metricas)
            turno = HUMANO
            continue

        print()
        imprimir_tablero(tablero)
        disponibles = movimientos_disponibles(tablero)
        while True:
            entrada = input("Tu movimiento (1-9): ").strip()
            if entrada.isdigit() and int(entrada) - 1 in disponibles:
                break
            print("Movimiento inválido.")
        tablero = aplicar(tablero, int(entrada) - 1, HUMANO)
        turno = MAQUINA

    print()
    imprimir_tablero(tablero)
    resultado = ganador(tablero)
    if resultado == HUMANO:
        print("Ganaste.")
    elif resultado == MAQUINA:
        print("Ganó la máquina.")
    else:
        print("Empate.")

    if historial:
        total_sin = sum(m["nodos_sin_poda"] for m in historial)
        total_con = sum(m["nodos_con_poda"] for m in historial)
        print(f"\nResumen de la partida (profundidad límite {profundidad}):")
        print(f"  Nodos evaluados sin poda: {total_sin}")
        print(f"  Nodos evaluados con poda: {total_con}")
        print(f"  Reducción total: {100 * (1 - total_con / total_sin):.1f} %")
