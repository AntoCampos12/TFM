import Predict
import input
import BaumWelch
import matplotlib.pyplot as plt
import numpy as np

CODIGO = 'MCF0600'

def main():
    #input.actualizar_archivo_local(secuencia, CODIGO)
    print("==================== INICIALIZACIÓN DE LOS DATOS ==========================")
    secuencia = input.get_secuencia_local(CODIGO)
    print("\nGENERADA SECUENCIA DE OBSERVACIONES DE {} SEMANAS:\n{}".format(len(secuencia.keys()), secuencia))
    print("==================== OBTENCIÓN DE DATAFRAME PARA APLICACIÓN BAUM WELCH ==========================")
    secuencia_semana = input.obtener_semana_usuario(secuencia,53)
    print(secuencia_semana)
    print("==================== OBTENER MATRICES DE EMISIÓN Y TRANSICIÓN ==========================")
    
    dataframe, transicion, emision = BaumWelch.iniciar_BaumWelch(secuencia_semana)
    plot_x = range(6, len(secuencia.keys()))
    plot_y = []

    for i in range(1,6):
        transicion, emision = BaumWelch.aplicar_entrenamiento(secuencia_semana, 100, 0.01, 0.1, 5, 0.5, transicion, emision)
        secuencia_semana = input.obtener_semana_usuario(secuencia, i)

    for i in range(6, len(secuencia.keys())):
        prob = Predict.viterbi(transicion, emision, BaumWelch.NUMERO_ESTADOS, secuencia[i])
        plot_y.append(prob[0])
        transicion, emision = BaumWelch.aplicar_entrenamiento(secuencia_semana, 100, 0.01, 0.1, 5, 0.5, transicion, emision)
        secuencia_semana = input.obtener_semana_usuario(secuencia, i)

    
    plt.plot(plot_x, plot_y)
    plt.show()
    #print("TRANSICIÓN:", transicion)
    #print("EMISION", emision)
    #print("=========================== PREDICCIÓN ====================================")
    # prob, ruta = Predict.viterbi(transicion, emision, BaumWelch.NUMERO_ESTADOS, dataframe_semana1['actividad'].values, BaumWelch.INICIAL[0])
    # print("PROBABILIDAD",prob)
    # print("PREDECCIÓN RUTA",ruta)
    # UTILIZAR LAS PRIMERAS CINCO SEMANAS PARA ENTRENAR EL MODELO
    # PROBABILIDAD <- PREDECIR LA SECUENCIA A PARTIR DEL MODELO 

main()