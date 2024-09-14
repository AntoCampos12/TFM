import copy
from functools import reduce
import json
from outputs import EVAL_MODELOA as archivo_evaluaciones
from outputs import EVAL_MODELOS as archivo_evaluaciones2
import input
from const import ENTRADA, INSIDERS_T1, INSIDERS_T2, INSIDERS_T3
import BaumWelch
import Evaluacion
import matplotlib.pyplot as plt
import numpy as np
import time
import tqdm

ahora = int(time.time())

## ========================  MAIN.PY  =============================== ##
# Función principal, realiza el proceso completo de la aplicación.

maximo = []
# Se inicializa el diccionario que se rellenara con los resultados de cada una de las evaluaciones
diccionario = []
for i in range(0, 53):
    diccionario.append({"VP": 0, "VN": 0, "FP": 0, "FN": 0})

# En ocasiones para las pruebas se filtraron las observaciones por su número de actividades
def __get_numero_actividades(secuencia):
    flat_map = lambda f, xs: reduce(lambda a, b: a + b, map(f, xs))
    actividades_usuario = flat_map(lambda x: x, secuencia.values())
    return len(actividades_usuario)

# La función principal, realiza los siguientes pasos:
def main(codigo, mostrarEvaluacion):
    # print("==================== INICIALIZACIÓN DE LOS DATOS ==========================")
    secuencia = input.get_secuencia_local(codigo) # Del archivo local se obtiene el diccionario de observaciones del usuario 
    # # print("\nGENERADA SECUENCIA DE OBSERVACIONES DE {}:\n{}".format(codigo, secuencia))
    # print("==================== OBTENCIÓN DE DATAFRAME PARA APLICACIÓN BAUM WELCH ==========================")
    secuencia_semana = input.obtener_semana_usuario(secuencia,1) # Se transforma la semana de actividades en un dataFrame de panda
    # # print("ACTIVIDADES POR SEMANA {}\n".format(__get_numero_actividades(secuencia)))
    # print("==================== OBTENER MATRICES DE EMISIÓN Y TRANSICIÓN ==========================")
    dataframe, transicion, emision = BaumWelch.iniciar_BaumWelch(secuencia_semana) # Se inicializa las matrices de transicion, emision y valores iniciales del HMM
    plot_x = range(6, len(secuencia.keys()) + 1) # Se inicializan también las variables que luego permitirán mostrar en una gráfica los valores obtenidos
    plot_y = []
    
    # Durante las primeras cinco semanas solo se entrena el modelo
    for i in range(1,6):
        secuencia_semana = input.parse_to_dataframe(secuencia[i]) # input.obtener_semana_usuario(secuencia, i)
        transicion, emision, puntuacion, primera_puntuacion = BaumWelch.aplicar_entrenamiento(secuencia_semana, 20, 0.01, 0.1, 20, 0.5, transicion, emision)

    # A partir de la semana cinco, se evalúa la secuencia obtenida y se entrena el módelo con la mejor secuencia estimada
    for i in tqdm.tqdm(range(6, len(secuencia.keys())+1), desc=codigo, leave=False):
        secuencia_semana = input.parse_to_dataframe(secuencia[i])
        transicion, emision, puntuacion, primera_puntuacion = BaumWelch.aplicar_entrenamiento(secuencia_semana, 20, 0.01, 0.1, 20, 0.5, transicion, emision)
        # VMAYOR: CORREGIDO, HAY QUE PUNTUAR ANTES DE ENTRENAR (CON EL MODELO PREVIO)
        # print("-LogP is ", primera_puntuacion)
        plot_y.append(primera_puntuacion)

    # Se evalúan los resultados obtenidos y se muestra en una gráfica las probabilidades recogidas en cada semana
    resultados_semana = Evaluacion.getEvaluacionSemanas(codigo, plot_y)
    # print(resultados_semana)
    # print(resultados_semana)
    with open(f"run_{ahora}_eval.csv", "a") as dst:
        dst.write(codigo + "," + ",".join(resultados_semana) + "\n")

    with open(f"run_{ahora}_score.csv", "a") as dst:
        dst.write(codigo + "," + ",".join([(str(x)) for x in plot_y]) + "\n")
        
    Evaluacion.actualizarDiccionarioEvaluaciones(resultados_semana,diccionario)
    # print("============================ EVALUACIÓN COMPLETADA ===========================")
    maximo.append(max(plot_y))
    if(mostrarEvaluacion):
        plt.plot(plot_x, plot_y)
        plt.show()


# Si se quiere ejecutar el algoritmo aquí se presentan dos opciones:
#   • La iteración individual realiza una ejecución completa para un único individuo, muestra las probabilidades del individuo para cada semana
#   • La iteración conjunta realiza la ejecución de todos los códigos que se encuentran en el archivo local, muestra el rendimiento obtenido
def iteracion_individual_T1():
    main('MCF0600', True)

def iteracion_individual_T2():
    main('DRR0162', True)

def iteracion_individual_T3():
    main('JGT0221', True)

def iteracion_seleccion():
    start = time.time()
    cod = []
    with open (ENTRADA, "r") as f:
        lines = f.readlines()
        for line in lines:
            cod.append(line[:7])

    for val in INSIDERS_T1:
        cod.remove(val)

    for val in INSIDERS_T2:
        cod.remove(val)

    for val in INSIDERS_T3:
        cod.remove(val)

    cod = cod[0:100]
    cod.extend(INSIDERS_T1)
    #cod.extend(INSIDERS_T2)
    cod.extend(INSIDERS_T3)

    print("Se van a evaluar", len(cod), "usuarios")
    for i in tqdm.tqdm(cod):
        main(i, False)
    end = time.time()

    # print("TIEMPO", end - start)
    d = [(i,diccionario[i]) for i in range(0,len(diccionario))]
    # print("DICCIONARIO EVALUACIONES", d)
    rendimiento = Evaluacion.calcular_rendimiento(diccionario[:46])
    # print("RENDIMIENTO", rendimiento)
    plot_x = range(0, len(rendimiento))
    plt.plot(plot_x, rendimiento)
    plt.show()
#iteracion_individual_T1()

iteracion_seleccion()
