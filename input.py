import csv
import pandas as pd
from itertools import islice
from datetime import datetime


diccionario_actividades = {}
EMAIL_USUARIO = "Maxwell.Clark.Faulkner@dtaa.com"
CODIGO = 'MCF0600'

def __actualizar_diccionario(row, actividad):
    valor = {}
    valor['activity'] = actividad
    valor['date'] = row[1]
    
    clave_usuario = row[2]

    semana = datetime.strptime(row[1], '%m/%d/%Y %H:%M:%S')
    clave_semana = semana.isocalendar()[1]

    if clave_usuario not in diccionario_actividades:
        diccionario_actividades[clave_usuario] = {}
    
    if clave_semana not in diccionario_actividades[clave_usuario]:
        diccionario_actividades[clave_usuario][clave_semana] = []
    
    diccionario_actividades[clave_usuario][clave_semana].append(valor)

def __obtener_diccionario_logon():
    res = []
    with open('./inputs/r4.2/logon.csv', mode="r") as file:
        rows = csv.reader(file)
        next(rows)
        for row in rows:
            __actualizar_diccionario(row, row[4])
    return res

def __obtener_diccionario_http():
    res = []
    with open('./inputs/r4.2/http.csv', mode="r") as file:
        rows = csv.reader(file)
        next(rows)
        for row in islice(rows,100000):
            __actualizar_diccionario(row, 'HTTP')
    return res

def __obtener_diccionario_email():
    ## POR REALIZAR, ES NECESARIO PARSEAR LOS NOMBRE DE USUARIO
    res = []
    with open('./inputs/r4.2/email.csv', mode="r") as file:
        rows = csv.reader(file)
        next(rows)
        for row in rows:
            __actualizar_diccionario(row, "EMAIL")
    return res

def __obtener_diccionario_file():
    res = []
    with open('./inputs/r4.2/file.csv', mode="r") as file:
        rows = csv.reader(file)
        next(rows)
        for row in rows:
           __actualizar_diccionario(row, 'USB')
    return res

def __obtener_diccionario_device():
    res = []
    with open('./inputs/r4.2/device.csv', mode="r") as file:
        rows = csv.reader(file)
        next(rows)
        for row in rows:
           __actualizar_diccionario(row, row[4])
    return res

def __parse_valores(actividades):
    VALORES = {'Logon': 0, 'Logoff': 1, 'HTTP': 2, 'USB': 3, 'Connect': 4, 'Disconnect': 5, 'EMAIL': 6}
    res = []
    for actividad in actividades:
        res.append(VALORES.get(actividad['activity']))
    return res

def __get_acciones(user):
    acciones_user = diccionario_actividades.get(user)
    for clave,semana in acciones_user.items():
        semana = sorted(semana,key=lambda x: x['date'])
        semana = __parse_valores(semana)
        acciones_user[clave] = semana
    diccionario_actividades[user] = acciones_user
    return diccionario_actividades.get(user)

def __obtener_diccionario():
    __obtener_diccionario_logon()
    __obtener_diccionario_http()
    __obtener_diccionario_email()
    __obtener_diccionario_file()
    __obtener_diccionario_device()
    return diccionario_actividades

def obtener_secuencia_observaciones(usuario):
    __obtener_diccionario()
    res = __get_acciones(usuario)
    return res

def obtener_semana_usuario(secuencia, semana):
    actividades_semana = secuencia.get(semana)

    lista_pd =[]
    for actividad in actividades_semana:
        lista_pd.append({'actividad':actividad})
    df = pd.DataFrame(lista_pd)
    return df

def actualizar_archivo_local(secuencia, usuario):
    f = open("inputs/local.txt", "w")
    f.write("{};{}".format(usuario, secuencia))
    f.close()

def get_secuencia_local(usuario):
    f = open("inputs/local.txt", "r")
    res = {}
    for line in f.readlines():
        lineas = line.split(';')
        if(lineas[0] == usuario):
            res = eval(lineas[1])
            res = dict(res)
            return res
    return res