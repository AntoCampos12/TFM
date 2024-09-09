import csv
import pandas as pd
from datetime import datetime

## ========================  INPUT.PY  =============================== ##
# Aquí se recogen los métodos necesarios para, a partir de los archivos '.csv' de la base de datos de estudio (https://kilthub.cmu.edu/articles/dataset/Insider_Threat_Test_Dataset/12841247)
# generar los dataset que consumirá el algoritmo de HMM. 
# Las actividades se organizarán según cuatro modelos distintos:
# MODELO A: Actividades LOGIN, LOGOUT, CONECTAR USB, MOVER ARCHIVOS A USB, DESCONECTAR USB, EMAIL
# MODELO B: Actividades LOGIN EN HORARIO LABORAL, LOGOUT EN HORARIO LABORAL LOGIN FUERA DEL HORARIO, LOGOUT FUERA DEL HORARIO, 
#                                           CAMBIO DISPOSITIVO EN HORARIO LABORAL Y FUERA DEL HORARIO LABORAL
# MODELO C: MODELO B + EMAIL Y MOVER ARCHIVOS A USB
# MODELO D: MODELO A, PERO SE DIFERENCIA SI EL USUARIO HACE LOGOUT TRAS NINGUNA, UNA O MÁS DE UNA ACCIÓN

diccionario_actividades = {}

# ACTUALIZAR DICCIONARIO
# A partir de una actividad (Usuario, PC, actividad, fecha...) añade una nueva entrada en el diccionario de actividades del usuario.
# La versión 2 del método distingue si la actividad se realiza en el horario laboral o fuera de él

def __actualizar_diccionario(row, actividad):
    valor = {}
    valor['activity'] = actividad
    valor['date'] = row[1]
    valor['pc'] = row[3]
    clave_usuario = row[2]

    semana = datetime.strptime(row[1], '%m/%d/%Y %H:%M:%S')
    clave_semana = semana.isocalendar()[1]

    if clave_usuario not in diccionario_actividades:
        diccionario_actividades[clave_usuario] = {}
    
    if clave_semana not in diccionario_actividades[clave_usuario]:
        diccionario_actividades[clave_usuario][clave_semana] = []
    
    diccionario_actividades[clave_usuario][clave_semana].append(valor)

def __actualizar_diccionario2(row, actividad):
    valor = {}
    valor['activity'] = actividad
    valor['date'] = row[1]
    valor['pc'] = row[3]
    
    clave_usuario = row[2]

    semana = datetime.strptime(row[1], '%m/%d/%Y %H:%M:%S')
    if semana.hour >= 8 and semana.hour <= 17:
        valor['activity'] = actividad + 'I'
    else:
        valor['activity'] = actividad + 'F'

    clave_semana = semana.isocalendar()[1]

    if clave_usuario not in diccionario_actividades:
        diccionario_actividades[clave_usuario] = {}
    
    if clave_semana not in diccionario_actividades[clave_usuario]:
        diccionario_actividades[clave_usuario][clave_semana] = []
    
    diccionario_actividades[clave_usuario][clave_semana].append(valor)

# OBTENER DICCIONARIO
# Accede a cada uno de los archivos '.csv' correspondiente y realiza una llamada a la función actualizar_diccionario
# La versión 'logon2' llama a la versión 2 de actualizar diccionario 

def __obtener_diccionario_logon():
    res = []
    with open('./inputs/r4.2/logon.csv', mode="r") as file:
        rows = csv.reader(file)
        next(rows)
        for row in rows:
            __actualizar_diccionario(row, row[4])
    return res

def __obtener_diccionario_logon2():
    res = []
    with open('./inputs/r4.2/logon.csv', mode="r") as file:
        rows = csv.reader(file)
        next(rows)
        for row in rows:
            __actualizar_diccionario2(row, row[4])
    return res

def __obtener_diccionario_http():
    res = []
    with open('./inputs/r4.2/http.csv', mode="r") as file:
        rows = csv.reader(file)
        next(rows)
        for row in rows:
            __actualizar_diccionario(row, 'HTTP')
    return res

def __obtener_diccionario_email():
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

# OBTENER MODELO
# Llama a los métodos obtener_diccionario... que son necesario según el modelos seleccionado.

def __obtener_diccionario():
    __obtener_diccionario_logon()
    __obtener_diccionario_http()
    __obtener_diccionario_email()
    __obtener_diccionario_file()
    __obtener_diccionario_device()
    return diccionario_actividades

def __obtener_modelo_2():
    # Este modelo consiste en Login/Logout durante y fuera del horario laboral y el estudio del cambio de dispositivo
    __obtener_diccionario_logon2()
    return diccionario_actividades

def __obtener_modelo_3():
    # Este modelo consiste en Login/Logout durante y fuera del horario laboral y el estudio del cambio de dispositivo
    # Además se suma las actividades de correo y mover archivos a USB
    __obtener_diccionario_logon2()
    __obtener_diccionario_email()
    __obtener_diccionario_file()
    return diccionario_actividades

def __obtener_modelo_4():
    __obtener_diccionario_logon()
    __obtener_diccionario_email()
    __obtener_diccionario_file()
    __obtener_diccionario_device()
    return diccionario_actividades

# PARSE VALORES
# Una vez que la variable diccionario_actividades está completamente rellena, se recorre cada una de las semanas del usuario, ordenando las actividades por fecha y hora
# cambiando las actividades por su número asociado y realizando modificaciones auxiliares en caso de ser necesario

def __parse_valores(actividades):
    VALORES = {'Logon': 0, 'Logoff': 1, 'HTTP': 2, 'USB': 3, 'Connect': 4, 'Disconnect': 5, 'EMAIL': 6}
    res = []
    for actividad in actividades:
        res.append(VALORES.get(actividad['activity']))
    return res

def __parse_valores2(actividades):
    VALORES = {'LogonI': 0, 'LogoffI': 1, 'LogonF': 2, 'LogoffF': 3, 'CDI': 4, 'CDF': 5}
    res = []
    sesiones = 0 # Indica si ya hay alguna sesión abierta
    for actividad in actividades:
        if actividad['activity'] == 'LogoffI' or actividad['activity'] == 'LogoffF':
            res.append(VALORES.get(actividad['activity']))
            sesiones = sesiones - 1
        else:
            if sesiones == 0:
                res.append(VALORES.get(actividad['activity']))
                sesiones = 1
            else:
                semana = datetime.strptime(actividad['date'], '%m/%d/%Y %H:%M:%S')
                if semana.hour >= 8 and semana.hour <= 17:
                    res.append(4)
                    sesiones = sesiones + 1
                else:
                    res.append(5)
                    sesiones = sesiones + 1

    return res

def __parse_valores3(actividades):
    VALORES = {'LogonI': 0, 'LogoffI': 1, 'LogonF': 2, 'LogoffF': 3, 'CDI': 4, 'CDF': 5, 'EMAIL': 6, 'USB': 7}
    res = []
    sesiones = 0 # Indica si ya hay alguna sesión abierta
    for actividad in actividades:
        if actividad['activity'] == 'LogoffI' or actividad['activity'] == 'LogoffF' or actividad['activity'] == 'EMAIL' or actividad['activity'] == 'USB':
            res.append(VALORES.get(actividad['activity']))
            sesiones = sesiones - 1
        else:
            if sesiones == 0:
                res.append(VALORES.get(actividad['activity']))
                sesiones = 1
            else:
                semana = datetime.strptime(actividad['date'], '%m/%d/%Y %H:%M:%S')
                if semana.hour >= 8 and semana.hour <= 17:
                    res.append(4)
                    sesiones = sesiones + 1
                else:
                    res.append(5)
                    sesiones = sesiones + 1

    return res

def __parse_valores4(actividades):
    VALORES = {'Logon': 0, 'Logoff': 1, 'HTTP': 2, 'USB': 3, 'Connect': 4, 'Disconnect': 5, 'EMAIL': 6} ## 7 LOGOFF 1 ACTIVIDAD, 8 LOGOFF > 2 ACTIVIDADES   
    actividades_conexion = {}
    res = []
    for actividad in actividades:
        if actividad['activity'] == 'Logoff':
            if actividad['pc'] not in actividades_conexion or actividades_conexion[actividad['pc']] == 0:
                res.append(1)
            elif actividades_conexion[actividad['pc']] == 1:
                res.append(7)
            else:
                res.append(8)
            actividades_conexion[actividad['pc']] = 0
        else:
            if actividad['pc'] not in actividades_conexion or actividad['activity'] == 'Logon':
                actividades_conexion[actividad['pc']] = 0
            else:
                actividades_conexion[actividad['pc']] = actividades_conexion[actividad['pc']] + 1
            res.append(VALORES.get(actividad['activity']))
    return res

# GET ACCIONES
# Método que, a partir del diccionario de actividades, llama a parse_valores para obtener el conjunto de observaciones de un usuario

def __get_acciones(user):
    acciones_user = diccionario_actividades.get(user)
    for clave,semana in acciones_user.items():
        semana = sorted(semana,key=lambda x: x['date'])
        semana = __parse_valores(semana)
        acciones_user[clave] = semana
    diccionario_actividades[user] = acciones_user
    return diccionario_actividades.get(user)

def __get_acciones2(user):
    acciones_user = diccionario_actividades.get(user)
    for clave,semana in acciones_user.items():
        semana = sorted(semana,key=lambda x: x['date'])
        semana = __parse_valores2(semana)
        acciones_user[clave] = semana
    diccionario_actividades[user] = acciones_user
    return diccionario_actividades.get(user)

def __get_acciones3(user):
    acciones_user = diccionario_actividades.get(user)
    for clave,semana in acciones_user.items():
        semana = sorted(semana,key=lambda x: x['date'])
        semana = __parse_valores3(semana)
        acciones_user[clave] = semana
    diccionario_actividades[user] = acciones_user
    return diccionario_actividades.get(user)

def __get_acciones4(user):
    acciones_user = diccionario_actividades.get(user)
    for clave,semana in acciones_user.items():
        semana = sorted(semana,key=lambda x: x['date'])
        semana = __parse_valores4(semana)
        acciones_user[clave] = semana
    diccionario_actividades[user] = acciones_user
    return diccionario_actividades.get(user)

# OBTENER SECUENCIA OBSERVACIONES
# Método que realiza la secuencia completa, genera primero el diccionario de actividades y tras esto llama a get_acciones de un usuario

def obtener_secuencia_observaciones(usuario):
    __obtener_diccionario()
    res = __get_acciones(usuario)
    return res

# Una vez que has conseguido el conjunto de observaciones, el resultado todavía no esta preparado para ser consumido por el HMM. Para ello es necesario transformarlo a un objeto
# dataFrame de panda.

def obtener_semana_usuario(secuencia, semana):
    actividades_semana = secuencia.get(semana)
    return parse_to_dataframe(actividades_semana)

def parse_to_dataframe(actividades_semana):
    lista_pd =[]
    for actividad in actividades_semana:
        lista_pd.append({'actividad':actividad})
    df = pd.DataFrame(lista_pd)
    return df

# Generar el diccionario de actividades requiere de mucho tiempo y realizar esta operación es inviable cada vez que se analiza un sujeto, para ello, existen estos dos métodos
# que almacen los valores en archivos locales

def actualizar_archivo_local(secuencia, usuario):
    f = open("inputs/local(MODELOD).txt", "a")
    f.write("{};{}\n".format(usuario, secuencia))
    f.close()

def get_secuencia_local(usuario):
    f = open("inputs/local(MODELOD).txt", "r")
    res = {}
    for line in f.readlines():
        lineas = line.split(';')
        if(lineas[0] == usuario):
            res = eval(lineas[1])
            res = dict(res)
            return res
    return res
