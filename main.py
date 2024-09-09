from functools import reduce
from outputs import EVAL_MODELOA as archivo_evaluaciones
from outputs import EVAL_MODELOS as archivo_evaluaciones2
import input
import BaumWelch
import Evaluacion
import matplotlib.pyplot as plt
import numpy as np
import time

## ========================  MAIN.PY  =============================== ##
# Función principal, realiza el proceso completo de la aplicación.

# Esta lista contiene todos los códigos almacenados en los archivos locales, es decir, los usuarios utilizados para evaluar el rendimiento de la aplicación
CODIGOS = ['MCF0600', 'MAS0025', 'NAH0503', 'LBC0356', 'SSH0799', 'LJT0817', 'MYD0978', 'RAB0589', 'AJR0932', 'BDV0168', 
           'BIH0745', 'BLS0678', 'BTL0226', 'CAH0936', 'DCH0843', 'EHB0824', 'EHD0584', 'FMG0527', 'FTM0406', 'SLT0907',
           'GHL0460', 'HJB0742', 'JMB0308', 'JRG0207', 'KPC0073', 'LJR0523', 'LQC0479', 'PPF0435', 'RGG0064', 'RKD0604', 
           'TAP0551', 'WDD0366', 'AAF0535', 'ABC0174', 'AKR0057', 'CCL0068', 'CQW0652', 'DIB0285', 'DRR0162', 'EDB0714', 
           'EGD0132', 'FSC0601', 'HBO0413', 'HXL0968', 'IJM0776', 'IKR0401', 'IUB0565', 'JJM0203', 'KRL0501', 'LCC0819', 
           'MDH0580', 'MOS0047', 'NWT0098', 'PNL0301', 'PSF0133', 'RAR0725', 'RHL0992', 'RMW0542', 'TNM0961', 'VSS0154', 
           'XHW0498', 'BSS0369', 'CCA0046', 'CSC0217', 'GTD0219', 'JGT0221', 'JLM0364', 'JTM0223', 'MPM0220', 'MSO0222', 
           'SKG0759', 'AAM0658', 'MAR0955', 'KLH0596', 'LPH0572', 'EDA0684', 'CYA0506', 'OLB0749',
           'CRD0624', 'LDD0560', 'EAH0466', 'JRH0455', 'BQS0525', 'CAC0889', 'CFW0264', 'AAS0442', 'LHB0606', 'HMM0108']
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
    print("==================== INICIALIZACIÓN DE LOS DATOS ==========================")
    secuencia = input.get_secuencia_local(codigo) # Del archivo local se obtiene el diccionario de observaciones del usuario 
    print("\nGENERADA SECUENCIA DE OBSERVACIONES DE {}:\n{}".format(codigo, secuencia))
    print("==================== OBTENCIÓN DE DATAFRAME PARA APLICACIÓN BAUM WELCH ==========================")
    secuencia_semana = input.obtener_semana_usuario(secuencia,1) # Se transforma la semana de actividades en un dataFrame de panda
    print("ACTIVIDADES POR SEMANA {}\n".format(__get_numero_actividades(secuencia)))
    print("==================== OBTENER MATRICES DE EMISIÓN Y TRANSICIÓN ==========================")
    dataframe, transicion, emision = BaumWelch.iniciar_BaumWelch(secuencia_semana) # Se inicializa las matrices de transicion, emision y valores iniciales del HMM
    plot_x = range(6, len(secuencia.keys())) # Se inicializan también las variables que luego permitirán mostrar en una gráfica los valores obtenidos
    plot_y = []

    # Durante las primeras cinco semanas solo se entrena el modelo
    for i in range(1,6):
        secuencia_semana = input.obtener_semana_usuario(secuencia, i)
        transicion, emision, puntuacion = BaumWelch.aplicar_entrenamiento(secuencia_semana, 20, 0.01, 0.1, 5, 0.5, transicion, emision)

    # A partir de la semana cinco, se evalúa la secuencia obtenida y se entrena el módelo con la mejor secuencia estimada
    for i in range(6, len(secuencia.keys())):
        secuencia_semana = input.parse_to_dataframe(secuencia[i])
        transicion, emision, puntuacion = BaumWelch.aplicar_entrenamiento(secuencia_semana, 20, 0.01, 0.1, 5, 0.5, transicion, emision)
        plot_y.append(puntuacion)

    # Se evalúan los resultados obtenidos y se muestra en una gráfica las probabilidades recogidas en cada semana
    resultados_semana = Evaluacion.getEvaluacionSemanas(codigo, plot_y)
    Evaluacion.actualizarDiccionarioEvaluaciones(resultados_semana,diccionario)
    print("============================ EVALUACIÓN COMPLETADA ===========================")
    maximo.append(max(plot_y))
    if(mostrarEvaluacion):
        plt.plot(plot_x, plot_y)
        plt.show()


# Si se quiere ejecutar el algoritmo aquí se presentan dos opciones:
#   • La iteración individual realiza una ejecución completa para un único individuo, muestra las probabilidades del individuo para cada semana
#   • La iteración conjunta realiza la ejecución de todos los códigos que se encuentran en el archivo local, muestra el rendimiento obtenido
def iteracion_individual():
    main('MCF0600', True)

def iteracion_conjunta():
    start = time.time()
    for i in CODIGOS:
        main(i, False)
    end = time.time()

    print("TIEMPO", end - start)
    d = [(i,diccionario[i]) for i in range(0,len(diccionario))]
    print("DICCIONARIO EVALUACIONES", d)
    rendimiento = Evaluacion.calcular_rendimiento(diccionario[:46])
    print("RENDIMIENTO", rendimiento)
    plot_x = range(0, len(rendimiento))
    plt.plot(plot_x, rendimiento)
    plt.show()

    print("MEDIA UMBRAL", sum(maximo)/len(maximo))

iteracion_individual()