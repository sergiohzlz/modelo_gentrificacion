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
Clase envoltorio (`wrapper`) que representa a un agente individual dentro del vecindario con 
salario y posicion

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
Clase que gestiona el entorno de simulación y la interacción entre agentes dentro de una malla 
bidimensional finita.
Se establece una capa de renta con algún tipo de distribución subyacente (normal, power, binomial) 
$V \in \mathcal{R}^{n \times n}$
y también se considera una periferia (_padding_) de valor 0. 
Cada celda puede alojar a `k` posibles agentes (_capacidad de carga_).

Al tiempo `t=0` se van distribuir los agentes respetando las condiciones de cada celda. En la periferia no debe haber agentes

Después se itera una cantidad fija de iteraciones. 

#### Atributos
- `size`          :  — Tamaño de la malla.
- `carga`         : `int` — k agentes por celda.
- `distrib_renta` : `str` — Tipo de distribución.

#### Métodos Principales
| Método     | Descripción         | Parámetros                                         |
|------------|---------------------|----------------------------------------------------|
|`__init__()`  | Constructor       | n (int) Dimensión de la malla. P lista de agentes ya instanciados params (dict) Para distribución de renta. k (int) Capacidad de carga por celda. pad (int) Periferia o _padding_ de malla. a, b (float) Parametros para proporción de agentes |
| `itera`     | Método para iterar  | dbg (boolean) True, imprime algunos valores        |
| ``     |             |

---
### `Obs`

Clase con métodos para medir algunos observables

Se implementan algunos métodos que permiten sacar estadísticos sobre la malla 

#### Características del Entorno
- **Malla finita**: Espacio discreto de tamaño definido.
- **Límites**: Los agentes no pueden salir de los bordes del vecindario.
- **Interacciones**: (Por implementar) Posibilidad de agregar reglas de interacción entre agentes.

---

## 🚀 Ejemplo de Uso

```python
