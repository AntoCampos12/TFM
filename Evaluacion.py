import csv
from datetime import datetime
import numpy as np

## ========================  EVALUACION.PY  =============================== ##
# Este documento contiene las funciones que, recogen los resultados de la evaluación y ofrecen el rendimiento del modelo
# Para ello se clasifica la respuesta del método de Viterbi como atacante según si supera el valor umbral. Tras ello se comprueba si la valoración ha sido correcta o no
# y se almacena en un diccionario por semana.
# Finalmente se realiza una especie de media que evalua el rendimiento obtenido para cada semana

UMBRAL = 45

def getEvaluacionSemanas(usuario, diccionario):
    parse_diccionario = [1 if x > UMBRAL else 0 for x in diccionario]
    insiders = __obtener_insiders() # Se obtienen los atacantes 
    resultados_semana = []
    for i in range(0, len(parse_diccionario)):
        if parse_diccionario[i] == 0:
            if (usuario, (i + 6)%41) in insiders: # Se comprueba si el usuario está en atacantes (Se suma 6 pues las primeras cinco semanas no hay evaluaciones) 
                resultados_semana.append("FN") # Falso negativo, la evaluación da atacante y no era atacante
            else:
                resultados_semana.append("VN") # Verdadero negativo, la evaluación da no atacante y no era atacante
        else:
            if (usuario, (i + 6)%41) in insiders:
                resultados_semana.append("VP") # Verdadero positivo, la evolución da atacante y era atacante
            else:
                resultados_semana.append("FP") # Falso positivo, la evolución da atacante y no era atacante
    return resultados_semana

def actualizarDiccionarioEvaluaciones(evaluacion_semana, diccionario):
    print("TEVAL",len(evaluacion_semana),"TDIC",len(diccionario))
    for i in range(0, len(evaluacion_semana)):
        valores_semana = diccionario[i]
        evaluacion = evaluacion_semana[i]
        if evaluacion == "VP":
            valores_semana["VP"] = valores_semana["VP"] + 1
        elif evaluacion == "VN":
            valores_semana["VN"] = valores_semana["VN"] + 1
        elif evaluacion == "FP":
            valores_semana["FP"] = valores_semana["FP"] + 1
        else:
            valores_semana["FN"] = valores_semana["FN"] + 1
        diccionario[i] = valores_semana
    return diccionario

def __obtener_insiders():
    res = []
    with open('./inputs/insiders.csv', mode="r") as file:
        rows = csv.reader(file)
        next(rows)
        for row in rows:
            semana = datetime.strptime(row[4], '%m/%d/%Y %H:%M:%S')
            clave_semana = semana.isocalendar()[1]
            res.append((row[3], clave_semana))
    return res

def calcular_rendimiento(diccionario_evaluaciones):
    rendimiento_semana = []
    for evaluacion in diccionario_evaluaciones:
        if evaluacion["VP"] + evaluacion["FN"] == 0:
            tasa_VP = 1
        else:
            if evaluacion["VP"] / (evaluacion["VP"] + evaluacion["FN"]) == 0:
                tasa_VP = 1/evaluacion['FN']
            else:
                tasa_VP = evaluacion["VP"] / (evaluacion["VP"] + evaluacion["FN"])
        if evaluacion["VN"] + evaluacion["FP"] == 0:
            tasa_VN = 1
        else:
            tasa_VN = evaluacion["VN"] / (evaluacion["FP"] +  evaluacion["VN"])
        rendimiento_semana.append(np.sqrt(tasa_VP * tasa_VN))
    return rendimiento_semana