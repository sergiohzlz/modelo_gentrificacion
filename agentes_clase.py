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
                 a      : float = 0.1,
                 b      : float = 0.2,
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
        assert 0<a<1, f"Error en a {a}"
        assert 0<b<1, f"Error en b {b}"
        
        self._pad    = pad
        self._params = params
        self._n      = n
        self._P      = P
        self._k      = k 
        self._a      = a
        self._b      = b
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
        # al inicio de la distribucion 
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
            
        # Agregamos las posiciones del padding
        for i in range(n):
            for j in range(n):
                if i < pad or i >= n-pad or j < pad or j >= n-pad:
                    self.ocupacion[(i, j)] = 0


    def itera(self, dbg=True):

        """
        Método para llevar a cabo la iteración del modelo 
        Se ejecuta en 3 pasos
        1. Elección de agentes conformes C      V[i,j] <= salario  
        2. Elección de agentes inconformes I    V[i,j] >  salario 
        
        Parameters:
            - alfa : proporción de agentes conformes que serán reubicados
            - beta : proporción de agentes inconformes que serán reubicados
        """

        # recuperamos las variables del objeto que vamos a ocupar
        alfa = self._a
        beta = self._b
        V = self.V
        k = self._k
        rng = self._rng
        agentes = self.agentes 
        ocupacion = self.ocupacion  # diccionario de ocupacion
        
        #conjuntos de agentes 
        # C conformes e Inconformes I
        C, I = [], []
        for pos, pobladores in agentes.items():
            vpos = V[pos]
            for agente in pobladores:
                if vpos <= agente.salario:
                    C.append(agente)
                else:
                    I.append(agente)
        if(dbg):
            print(f"Las poblaciones C {len(C)} e I {len(I)}")
        

        prop_C = int(alfa * len(C))  # proporcion de conformes
        prop_I = int(beta * len(I))  # propocion de inconformes

        n_C = min(prop_C, len(C))  # escogemos los indices 
        seleccionados_C = rng.choice(C, size=n_C, replace=False) 
        n_I = min(prop_I, len(I))  # escogemos los indices
        seleccionados_I = rng.choice(I, size=n_I, replace=False)

        selected_agents = list(seleccionados_C) + list(seleccionados_I)
        selected_agents.sort(key=lambda ag: ag.salario, reverse=True)  # ordenamos por salario

        disponibles = []

        for pos, n in ocupacion.items():
            espaciosabiertos = k - n
            if espaciosabiertos > 0:
                precio = self.V[pos]
                posycosto = tuple([pos, precio])
                disponibles += espaciosabiertos * [posycosto]

        # Primero la gente se sale de donde está, se queda "flotando"
        for agent in selected_agents:
            disponibles.append((agent.posicion, self.V[agent.posicion]))  # agregamos la posición actual del agente con su precio

        disponibles.sort(key=lambda posycosto: posycosto[1], reverse=True)  # ordenamos por renta


        # selected_agents están ordenados por salario de mayor a menor
        # disponibles están ordenados por renta de mayor a menor
       
        # Todos los que están flotando, se van a intentar reubicarse

        for agent in selected_agents:
            pos_seleccionada, disponibles = self._seleccionar_entre_disponibles(disponibles, agent.salario)
            if pos_seleccionada is not None:
                # posición anterior
                posact = agent.posicion
                agentes[posact].remove(agent)
                ocupacion[posact] -= 1
                
                # actualizar posición
                ocupacion[pos_seleccionada] += 1
                agentes.setdefault(pos_seleccionada, []).append(agent)
                agent.posicion = pos_seleccionada

        



    def _seleccionar_entre_disponibles(self, disponibles, salario):
        """
        Selecciona una celda disponible para un agente con salario dado
        Parameters:
            - disponibles : lista de tuplas (pos, precio) de celdas disponibles, ordenadas de mayor a menor precio
            - salario     : salario del agente que busca una celda
        """
        idxbreak = 0
        for pos, precio in disponibles:
            if precio > salario:
                break
            idxbreak += 1
        disponibles_aptas = disponibles[idxbreak:]
    
        if not disponibles_aptas:
            return None, disponibles  # No hay celdas aptas


        idx = self._rng.choice(len(disponibles_aptas))
        pos_seleccionada = disponibles_aptas[idx][0]
        # Remover la celda seleccionada de la lista de disponibles
        disponibles_ = disponibles_aptas[:idx] + disponibles_aptas[idx+1:]

        return pos_seleccionada, disponibles_


    def itera_(self, dbg=True):
        """
        Método para llevar a cabo la iteración del modelo 
        Se ejecuta en 3 pasos
        1. Elección de agentes conformes C      V[i,j] <= salario  
        2. Elección de agentes inconformes I    V[i,j] >  salario 
        
        Parameters:
            - alfa : proporción de agentes conformes que serán reubicados
            - beta : proporción de agentes inconformes que serán reubicados
        """

        # recuperamos las variables del objeto que vamos a ocupar
        alfa = self._a
        beta = self._b
        V = self.V
        k = self._k
        rng = self._rng
        agentes = self.agentes 
        ocupacion = self.ocupacion  # diccionario de ocupacion
        
        #conjuntos de agentes 
        # C conformes e Inconformes I
        C, I = [], []
        for pos, pobladores in agentes.items():
            vpos = V[pos]
            for agente in pobladores:
                if vpos <= agente.salario:
                    C.append(agente)
                else:
                    I.append(agente)
        if(dbg):
            print(f"Las poblaciones C {len(C)} e I {len(I)}")
        
        # celdas con capacidad disponible al interior 
        # disponibles = [
        #     pos for pos, n in ocupacion.items()
        #     if n<k
        # ]
        disponibles = []
        for pos, n in ocupacion.items():
            espaciosabiertos = k - n
            if espaciosabiertos > 0:
                disponibles += espaciosabiertos * [pos]

        rng.shuffle(disponibles)  # barajamos las celdas disponibles

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

                posnva = disponibles.pop()

                # sacar agente de su posición actual
                posact = conforme.posicion
                agentes[posact].remove(conforme)      # quitamos al agente de la celda actual
                ocupacion[posact] -= 1                # indicamos que hay un agente menos en la celda actual

                # agregarlo a la nueva posición
                agentes.setdefault(posnva, []).append(conforme)
                ocupacion[posnva] += 1                # indicamos que hay un agente más en la nueva celda

                conforme.posicion = posnva            # le actualizamos la posición al agente


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

            # disponibles.sort(key=lambda pos: V[pos])  # ordenamos por renta
            
            # para cada inconforme, vamos a intentar alojarlo en una celda que pueda pagar
            # y que tenga capacidad
            for inconforme in seleccionados_I:
                salario = inconforme.salario
                #celdas que puede pagar y que tienen capacidad
                # y cumplen con ser pagables por el agente
                disponibles = [
                    pos for pos, n in ocupacion.items() 
                    if (n<k and V[pos] <= salario)                    
                ]
                # candidatas = [
                #     pos for pos in disponibles
                #     if V[pos] <= salario
                # ]

                if not disponibles:
                    if(dbg):
                        print(f"No hay celdas disponibles para el agente {inconforme}")
                    continue

                idx = rng.integers(len(disponibles))
                posnva = disponibles[idx]

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
        
class Obs(object):

    @staticmethod
    def fd_bins(data):
        """
        Método Freedman–Diaconis para calcular número de bins para histograma
        """
        n = len(data)
        if(n<2):
            return 1
        rango = data.max() - data.min()
        if(rango==0):
            return 1
        iqr = np.percentile(data, 75) - np.percentile(data, 25)
        if iqr == 0:
            return max(1, int(np.ceil(np.sqrt(n))))
        h = 2 * iqr / n**(1/3)
        return int(np.ceil(rango / h))  
    
    @staticmethod
    def ocupacion(V):
        """
        Ocupación en cada celda 
        Returns:
        Tuple(np.array, float)
        """
        data = np.array(list(V.ocupacion.values()))
        nbins = Obs.fd_bins(data)
        return data, nbins
    
    @staticmethod
    def hacinamiento(V, k=4):
        """
        Hacinamiento de una celda en V[i,j]. Proporción de agentes
        que usan la celda respecto de la capaciadad 
        
        Returns:
        Tuple(np.array, float)
        """
        O, nbins = Obs.ocupacion(V)
        data = O/k
        return data, nbins

    @staticmethod
    def estres(V, fbins=fd_bins) -> list:
        """
        Observables que mide
        1. Estres por agente se define como el porcentaje de salario dedicado a renta
           en todos los agentes que el salario <= Renta
        2. Remanente que se define como la cantidad de salario remantente después
           de pagar la renta
           
        Returns:
        list(np.array) con [1 , 2]
        """
        estresados   = []
        remanente    = []
        for cel in V.agentes:
            # print(f"{cel} : {len(V.agentes[cel])} - renta {V.V[cel]}")
            por_celda    = [(ag.salario, V.V[cel])  
                            for ag in V.agentes[cel] ]
            estresados   += [x[0] / x[1] for x in por_celda if x[0] <= x[1]]
            remanente    += [x[0]-x[1]   for x in por_celda]
        a_estres, a_reman = np.array(estresados), np.array(remanente)
        return a_estres, a_reman, Obs.fd_bins(a_estres)

# funciones generales
def dict_a_array(d_pos : dict, shp : tuple)-> np.array:
    M = np.zeros(shp)
    for k,v in  d_pos.items():
        M[k] = v
    return M

def crea_agentes(N=50_000, mu=5, std=1):
    agentes = []
    salarios = std*np.random.randn(N) + mu
    salarios = np.clip(salarios, a_min=0, a_max=salarios.max())
    for i in range(N):
        ag = Agente()
        ag.salario = salarios[i]
        agentes.append(ag)
    return agentes


import datetime
def experimento(a=0.1,       b=0.2, k=4, n=100, 
                iters=1_000, N=30_000, 
                pad=2, mu=5, p=50, std=1):
    """
    Instancia de un experimento con los parámetros
    n      = tamaño de la malla
    mu     = valor medio del salario de cada agente
    iters  = cantidad de agentes 
    M      = cantidad de iteraciones
    a      = alfa
    b      = beta 
    k      = capacidad de carga
    p      = con qué frecuencia se reporta en pantalla
    """

    T = np.zeros((iters,n,n))
    observables = {'estres'    : [],
                   'remanente' : [],
                   'ocupacion' : []}
    agentes = crea_agentes(N=N, mu=mu, std=std)
    n_ags = len(agentes)
    print(f"Generando vecindario de {n}^2 capacidad de carga {k} y {N} agentes")
    V = Vecindario(n=n,
                   k=k,
                   P=agentes,                             
                   params={'tipo' : 'gaussian', 'gauss_mean': mu, 'gauss_std': std}, 
                   a = a, 
                   b = b,
                   pad=pad)
    T[0] = dict_a_array(V.ocupacion, (n,n))
    e, h, bins_e = Obs.estres(V)
    o, bins_o    = Obs.ocupacion(V)
    observables['estres'].append(e)
    observables['remanente'].append(h)
    observables['ocupacion'].append(o)


    print(f"Corriendo las {iters} iteraciones")
    for j in range(1,iters):
        dinititer = datetime.datetime.now()
        if(not j%p):
            print(f"Iteracion {j}")
            e,h, _ = Obs.estres(V)
            o, _   = Obs.ocupacion(V)
            observables['estres'].append(e)
            observables['remanente'].append(h)
            observables['ocupacion'].append(o)
        V.itera(dbg=False)
        T[j] = dict_a_array(V.ocupacion, (n,n))
        denditer = datetime.datetime.now()
        print(f"\t\tTiempo de iteracion {j} {(denditer-dinititer).total_seconds()} segundos")



    print(f"--> Iteracion {iters} <--")
    
    return T, observables, bins_e
