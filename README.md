# Laboratorio de búsqueda: 8-puzzle y Triqui

## 1. Descripción del proyecto

Este proyecto implementa y compara algoritmos clásicos de Inteligencia
Artificial en dos aplicaciones válidas:

1. **8-puzzle**, un rompecabezas de un agente resuelto mediante algoritmos
   de búsqueda.
2. **Triqui contra la máquina**, un juego de dos jugadores en el que la
   computadora decide sus movimientos mediante Minimax con poda
   alfa-beta.

El proyecto permite observar cómo cambia el rendimiento de cada algoritmo
según la dificultad del problema. Para cada búsqueda se registran:

- si se encontró una solución;
- cantidad de movimientos de la solución;
- costo total;
- nodos expandidos;
- tiempo promedio de ejecución.

El proyecto no utiliza un laberinto. El problema principal es el 8-puzzle,
que es un problema de planificación y búsqueda sobre estados.

## 2. Requisitos

- Python 3.13 o una versión compatible con el código.
- `matplotlib`, únicamente para generar las gráficas.

Si `matplotlib` no está instalado:

```bash
python -m pip install matplotlib
```

En Windows también puede utilizarse:

```bash
py -3.13 -m pip install matplotlib
```

## 3. Ejecución

### Ejecutar la aplicación

Desde la carpeta del proyecto:

```bash
python main.py
```

En Windows:

```bash
py -3.13 main.py
```

El menú permite elegir entre:

- resolver un caso de 8-puzzle;
- jugar Triqui contra Minimax.

Al resolver un puzzle se puede ejecutar un solo algoritmo o todos los
algoritmos para compararlos.

### Generar resultados y gráficas

```bash
python graficas.py
```

Este comando ejecuta los cinco algoritmos sobre todos los casos de prueba
y genera en la carpeta `resultados/`:

- `resultados.csv`;
- `nodos_expandidos.png`;
- `costo_total.png`;
- `tiempo_ejecucion.png`.

Los tiempos se promedian durante 20 ejecuciones por algoritmo y por caso.
Esto reduce el efecto de pequeñas variaciones del sistema durante la
medición.

## 4. Representación del 8-puzzle

El tablero es una matriz de 3 x 3 representada internamente como una tupla
de nueve valores:

```text
1 2 3
4 5 6
7 8 0
```

El valor `0` representa el espacio vacío. El estado objetivo utilizado en
todos los casos es:

```text
(1, 2, 3, 4, 5, 6, 7, 8, 0)
```

Un vecino se obtiene intercambiando el espacio vacío con una ficha
adyacente. Cada movimiento tiene costo 1. Por eso, en este proyecto:

```text
costo total = cantidad de movimientos
```

El módulo [mapa.py](./mapa.py) contiene la clase `Puzzle`, que valida los
estados, genera los sucesores y muestra los tableros.

## 5. Algoritmos de búsqueda utilizados

### 5.1 DFS: búsqueda en profundidad

DFS utiliza una pila LIFO. Siempre expande el último estado agregado.

Características:

- puede encontrar una solución sin explorar todo el espacio;
- no garantiza la solución con menor cantidad de movimientos;
- utiliza memoria asociada principalmente a los estados visitados y la pila;
- su resultado depende del orden de generación de sucesores.

En este proyecto los sucesores se ordenan usando la distancia Manhattan y
se apilan en orden inverso. Esto sigue siendo DFS porque la estructura de
control continúa siendo una pila y no se utiliza el costo acumulado para
seleccionar globalmente los estados. El orden ayuda a evitar que los casos
de demostración recorran una rama innecesariamente extensa.

Por lo tanto, DFS puede devolver una solución más larga que BFS o A*, como
ocurre en el caso difícil.

### 5.2 BFS: búsqueda en amplitud

BFS utiliza una cola FIFO y explora el espacio por niveles:

1. primero el estado inicial;
2. después los estados a un movimiento;
3. luego los estados a dos movimientos;
4. y así sucesivamente.

Como todos los movimientos tienen costo 1, BFS garantiza encontrar una
solución con el menor número de movimientos si existe. Su desventaja es
que puede almacenar y expandir muchos estados.

### 5.3 BCU: búsqueda de costo uniforme

La búsqueda de costo uniforme utiliza una cola de prioridad y siempre
expande el estado con menor costo acumulado `g(n)`.

En este proyecto todos los movimientos cuestan 1, por lo que BCU produce
soluciones óptimas igual que BFS. Sin embargo, puede tener un tiempo
ligeramente diferente debido al uso de la cola de prioridad.

BCU es especialmente útil como referencia cuando los movimientos tienen
costos diferentes. En el 8-puzzle actual todos tienen el mismo costo.

### 5.4 A*

A* combina el costo acumulado desde el inicio con una estimación del costo
restante:

```text
f(n) = g(n) + h(n)
```

Donde:

- `g(n)` es el costo real desde el estado inicial hasta `n`;
- `h(n)` es la heurística;
- `f(n)` es la prioridad usada para elegir el siguiente estado.

Cuando la heurística es admisible y consistente, A* garantiza una solución
óptima.

El módulo [algoritmos.py](./algoritmos.py) contiene una implementación
genérica de A* y dos funciones que la utilizan con heurísticas diferentes.

## 6. Heurísticas utilizadas

### 6.1 Heurística Manhattan

Para cada ficha se calcula cuántas filas y columnas debe recorrer para
llegar a su posición objetivo. Después se suman esas distancias:

```text
h(n) = suma de distancias Manhattan de las fichas
```

El espacio vacío no se cuenta.

Ejemplo conceptual: si una ficha está a dos filas y una columna de su
posición final, contribuye con `2 + 1 = 3`.

Esta heurística:

- no cuenta movimientos de fichas entre sí;
- nunca sobreestima el número real de movimientos;
- es admisible;
- normalmente informa mejor a A* que contar únicamente las fichas
  incorrectas.

### 6.2 Heurística de fichas fuera de lugar

Esta heurística cuenta cuántas fichas no están en su posición final:

```text
h(n) = cantidad de fichas incorrectas
```

El espacio vacío no se cuenta.

Es una heurística admisible porque cada ficha incorrecta necesita al menos
un movimiento para corregirse. Sin embargo, es menos informada que la
distancia Manhattan: no diferencia entre una ficha desplazada una posición
y otra desplazada varias posiciones.

En la aplicación aparece como **A* Propia**.

## 7. Implementación de Minimax

El modo de Triqui se encuentra en
[minimax.py](./minimax.py). El usuario juega con `X` y la máquina con `O`.

Minimax considera el juego como un árbol de estados:

- cada nodo es una configuración del tablero;
- cada hijo es un movimiento posible;
- los turnos alternan entre el jugador humano y la máquina;
- las hojas representan una victoria, una derrota o un empate.

La evaluación utilizada es:

```text
+10  si gana la máquina
-10  si gana el jugador humano
  0  si hay empate
```

La máquina intenta maximizar la puntuación y el jugador humano se modela
como un oponente que intenta minimizarla.

El flujo para elegir un movimiento es:

1. obtener las casillas libres;
2. simular cada movimiento posible de la máquina;
3. evaluar recursivamente las respuestas del jugador;
4. propagar la mejor puntuación de cada nivel;
5. elegir el movimiento con mayor puntuación.

### Poda alfa-beta

La poda alfa-beta evita evaluar ramas que ya no pueden mejorar la decisión
actual:

- `alfa` representa la mejor puntuación garantizada para el maximizador;
- `beta` representa la mejor puntuación garantizada para el minimizador;
- si `beta <= alfa`, la rama restante se descarta.

La poda alfa-beta no cambia la decisión de Minimax; solamente reduce la
cantidad de estados evaluados.

## 8. Casos de prueba

Los casos están definidos en [mapas_prueba.py](./mapas_prueba.py):

| Caso | Descripción |
|---|---|
| 8-puzzle fácil | Requiere pocos movimientos y sirve para verificar rápidamente el programa. |
| 8-puzzle medio | Permite comparar diferencias de expansión entre DFS, BFS y A*. |
| 8-puzzle difícil | Requiere una búsqueda más amplia y muestra la diferencia entre una solución de DFS y una solución óptima. |
| 8-puzzle sin solución | Tiene dos fichas intercambiadas y no puede alcanzar el estado objetivo. |

El caso sin solución es importante porque comprueba que los algoritmos
pueden terminar indicando correctamente que no existe una solución.

## 9. Resumen de resultados

Los resultados de esta sección corresponden al archivo
[resultados/resultados.csv](./resultados/resultados.csv), generado con 20
repeticiones por medición. Los tiempos pueden cambiar ligeramente según
el equipo y la carga del sistema.

### 9.1 Movimientos encontrados

| Caso | DFS | BFS | BCU | A* Manhattan | A* Propia |
|---|---:|---:|---:|---:|---:|
| Fácil | 2 | 2 | 2 | 2 | 2 |
| Medio | 8 | 8 | 8 | 8 | 8 |
| Difícil | 80 | 20 | 20 | 20 | 20 |
| Sin solución | - | - | - | - | - |

Interpretación:

- BFS, BCU y las dos versiones de A* encuentran soluciones óptimas en los
  casos resolubles.
- DFS encuentra una solución válida, pero no necesariamente óptima.
- En el caso difícil, DFS necesita 80 movimientos frente a los 20 de los
  algoritmos óptimos.
- El caso sin solución no tiene costo ni cantidad de movimientos.

### 9.2 Nodos expandidos

| Caso | DFS | BFS | BCU | A* Manhattan | A* Propia |
|---|---:|---:|---:|---:|---:|
| Fácil | 3 | 7 | 7 | 3 | 3 |
| Medio | 9 | 311 | 311 | 13 | 19 |
| Difícil | 82 | 55.409 | 55.409 | 283 | 3.667 |
| Sin solución | 181.440 | 181.440 | 181.440 | 181.440 | 181.440 |

En el caso difícil, DFS encuentra su solución con pocas expansiones, pero
la solución es más larga. A* Manhattan expande muchos menos nodos que BFS
y BCU, manteniendo la solución óptima.

El valor 181.440 del caso sin solución corresponde al conjunto de estados
alcanzables del 8-puzzle desde una paridad determinada. Como el estado
objetivo pertenece a la otra paridad, ningún algoritmo puede encontrarlo.

### 9.3 Tiempos medidos

Los siguientes valores están expresados en milisegundos y son los tiempos
promedio registrados en la ejecución que produjo el CSV actual:

| Caso | DFS | BFS | BCU | A* Manhattan | A* Propia |
|---|---:|---:|---:|---:|---:|
| Fácil | 0.0432 | 0.0257 | 0.0353 | 0.0416 | 0.0238 |
| Medio | 0.1775 | 1.0498 | 1.5570 | 0.2056 | 0.1752 |
| Difícil | 1.7045 | 205.9360 | 343.3239 | 5.9798 | 37.7350 |
| Sin solución | 3702.6964 | 650.4182 | 1129.3194 | 2274.9815 | 1607.2316 |

El caso sin solución es más costoso porque todos los algoritmos deben
agotar los estados alcanzables antes de determinar que no existe un
camino. Los tiempos son una referencia experimental, no una constante
matemática: dependen de la versión de Python, el procesador y otros
procesos ejecutándose en el equipo.

## 10. Interpretación general

Los resultados muestran los siguientes compromisos:

- **DFS** puede encontrar una solución con pocas expansiones, pero no
  garantiza que sea corta.
- **BFS** garantiza la solución mínima cuando cada movimiento cuesta lo
  mismo, aunque puede consumir muchos nodos.
- **BCU** también garantiza el menor costo y es la opción general cuando
  los movimientos tienen costos diferentes.
- **A* Manhattan** ofrece el mejor equilibrio en los casos difíciles:
  mantiene la optimalidad y reduce considerablemente los nodos expandidos.
- **A* Propia** es correcta y admisible, pero su heurística aporta menos
  información que Manhattan.
- **Minimax** permite resolver una aplicación competitiva de dos jugadores,
  en lugar de limitar el proyecto a problemas de un solo agente.

## 11. Estructura de archivos

| Archivo | Responsabilidad |
|---|---|
| [main.py](./main.py) | Menú principal para 8-puzzle y Triqui. |
| [mapa.py](./mapa.py) | Modelo del estado y movimientos del 8-puzzle. |
| [mapas_prueba.py](./mapas_prueba.py) | Casos de prueba reproducibles. |
| [algoritmos.py](./algoritmos.py) | DFS, BFS, BCU y A*. |
| [minimax.py](./minimax.py) | Triqui, Minimax y poda alfa-beta. |
| [comparador.py](./comparador.py) | Ejecución repetida y tabla comparativa. |
| [graficas.py](./graficas.py) | Generación del CSV y las gráficas. |
| [algoritmos_basicos.py](./algoritmos_basicos.py) | Implementaciones didácticas auxiliares de BFS y DFS sobre grafos genéricos. |
| [resultados/](./resultados/) | CSV y gráficas generadas. |

## 12. Conclusión

El proyecto integra búsqueda no informada, búsqueda de costo uniforme,
búsqueda informada y búsqueda adversarial. El 8-puzzle permite comparar
formalmente la calidad de las soluciones y el costo computacional de cada
algoritmo, mientras que Triqui demuestra el uso de Minimax para tomar
decisiones frente a un oponente.

