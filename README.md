# Proyecto 1 – Algoritmos de búsqueda: 8-puzzle con costos y Triqui

Curso: Inteligencia Artificial – Universidad del Valle (2026)

## Integrantes

| Nombre | Código |
|---|---|
| Jhon Perlaza | 2456529 |
| Alejandro Montero | 2610130 |
| Juan E. Pereira | 2569459 |

## 1. Descripción del proyecto

La aplicación tiene dos modos:

1. **8-puzzle con costos por ficha** (un agente). Se resuelve con DFS, BFS,
   búsqueda de costo uniforme (BCU) y A* con dos heurísticas.
2. **Triqui contra la máquina** (dos jugadores por turnos). La computadora
   decide con Minimax con poda alfa-beta, función de evaluación y
   profundidad límite.

Para cada búsqueda del 8-puzzle se muestran: si hubo solución, nodos
expandidos, memoria (estados almacenados), pasos (profundidad), costo total,
si el costo es óptimo y el tiempo de ejecución. En el triqui, cada jugada de
la máquina muestra los nodos evaluados **con y sin poda** y el porcentaje de
reducción.

Todos los algoritmos fueron programados por el grupo; no se usan librerías
que resuelvan las búsquedas.

## 2. Requisitos

- Python 3.10 o superior (probado con Python 3.13).
- `matplotlib`, únicamente para `graficas.py`. La aplicación principal no
  necesita librerías externas.

```bash
python -m pip install matplotlib
```

En Windows también puede utilizarse `py -3.13 -m pip install matplotlib`.

## 3. Ejecución

### Aplicación interactiva

```bash
python main.py
```

En Windows: `py -3.13 main.py`.

Menú principal:

1. **Resolver un 8-puzzle**: se elige el caso de prueba y el algoritmo
   (DFS, BFS, BCU, A* Manhattan, A* Propia) o *Todos* para compararlos. Se
   imprime la tabla de métricas, las fichas movidas y, si se desea, los
   tableros paso a paso.
2. **Jugar triqui contra Minimax**: se elige la profundidad límite (1 a 9,
   por defecto 4) y quién empieza. Las casillas se numeran del 1 al 9.

### Resultados y gráficas

```bash
python graficas.py
```

Ejecuta los cinco algoritmos sobre los cinco casos (20 repeticiones para
promediar el tiempo) y mide Minimax con y sin poda. Tarda cerca de dos
minutos, sobre todo por el caso sin solución. Genera en `resultados/`:
`resultados.csv`, `minimax.csv`, `nodos_expandidos.png`, `costo_total.png`,
`memoria.png`, `tiempo_ejecucion.png` y `minimax_poda.png`.

## 4. Modelado del 8-puzzle

- **Estado**: tupla de 9 enteros leída fila por fila; `0` es el vacío.
- **Objetivo**: `(1, 2, 3, 4, 5, 6, 7, 8, 0)`.
- **Acciones**: deslizar hacia el vacío la ficha de arriba, abajo,
  izquierda o derecha (2 a 4 acciones según la posición del vacío).
- **Costo de una acción**: el número de la ficha movida (mover el 1 cuesta
  1, mover el 8 cuesta 8). Por eso la ruta con menos movimientos no siempre
  es la más barata.

## 5. Algoritmos

| Algoritmo | Frontera | Óptimo en | Archivo |
|---|---|---|---|
| DFS | Pila (LIFO) | No garantiza | `algoritmos.py` |
| BFS | Cola (FIFO) | Número de movimientos | `algoritmos.py` |
| BCU | Cola de prioridad por g(n) | Costo total | `algoritmos.py` |
| A* | Cola de prioridad por g(n)+h(n) | Costo total (h admisible) | `algoritmos.py` |
| Minimax α-β | Recursión en profundidad | Decisión minimax | `minimax.py` |

Heurísticas de A*:

- **A* Manhattan** (línea base): suma de distancias Manhattan de las fichas.
  Admisible porque cada movimiento cuesta al menos 1.
- **A* Propia – Manhattan ponderada**: `h(n) = Σ ficha × distancia(ficha)`.
  Admisible y consistente: la ficha t debe moverse al menos `distancia(t)`
  veces y cada movimiento suyo cuesta t; un movimiento cambia h como mucho
  en t, que es justamente su costo.

Minimax: utilidad ±100 en victoria (ajustada por profundidad), 0 en empate;
en la profundidad límite se usa una función de evaluación que suma 1 o 10
puntos por cada línea abierta con 1 o 2 fichas de la máquina y resta lo
mismo para las del humano.

## 6. Casos de prueba (`mapas_prueba.py`)

| Caso | Estado inicial | Propósito |
|---|---|---|
| Fácil | `1 2 3 / 4 5 6 / _ 7 8` | Verificación rápida (2 movimientos). |
| Medio | `1 3 6 / 5 _ 2 / 4 7 8` | 8 movimientos; diferencia las búsquedas. |
| Costo vs. pasos | `2 5 3 / 4 _ 1 / 7 8 6` | La ruta más corta (12) no es la más barata (14 movimientos, costo 44). |
| Difícil | `7 2 4 / 5 _ 6 / 8 3 1` | 20 movimientos; búsqueda amplia. |
| Sin solución | `1 2 3 / 4 5 6 / 8 7 _` | Paridad distinta; todos deben terminar sin solución. |

## 7. Resultados (`resultados/resultados.csv`)

Nodos expandidos:

| Caso | DFS | BFS | BCU | A* Manhattan | A* Propia |
|---|---:|---:|---:|---:|---:|
| Fácil | 3 | 7 | 15 | 8 | 3 |
| Medio | 9 | 311 | 387 | 140 | 13 |
| Costo vs. pasos | 13 | 2.359 | 896 | 360 | 67 |
| Difícil | 82 | 55.409 | 27.095 | 8.471 | 229 |
| Sin solución | 181.440 | 181.440 | 181.440 | 181.440 | 181.440 |

Costo total (pasos):

| Caso | DFS | BFS | BCU | A* Manhattan | A* Propia |
|---|---:|---:|---:|---:|---:|
| Fácil | 15 (2) | 15 (2) | 15 (2) | 15 (2) | 15 (2) |
| Medio | 37 (8) | 37 (8) | 37 (8) | 37 (8) | 37 (8) |
| Costo vs. pasos | 54 (12) | 54 (12) | **44 (14)** | **44 (14)** | **44 (14)** |
| Difícil | 406 (80) | 78 (20) | 78 (20) | 78 (20) | 78 (20) |

Minimax desde el tablero vacío (`resultados/minimax.csv`):

| Profundidad | Sin poda | Con poda | Reducción |
|---:|---:|---:|---:|
| 2 | 82 | 36 | 56,1 % |
| 4 | 3.610 | 635 | 82,4 % |
| 6 | 73.450 | 4.632 | 93,7 % |
| 9 | 549.946 | 20.866 | 96,2 % |

Los tiempos dependen del equipo; nodos, costos y memoria son deterministas.

## 8. Estructura de archivos

| Archivo | Responsabilidad |
|---|---|
| `main.py` | Menú principal. |
| `mapa.py` | Clase `Puzzle`: estados, sucesores y costos. |
| `mapas_prueba.py` | Casos de prueba. |
| `algoritmos.py` | DFS, BFS, BCU, A* y heurísticas. |
| `comparador.py` | Ejecución repetida, tabla comparativa y soluciones. |
| `minimax.py` | Triqui, Minimax, poda alfa-beta y métricas. |
| `graficas.py` | CSV y gráficas. |
| `algoritmos_basicos.py` | BFS y DFS didácticos sobre grafos genéricos (auxiliar). |
| `resultados/` | CSV y gráficas generadas. |

## 9. Herramientas de apoyo

Se utilizó Claude (Anthropic) como asistente para revisar el código, ajustar
el modelo de costos, completar las métricas de Minimax y redactar
documentación. El grupo revisó y validó todos los cambios.
