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
| Método       | Descripción         | Parámetros                                         |
|--------------|---------------------|----------------------------------------------------|
|`__init__()`  | Constructor       | n (int) Dimensión de la malla. P lista de agentes ya instanciados params (dict) Para distribución de renta. k (int) Capacidad de carga por celda. pad (int) Periferia o _padding_ de malla. a, b (float) Parametros para proporción de agentes |
| `itera`      | Método para iterar asíncronamente  | dbg (boolean) True, imprime algunos valores        |
| `itera_`     | Método par aiterar síncronamente   |

---
### `Obs`

Clase con métodos para medir algunos observables

Se implementan algunos métodos que permiten sacar estadísticos sobre la malla 

#### Características del Entorno
- **Malla finita**: Espacio discreto de tamaño definido.
- **Límites**: Los agentes no pueden salir de los bordes del vecindario.
- **Interacciones**: (Por implementar) Posibilidad de agregar reglas de interacción entre agentes.

---

### `agentes_clase`

El módulo `agentes_clase` típicamente se identifica como `A` contiene las clases y algunas funciones de uso genérico como la creación de un conjunto de agentes o una función para convertir un diccionario en una matriz 

#### Métodos Principales
| Método         | Descripción                  | Parámetros                                                   |
|----------------|------------------------------|--------------------------------------------------------------|
|`crea_agentes`  | Función para crear agentes   | N=50_000, mu=5, std=1. Determinan la media de salario y su sd|
| `dict_a_array` | Función que convierte el diccionario
                                      en array  | d_pos : dict, shp : tuple -> np.array                        |


## 🚀 Ejemplo de Uso

Para crear los agentes
```python
# Usamos la función dedicada a crear N agentes
agentes = A.crea_agentes(N=36_000)
salarios = np.array([ag.salario for ag in agentes])
```

Para instanciar un experimento en una malla de 100x100 durante 10 iteraciones y con un _padding_ de 2
```python
V, obs, bins_e = A.experimento(iters=10, p=2)
```

La creación de gráficos del vecindario
```python
fig, ax = plt.subplots(1,2, figsize=(10,5))
# divider = make_axes_locatable(ax)
# cax = divider.append_axes('right', size='5%', pad=0.05)
cax = fig.add_axes([0.93, 0.3, 0.04, 0.4])

ax[0].set_title("Inicio")
im0 = ax[0].imshow(V[0], cmap='viridis')
ax[1].set_title("Fin")
im1 = ax[1].imshow(V[-1], cmap='viridis')

fig.colorbar(im1, cax=cax, orientation='vertical')
plt.show()
```

El graficado de los observables 
```python
H = obs['estres']
E = obs['remanente']
O = obs['ocupacion']

fig, ax = plt.subplots(3,1, figsize=(10,5))

# al inicio

ax[0].hist((H[0],H[-1]),  label=['inicio','fin'], bins=bins_e);
ax[0].set_title('Proporción de salario dedicado a renta con salario menor a renta')
ax[1].hist((E[0],E[-1]), label=['inicio','fin'], bins=bins_e)
ax[1].set_title('Remanente de salario después de renta')
ax[2].hist((O[0],O[-1]), label=['inicio','fin'], bins=bins_e)
ax[2].set_xticks([0,1,2,3,4])
ax[2].set_title('Ocupación')

plt.legend()
plt.tight_layout()
```
