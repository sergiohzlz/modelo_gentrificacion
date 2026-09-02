# coding:utf8
import numpy as np
from numpy import random 

class Agente(object):
    """
    clase para los agentes que tiene asociado
    una posición [tupla (i,j)] y también un
    real representando un salario 
    """
    def __init__(self, t : tuple):
        """
        Al inicial le pasamos la posición en la que
        vive
        """
        self._pos = t
        self._salario = -1

    def __repr__(self):
        return f"agente en {(self._pos[0], self._pos[1])} con salario {self._salario}"

    @property
    def salario(self) -> float:
        return self._salario
    
    @salario.setter
    def salario(self, r : float) -> None:
        """
        Asignamos el salario definido en r
        """
        self._salario = r
    
    @property
    def posicion(self) -> tuple:
        return self._pos
    
    @posicion.setter
    def posicion(self, t) -> None:
        self._pos = t

class Vecindario(object):

    def __init__(self, 
                 n      : int,      # dimensiones
                 P      : list,     # lista de agentes
                 params : dict,     # 
                 k      : int = 3,  # capacidad de carga de cada celda 
                 pad    : int = 2,
                 rng          = None):
        """
        Constructor

        Params
        - n      : dimension de la matriz para establecer un mundo cuadrado
        - P      : lista de agentes previamente generada
        - params : parametros de la distribución de valores de la renta 
        - k      : capacidad de carga por celda k=5
        - pad    : padding de celda 
        - rng None simulador de aleatoriedad de numpy
        """
        assert 2*pad < n, "El padding debe ser menor al tamaño de la matriz"
        assert params['tipo'] in ['gaussian', 'power_law', 'binomial'], "f debe ser gaussian binomial o power_law"

        self._pad    = pad
        self._params = params
        self._n      = n
        self._P      = P
        self._k      = k 
        self._rng    = random.default_rng() if rng is None else rng

        self.V        = np.zeros((n,n))
        datos         = self._genera_V(params)
        self.V[pad:n-pad, pad:n-pad] = datos    # matriz de renta con un padding ya establecido
        self.agentes  = None

    def __repr__(self):
        return f"Vecindario {self.V.shape} con {len(self._P)} agentes"

    @property 
    def size(self):
        return self._n 

    @property
    def carga(self):
        return self._k 

    @property
    def distrib_renta(self):
        return self._params['tipo']

    
    def _genera_V(self, params : dict) -> np.array:
        """
        Función para generar el entorno inmobiliario 
        """
        n = self._n
        rng = self._rng

        # interior
        pad = self._pad
        shp = (n -2*pad, n-2*pad)

        tipo = params['tipo']
        if tipo =='gaussian':
            gauss_mean, gauss_std = params['gauss_mean'], params['gauss_std']
            datos = rng.normal(loc=gauss_mean, scale=gauss_std, size=(shp[0], shp[1]))
            datos = np.abs(datos)
        elif tipo == 'power_law':
            pl_alpha = params['pl_alpha']
            datos = rn.pareto(pl_alpha, size=shp) + 1
        elif tipo == 'binomial':
            bin_n, bin_p = params['bin_n'], params['bin_p']
            datos = rng.binomial(n=bin_n, p=bin_p, size=shp)

        else:
            raise ValueError("La distribucion `tipo` de ser gaussian binomial o power_law")

        return datos

    def _distribuye_pobladores(self):
        """
        Aloja a los agentes en un diccionario cuya llave es la entrada en la matriz 
        self.V

        Cada celda puede contener hasta k diferentes agentes y no debe haber nada en 
        la región de padding 

    
        El resultado se almacena en self.agentes como:

        {(i,j): [agente1, agente2, ...]}

        donde (i,j) es la posición de la celda.    
        """
        n = self._n
        k = self._k
        pad = self._pad
        rng = self._rng
        P = self._P

        # posiciones posibles para ubicar a los agentes
        posiciones = [
            (i, j) for i in range(pad, n-pad) for j in range(pad, n-pad)
        ]
        # Capacidad total disponible
        capacidad = len(posiciones) * k

        self.agentes = {}
        ocupacion = {
            pos: 0   for pos in posiciones
        }

        for ag in P:
            if len(P) > capacidad:
                raise ValueError("No hay suficiente capacidad para alojar a todos los agentes")

            # Elegimos una posición aleatoria
            pos = rng.choice(posiciones)
            while ocupacion[pos] >= k:
                pos = rng.choice(posiciones)

            # Asignamos la posición al agente
            ag.posicion = pos
            ocupacion[pos] += 1

            # Añadimos el agente al diccionario
            if pos not in self.agentes:
                self.agentes[pos] = []
            self.agentes[pos].append(ag)
            


