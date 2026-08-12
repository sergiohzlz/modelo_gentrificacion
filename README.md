# Modelo de inquilinos

Este proyecto implementa una simulación básica de agentes autónomos en un entorno de malla finita. 
Los agentes se mueven dentro de un vecindario bidimensional y poseen atributos como coordenadas y salario.


## 📁 Estructura del Proyecto
```
.
├── agentes_clase.py          # Módulo principal con las clases Agente y Vecindario
├── phd_tercer_semestre.ipynb # Script de ejemplo para ejecutar la simulación
└── README.md                # Este archivo
```


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
Se establece una capa de renta con algún tipo de distribución subyacente (normal, power, binomial) $V \in \mathcal{R}^{n \times n}$
 con una periferia (_padding_) de valor 0. Cada celda puede alojar a `k` posibles agentes.

 Al tiempo `t=0` se van distribuir los agentes respetando las condiciones de cada celda. En la periferia no debe haber agentes


#### Atributos
- `size`          :  — Tamaño de la malla.
- `carga`         : `int` — k agentes por celda.
- `distrib_renta` : `str` — Tipo de distribución.

#### Métodos Principales
| Método | Descripción |
|--------|-------------|
| ``     |             |

#### Características del Entorno
- **Malla finita**: Espacio discreto de tamaño definido.
- **Límites**: Los agentes no pueden salir de los bordes del vecindario.
- **Interacciones**: (Por implementar) Posibilidad de agregar reglas de interacción entre agentes.

---

## 🚀 Ejemplo de Uso

```python
