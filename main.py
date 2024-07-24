import input
import BaumWelch

CODIGO = 'NLR0174'

def main():
    print("==================== INICIALIZACIÓN DE LOS DATOS ==========================")
    secuencia = input.obtener_secuencia_observaciones(CODIGO)
    #print("\nGENERADA SECUENCIA DE OBSERVACIONES DE {} SEMANAS:\n{}".format(len(secuencia.keys()), secuencia))
    print("==================== OBTENCIÓN DE DATAFRAME PARA APLICACIÓN BAUM WELCH ==========================")
    dataframe_semana1 = input.obtener_semana_usuario(CODIGO,53)
    # print(dataframe_semana1)
    print("==================== OBTENER MATRICES DE EMISIÓN Y TRANSICIÓN ==========================")
    transicion, emision, prob = BaumWelch.iniciar_BaumWelch(dataframe_semana1)
    for i in range(1,5):
        dataframe = input.obtener_semana_usuario(CODIGO, 53-i)
        transicion, emision, prob = BaumWelch.aplicar_BaumWelch(dataframe, transicion, emision, 10)
    #print("TRANSICIÓN:", transicion)
    print("EMISION", emision)
    print("PROBABILIDAD", prob)
    print("=========================== PREDICCIÓN ====================================")
    # prob, ruta = Predict.viterbi(transicion, emision, BaumWelch.NUMERO_ESTADOS, dataframe_semana1['actividad'].values, BaumWelch.INICIAL[0])
    # print("PROBABILIDAD",prob)
    # print("PREDECCIÓN RUTA",ruta)
    # UTILIZAR LAS PRIMERAS CINCO SEMANAS PARA ENTRENAR EL MODELO
    # PROBABILIDAD <- PREDECIR LA SECUENCIA A PARTIR DEL MODELO 

main()