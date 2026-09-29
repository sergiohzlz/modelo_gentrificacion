# coding:utf8
import numpy as np
from numpy import random 

class Agente(object):
    """
    clase para los agentes que tiene asociado
    una posición [tupla (i,j)] y también un
    real representando un salario 
    """
    def __init__(self):
        """
        Al inicial le pasamos la posición en la que
        vive
        """
        self._salario = -1

    def __repr__(self):
        return f"pos {tuple(self._pos)} - {float(self._salario)}"

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
        self.V[pad:n-pad, pad:n-pad] = datos          # matriz de renta con un padding ya establecido
        self._distribuye_pobladores() # distribuimos a los pobladores de V

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
    
    def _distribuye_pobladores(self, dbg=True):
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
            (i, j)
            for i in range(pad, n-pad) 
            for j in range(pad, n-pad)
        ]
        # Capacidad total disponible
        n_agentes, n_pos = len(P), len(posiciones)
        capacidad = n_pos * k
        
        # verificacion de que haya menos 
        # agentes que posiciones posibles
        if(n_agentes > capacidad):
            raise ValueError(
                f"No hay suficiente capacidad para alojar a los {n_agentes} agentes"
                f"Solo hay {capacidad} posibles lugares"
            )

        # k posibles lugares para poner 
        # los n_agentes
        lugares = rng.choice(
            capacidad,
            size=n_agentes,
            replace=False	
        )
        
        # diccionario de agentes por celda
        # aqui vamos a poner a los agentes en la celda correspondiente
        self.agentes = {}
        # cuantos hay en la celda pos for pos in posiciones
        self.ocupacion = {
            pos: 0   for pos in posiciones
        }
        if(dbg):
            print(f"Vamos a alojar a {len(P)} agentes")
        for ag, lugar in zip(P, lugares):        
            # Primeros k lugares corresponden a la primera celda
            # los siguientes k a la segunda, etc.
            pos = posiciones[lugar // k]
            ag.posicion = pos
            
            if pos not in self.agentes:
                self.agentes[pos] = []

            self.agentes[pos].append(ag)
            self.ocupacion[pos] += 1

    def __proporcion_poblacion(self, coef):
        Q = []
        return Q
    
    def itera(self, alfa, beta, dbg=True):
        """
        Método para llevar a cabo la iteración del modelo 
        Se ejecuta en 3 pasos
        1. Elección de agentes conformes C      V[i,j] <= salario  
        2. Elección de agentes inconformes I    V[i,j] >  salario 
        
        Parameters:
            - alfa : proporción de agentes conformes que serán reubicados
            - beta : proporción de agentes inconformes que serán reubicados
        """
        if not(0< alfa < 1):
            raise ValueError(f"Error en alfa {alfa}")
        if not(0< beta < 1):
            raise ValueError(f"Error en beta {beta}")
        # recuperamos las variables del objeto que vamos a ocupar
        V = self.V
        k = self._k
        rng = self._rng
        agentes = self.agentes 
        ocupacion = self.ocupacion  # diccionario de ocupacion
        
        #conjuntos de agentes 
        # C conformes e Inconformes I
        C, I = [], []
        for pos, pobladores in agentes.items():
            for agente in pobladores:
                if V[pos] <= agente.salario:
                    C.append(agente)
                else:
                    I.append(agente)
        if(dbg):
            print(f"Las poblaciones C {len(C)} e I {len(I)}")
        
        # celdas con capacidad disponible al interior 
        disponibles = [
            pos for pos, n in ocupacion.items()
            if n<k
        ]

        # for i in range(self._n):
        #     for j in range(self._n):
        #         pos =(i,j)
        #         ocupacion = len(self.agentes.get(pos, []))
        #         if ocupacion < k:
        #             disponibles.append(pos)
                    
        # ---------------------------------------------------------
        # Pobladores C: Desean cambiarse porque pueden 
        # (sal >= V[i,j])
        # ---------------------------------------------------------
        prop_C = int(alfa * len(C))                     # proporcion de conformes
        if ((prop_C > 0) and (len(disponibles) > 0)):
            n_C = min(prop_C, len(C))
            # escogemos los indices 
            idxC = rng.choice(
                len(C),
                size=n_C,
                replace=False
            )
            seleccionados_C = [C[i] for i in idxC]     # <- poblacion seleccionada de C
            if(dbg):
                print(f"Len seleccionados C {len(seleccionados_C)}")

            # ahora vamos a actualizar su posicion 
            # eligiendo una celda disponible al azar
            # asegurandonos de que no se llene la celda
            for conforme in seleccionados_C:
                # solamente usamos celdas que todavía tienen capacidad
                if not disponibles:
                    break
                idx = rng.integers(len(disponibles))
                posnva = disponibles[idx]

                # sacar agente de su posición actual
                posact = conforme.posicion
                agentes[posact].remove(conforme)      # quitamos al agente de la celda actual
                ocupacion[posact] -= 1                # indicamos que hay un agente menos en la celda actual

                # agregarlo a la nueva posición
                agentes.setdefault(posnva, []).append(conforme)
                ocupacion[posnva] += 1                # indicamos que hay un agente más en la nueva celda

                conforme.posicion = posnva            # le actualizamos la posición al agente

                # si se llena, eliminamos la celda de disponibles
                if(ocupacion[posnva]) >= k:
                    disponibles.remove(posnva)

        # ---------------------------------------------------------
        # Pobladores I: su salario es menor que la renta reuerida
        # sal < V[i,j]
        # ---------------------------------------------------------

        prop_I = int(beta * len(I))  # propocion de inconformes

        # mismo caso que el anterior, pero ahora para los inconformes
        if prop_I > 0:
            idxI = rng.choice(
                len(I),
                size=prop_I,
                replace=False
            )
            seleccionados_I = [I[i] for i in idxI]  # <- poblacion seleccionada de I
            if(dbg):
                print(f"Len seleccionados I {len(seleccionados_I)}")

            # vamos a formar un diccionario de celdas con capacidad < k
            # y ordenadas por renta V[i,j] de menor a mayor
            # siempre y cuando la capacidad sea menor que k
            disponibles = [
                pos for pos, n in ocupacion.items() 
                if n<k
            ]
            disponibles.sort(key=lambda pos: V[pos])  # ordenamos por renta
            
            # para cada inconforme, vamos a intentar alojarlo en una celda que pueda pagar
            # y que tenga capacidad
            for inconforme in seleccionados_I:
                salario = inconforme.salario
                #celdas que puede pagar y que tienen capacidad
                candidatas = [
                    pos for pos in disponibles
                    if V[pos] <= salario
                ]

                if not candidatas:
                    if(dbg):
                        print(f"No hay celdas disponibles para el agente {inconforme}")
                    continue

                idx = rng.integers(len(candidatas))
                posnva = candidatas[idx]

                # posición anterior
                posact = inconforme.posicion
                agentes[posact].remove(inconforme)
                ocupacion[posact] -= 1
                
                # actualizar posición
                ocupacion[posnva] += 1
                agentes.setdefault(posnva, []).append(inconforme)
                inconforme.posicion = posnva

                if(ocupacion[posnva]) > k:
                    disponibles.remove(posnva)

        self.ocupacion = ocupacion
        self.agentes = agentes
