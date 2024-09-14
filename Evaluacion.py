import csv
from datetime import datetime
import numpy as np
from const import UMBRAL

## ========================  EVALUACION.PY  =============================== ##
# Este documento contiene las funciones que, recogen los resultados de la evaluación y ofrecen el rendimiento del modelo
# Para ello se clasifica la respuesta del método de Viterbi como atacante según si supera el valor umbral. Tras ello se comprueba si la valoración ha sido correcta o no
# y se almacena en un diccionario por semana.
# Finalmente se realiza una especie de media que evalua el rendimiento obtenido para cada semana

def compruebaSemana(tupla):
    if tupla in insiders:
        return True
    elif (tupla[0], tupla[1]-1) in insiders:
        return True
    elif (tupla[0], tupla[1]+1) in insiders:
        return True
    return False

def getEvaluacionSemanas(usuario, puntuaciones):
    anomalias = [1 if x > UMBRAL else 0 for x in puntuaciones]
    resultados_semana = []
    # print([x for x in insiders if x[0] == usuario])
    for semana in range(0, len(anomalias)):
        if anomalias[semana] == 0:
            if (usuario, (semana + 6)) in insiders: # Se comprueba si el usuario está en atacantes (Se suma 6 pues las primeras cinco semanas no hay evaluaciones) 
                if resultados_semana[-1] == "VP":
                    # VMAYOR: CAMBIO PARA EVITAR MARCAR COMO FN UN ATAQUE (DE VARIAS SEMANAS) QUE HA SIDO DETECTADO LA SEMANA ANTERIOR
                    resultados_semana.append("VP")
                else:
                    resultados_semana.append("FN") # Falso negativo, la evaluación da atacante y no era atacante
            else:
                resultados_semana.append("VN") # Verdadero negativo, la evaluación da no atacante y no era atacante
        else:
            if (usuario, (semana + 6)) in insiders:
                resultados_semana.append("VP") # Verdadero positivo, la evolución da atacante y era atacante
            elif compruebaSemana((usuario, (semana + 6))):
                # VMAYOR: CAMBIO PARA EVITAR MARCAR COMO FP SI HAY UN ATAQUE EN LA SEMANA ANTERIOR A POSTERIOR
                resultados_semana.append("VP") # Verdadero positivo, la evolución da atacante y era atacante
            else:
                resultados_semana.append("FP") # Falso positivo, la evolución da atacante y no era atacante
    return resultados_semana

def actualizarDiccionarioEvaluaciones(evaluacion_semana, diccionario):
    # print("TEVAL",len(evaluacion_semana),"TDIC",len(diccionario))
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
            if datetime.strptime(row[4], '%m/%d/%Y %H:%M:%S').isocalendar()[0] != 2010:
                continue
            # VMAYOR: CORREGIDO, UN ATAQUE PUEDE DURAR MÁS DE UNA SEMANA
            primera_semana = datetime.strptime(row[4], '%m/%d/%Y %H:%M:%S')
            ultima_semana = datetime.strptime(row[5], '%m/%d/%Y %H:%M:%S')
            for semana in range(primera_semana.isocalendar()[1], ultima_semana.isocalendar()[1]+1):
                res.append((row[3], semana))
    return res

def calcular_rendimiento(diccionario_evaluaciones):
    rendimiento_semana = []
    for evaluacion in diccionario_evaluaciones:
        if evaluacion["VP"] + evaluacion["FN"] == 0:
            tasa_VP = 1
        else:
            tasa_VP = evaluacion["VP"] / (evaluacion["VP"] + evaluacion["FN"])
        if evaluacion["VN"] + evaluacion["FP"] == 0:
            tasa_VN = 1
        else:
            tasa_VN = evaluacion["VN"] / (evaluacion["FP"] +  evaluacion["VN"])
        rendimiento_semana.append(np.sqrt(tasa_VP * tasa_VN))
    return rendimiento_semana

# VMAYOR: CAMBIO, PARA NO LEER EL LISTADO DE INSIDERS EN CADA ITERACIÓN
insiders = __obtener_insiders() # Se obtienen los atacantes 