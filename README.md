# Modelo de inquilinos

Este proyecto implementa una simulación básica de agentes autónomos en un entorno de malla finita. 
Los agentes se mueven dentro de un vecindario bidimensional y poseen atributos como coordenadas y salario.


## 📁 Estructura del Proyecto

.
├── agentes_clase.py          # Módulo principal con las clases Agente y Vecindario
├── phd_tercer_semestre.ipynb # Script de ejemplo para ejecutar la simulación
└── README.md                # Este archivo


## 🧩 Clases Principales

### `Agente`
Clase envoltorio (`wrapper`) que representa a un agente individual dentro del vecindario.

#### Atributos
- `posicion` : `tuple` (x, y) — Posición actual del agente en la malla.
- `salario`  : `float` — Ingreso o valor económico asociado al agente.

#### Métodos Principales
| Método (@setter / @getter ) | Descripción |
|-----------------------------|-------------|
| `salario`                   | Actualiza o regresa la coordenada del agente. |
| `posicion`                  | Actualiza o Devuelve la coordenada actual. |
| `__repr__()`                | Representación en cadena del agente. |

> *Nota: La clase puede extenderse para incluir más comportamientos según las necesidades de la simulación.*

---

### `Vecindario`
Clase que gestiona el entorno de simulación y la interacción entre agentes dentro de una malla bidimensional finita.
Se establece una capa de renta con algún tipo de distribución subyacente (normal, power, binomial) $V \in \realset$
 con una periferia
(_padding_) de valor 0. Encima se establecen algunos agentes 

#### Atributos
- `dimensiones` : `tuple` (ancho, alto) — Tamaño de la malla.
- `agentes` : `list` — Lista de objetos `Agente` presentes en el vecindario.

#### Métodos Principales
| Método | Descripción |
|--------|-------------|
| `agregar_agente(agente)` | Añade un agente al vecindario. |
| `remover_agente(agente)` | Elimina un agente del vecindario. |
| `mover_agente(agente, dx, dy)` | Mueve un agente dentro de los límites de la malla. |
| `listar_agentes()` | Muestra todos los agentes con sus coordenadas y salarios. |
| `calcular_estadisticas()` | Retorna estadísticas básicas (ej. salario promedio, densidad). |
| `simular_pasos(n_pasos)` | Ejecuta la simulación durante un número determinado de pasos de tiempo. |

#### Características del Entorno
- **Malla finita**: Espacio discreto de tamaño definido.
- **Límites**: Los agentes no pueden salir de los bordes del vecindario.
- **Interacciones**: (Por implementar) Posibilidad de agregar reglas de interacción entre agentes.

---

## 🚀 Ejemplo de Uso

```python
from agentes_clase import Agente, Vecindario

# Crear vecindario de 10x10
vecindario = Vecindario(ancho=10, alto=10)

# Crear agentes
agente1 = Agente(coordenada=(2, 3), salario=50000)
agente2 = Agente(coordenada=(7, 8), salario=62000)

# Agregar agentes al vecindario
vecindario.agregar_agente(agente1)
vecindario.agregar_agente(agente2)

# Mover agente1
vecindario.mover_agente(agente1, dx=1, dy=0)

# Listar estado actual
vecindario.listar_agentes()

# Ejecutar simulación por 5 pasos
vecindario.simular_pasos(5)