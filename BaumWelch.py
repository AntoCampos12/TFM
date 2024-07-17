import pandas as pd
import numpy as np

# Configuración del número de estados y las posibles observaciones

NUMERO_ESTADOS = 7  # Número de estados ocultos
# ¿Estudio de número de estados?

NUMERO_OBSERVACIONES = 7  # Número de observaciones
# Proviene de las distintas actividades que puede realizar el usuario: VALORES = {'Logon': 0, 'Logoff': 1, 'HTTP': 2, # 'USB': 3, 'Connect': 4, 'Disconnect': 5, 'EMAIL': 6}

# La distribución inicial será de 1/(numero estados)
_inicial = np.ones((1, 7))
INICIAL = _inicial / np.sum(_inicial, axis=1)

# Al realizar multiplicaciones de números muy pequeños cada vez se tiende a 0, llegando a provocar desbordamientos
# Por ello se utilizan logaritmos para evitar este comportamiento
# A partir de ahora las multiplicaciones y divisiones seguirán las propiedades de los logaritmos de forma que:
# log(a*b) = log(a) + log(b) y log(a/b) = log(a) - log(b). Puede suceder que en algún punto las probabilidades sean 0, en ese caso se añade una variable epsilon para evitar errores

def __forward(secuencia, transicion, emision, distribucion_inicial):
    # Se crea una matriz que almacenará para cada instante de la secuencia la probabilidad de colocarse en cada estado
    alpha = np.zeros((len(secuencia), NUMERO_ESTADOS))

    # El primer instante vendrá de multiplicar la distribución inicial por las probabilidades de la matriz de emisión para la observación de la secuencia
    alpha[0, :] = distribucion_inicial * emision[:, secuencia[0]]

    for t in range(1, len(secuencia)):
        for estado in range(NUMERO_ESTADOS):
            # Se calcula cada valor de alpha, multiplicando el valor anterior por la probabilidad de cada estado en la matriz de transición dado el estado 'j' (instante 't+1') 
            # y el valor de la matriz de emisión dada la observación de la secuencia en el instante 't' y el estado 'i'
            alpha[t, estado] = alpha[t - 1].dot(transicion[:, estado]) * emision[estado, secuencia[t]]

    # alpha por tanto representa la probabilidad de estar en el estado 'i' en el tiempo 't' dado el modelo y las observaciones hasta el tiempo 't'
    return alpha

def __backward(secuencia, transicion, emision):
    # Se crea una matriz que almacenará para cada instante de la secuencia la probabilidad de colocarse en cada estado
    TAM_SECUENCIA = len(secuencia)
    beta = np.zeros((TAM_SECUENCIA, NUMERO_ESTADOS))

    # se rellena la última columna con 1
    beta[TAM_SECUENCIA - 1] = np.ones((NUMERO_ESTADOS))

    
    for t in range(TAM_SECUENCIA - 2, -1, -1):
        for estado in range(NUMERO_ESTADOS):
            # El valor de beta viene dado por la multiplicación del valor del instante 't+1', la probabilidad de cada estado en la matriz de emisión dada la observación
            # y las probabilidades del estado 'j'(t+1) en la matriz de transición dado el estado 'i'
            beta[t, estado] = (beta[t + 1] * emision[:, secuencia[t + 1]]).dot(transicion[estado, :])

    return beta

def __baum_welch(secuencia, transicion, emision, distribucion_inicial, n_iter=100):
    
    TAM_SECUENCIA = len(secuencia) # Se calcula el tamaño de la secuencia

    # Por cada una de las iteraciones indicada en n_iter
    for n in range(n_iter):

        # Se realizan las funciones de backward y de forward:
        # Dada la secuencia [0,0,1 .... 4 .... 1,1,2]
        # 1.- La función forward calcula la probabilidad de obtener un estado a partir de una secuencia de observaciones desde el instante t=0 hasta el instante t=i
        alpha = __forward(secuencia, transicion, emision, distribucion_inicial)
        # 2.- La función backward calcula la probabilidad de obtener las observaciones restantes desde el instante t=i hasta el final dado un estado
        beta = __backward(secuencia, transicion, emision)

        # Se crea una matriz tridimensional x(i,j,t) que almacenará la probabilidad de estar en el estado 'i' en el tiempo 't' y en el estado 'j' en el tiempo 't+1'
        x = np.zeros((NUMERO_ESTADOS, NUMERO_ESTADOS, TAM_SECUENCIA - 1))

        # Para cada instante 't', se calculará cada x(i,j,t), que proviene de realizar la división:
        # Numerador: Probabilidad de estar en el estado 'i' en el tiempo 't' y en el estado 'j' en el tiempo 't+1' dado una observación 'O' y un modelo 'M'
        # Denominador: Probabilidad de obtener la secuencia de observaciones 'O' dado un modelo 'M'
        # Con modelo nos referimos a numero de estados, secuencia de observaciones y las probabilidad de matriz de transimisión, matriz de emisión y distribución inicial
        for t in range(TAM_SECUENCIA - 1):
            # Para cada instante 't', el denominador viene dado por la multiplicación del valor del algoritmo forward desde el instante 0 hasta 't', la probabilidad de transición,
            # la probabilidad de emisión para la observación de la secuencia en el instante 'j' y la probabilidad del algoritmo backward desde 't+1' hasta el final
            denominador = np.dot(np.dot(alpha[t, :].T, transicion) * emision[:, secuencia[t + 1]].T, beta[t + 1, :])
            for i in range(NUMERO_ESTADOS):
                # El numerador proviene de la multiplicación del valor del algoritmo forward del estado 'i' desde el instante 0 hasta 't', la matriz de transición para el estado 'i',
                # la probabilidad de emisión para la observación de la secuencia en el instante 'j' y la probabilidad del algoritmo backward desde 't+1' hasta el final
                numerador = alpha[t, i] * transicion[i, :] * emision[:, secuencia[t + 1]].T * beta[t + 1, :].T
                x[i, :, t] = numerador / denominador

        # Una vez obtenido x, sumando el eje 1 (correspondiente a los estados 'j') podemos calcular la probabilidad de estar en cada estado en el tiempo 't'
        gamma = np.sum(x, axis=1)
        
        # Para actualizar transición a las nuevas probabilidades se divide:
        # Numerador: Suma de las probabilidades de ir del estado 'i', 'j' a lo largo del tiempo
        # Denominador: Suma de las probabilidades de estar en cada estado a lo largo del tiempo
        
        denominador = np.sum(gamma, axis=1)
        transicion = np.sum(x, axis=2) / denominador.reshape((-1, 1))

        # Se calcula el valor de gamma para el último 't' y se concatena con la matriz gamma
        gamma = np.hstack((gamma, np.sum(x[:, :, TAM_SECUENCIA - 2], axis=0).reshape((-1, 1))))

        # Para actualizar emisión a las nuevas probabilidades se divide:
        # Numerador: Suma de las probabilidades de estar en cada estado a lo largo del tiempo cuando la observación en la secuencia es 'l'
        # Denominador: Suma de las probabilidades de estar en cada estado a lo largo del tiempo
        for l in range(NUMERO_OBSERVACIONES):
            emision[:, l] = np.sum(gamma[:, secuencia == l], axis=1)

        emision = np.divide(emision, denominador.reshape((-1, 1)))

    return (transicion, emision)

def iniciar_BaumWelch(dataframe):

    # Para inicializar el método de Baum Welch será necesario:
    # 1.- La secuencia de observaciones
    # 2.- La matriz de transición, que recoge la probabilidad de ir de un estado a otro
    # 3.- La matriz de emisión, que contiene la probabilidad de dado un estado obtener una observación
    # 4.- Una distribución inicial referente a las probabilidades iniciales de estar en cada estado
    
    secuencia = dataframe['actividad'].values # Obtenemos la secuencia de observaciones

    # Mátriz de transición
    # Como valor inicial 1/(numero estados)
    transicion = np.ones((NUMERO_ESTADOS, NUMERO_ESTADOS))
    transicion = transicion / np.sum(transicion, axis=1)

    # Matriz de emisión
    # Generamos valores aleatorios entre 0 y 1, y luego normalizamos para que cada fila sume 1
    emision = np.random.rand(NUMERO_ESTADOS, NUMERO_OBSERVACIONES)
    emision = emision / np.sum(emision, axis=1).reshape((-1, 1))

    # Tras inicializar los parámetros se realiza la llamada al método Baum Welch
    return __baum_welch(secuencia, transicion, emision, INICIAL, n_iter=100)

def aplicar_BaumWelch(dataframe , transicion, emision, n_iter=100):

    secuencia = dataframe['actividad'].values

    return __baum_welch(secuencia, transicion, emision, INICIAL, n_iter)