import numpy as np

# VITERBI: Algoritmo que halla la secuencia más probable de estados ocultos
# que produce una secuencia observada de sucesos

def viterbi(transmision, emision, nestados, obs, distribucion_inicial, epsilon = 0.0001):
    # Se inicializan las matrices que contendrán:
    vit = [{}] # Las probabilidades dependiendo del instante 't' y el estado 'i'
    path = {} # Las distintas rutas dependiendo del estado escogido

    # Se calcula una lista a partir del número de estados
    estados = range(0, nestados)

    transmision = np.log(np.clip(transmision, epsilon, 1))
    emision = np.log(np.clip(emision, epsilon, 1))

    # Se inicializan las primeras probabilidades a partir de la distribución inicial
    for i in estados:
        # Para ello el valor de la matriz de viterbi en el instante 0 vendrá dado por la multiplicación de la 
        # probabilidad de estar en un estado 'i' y la probabilidad de emitir la primera observación de la secuencia estando en dicho estado
        vit[0][i] = distribucion_inicial[i] + emision[i][obs[0]]

        # Se añade cada estado como primer paso de cada ruta
        path[i] = [i]
    
    # Para cada instante
    for t in range(1, len(obs)):
        vit.append({})
        newpath = {}
        # Se actualiza la ruta para cada estado.
        for j in estados:
            # Para ello se calcula la probabilidad de estar en el estado 'j' dependiendo de cada uno de los estados 'i', que viene dado por la probabilidad del estado 'i' en la matriz de viterbi anterior,
            # la probabilidad de pasar de 'i' a 'j' y la probabilidad de haber emitido la observación de la secuencia durante el proceso. Tras calcular todo el proceso nos quedamos con aquel de mayor probabilidad
            (prob, state) = max((vit[t-1][i] + transmision[i][j] + emision[j][obs[t]], i) for i in estados)
            # Tras quedarnos con el estado de mayor probabilidad actualizamos las rutas.
            vit[t][j] = prob
            newpath[j] = path[state] + [j]     
        # Y tras pasar por todos los estados actualizamos el valor de path
        path = newpath
    # Finalmente nos quedamos con la ruta de mayor probabilidad en el último instante.
    (prob, state) = max((vit[t][i], i) for i in estados)
    return (prob, path[state])