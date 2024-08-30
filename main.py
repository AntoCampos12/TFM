from functools import reduce
import Predict
import input
import BaumWelch
import Evaluacion
import matplotlib.pyplot as plt
import numpy as np
import time

## ========================  MAIN.PY  =============================== ##
# Función principal, realiza el proceso completo de la aplicación.

# Esta lista contiene todos los códigos almacenados en los archivos locales, es decir, los usuarios utilizados para evaluar el rendimiento de la aplicación
CODIGOS = ['MCF0600', 'MAS0025', 'NAH0503', 'LBC0356', 'SSH0799', 'LJT0817', 'ANM0123', 'MYD0978', 'RAB0589', 'AJR0932', 
           'BDV0168', 'BIH0745', 'BLS0678', 'BTL0226', 'CAH0936', 'DCH0843', 'EHB0824', 'EHD0584', 'FMG0527', 'FTM0406', 
           'GHL0460', 'HJB0742', 'JMB0308', 'JRG0207', 'KPC0073', 'LJR0523', 'LQC0479', 'PPF0435', 'RGG0064', 'RKD0604', 
           'TAP0551', 'WDD0366', 'AAF0535', 'ABC0174', 'AKR0057', 'CCL0068', 'CQW0652', 'DIB0285', 'DRR0162', 'EDB0714', 
           'EGD0132', 'FSC0601', 'HBO0413', 'HXL0968', 'IJM0776', 'IKR0401', 'IUB0565', 'JJM0203', 'KRL0501', 'LCC0819', 
           'MDH0580', 'MOS0047', 'NWT0098', 'PNL0301', 'PSF0133', 'RAR0725', 'RHL0992', 'RMW0542', 'TNM0961', 'VSS0154', 
           'XHW0498', 'BSS0369', 'CCA0046', 'CSC0217', 'GTD0219', 'JGT0221', 'JLM0364', 'JTM0223', 'MPM0220', 'MSO0222', 
           'SKG0759', 'AAM0658', 'MAR0955', 'KLH0596', 'DGM0754', 'MBW0809', 'HJS0072', 'LPH0572', 'MTT0901', 'EDA0684', 
           'CRD0624', 'LDD0560', 'EAH0466', 'JRH0455', 'BQS0525', 'DAR0885', 'CAC0889', 'CFW0264', 'AAS0442', 'LHB0606', 
           'OLB0749', 'HMM0108', 'CYA0506', 'SLT0907']
PLOT4 = [0.44460591382105025, 0.6370889678382262, 0.9117704213259056, 0.8917290636126908, 0.8903274267533648, 0.8944271909999159, 0.8987170342729172, 0.9268086959962983, 
         0.9058216273156766, 0.9128709291752769, 0.9336995618478525, 0.9318911162960933, 0.9328075204080797, 0.9258200997725514, 0.9459053029269173, 0.9528351047490354, 
         0.9591663046625439, 0.9586025865388216, 0.6765696408155183, 0.6821127309893709, 0.67700320038633, 0.6813851438692469, 0.6083989264712285, 0.6813851438692469, 
         0.6691496051182058, 0.6797949780052895, 0.672021505032247, 0.9503819266229829, 0.947789578306157, 0.6666666666666666, 0.6859943405700354, 0.6715507368448513, 
         0.6633249580710799, 0.7989354619369612, 0.674199862463242, 0.9636241116594315, 0.6698641270570836, 0.9597148699373931, 0.6853444168423419, 0.9710083124552245, 
         0.6839166144230384, 0.7071067811865476, 0.693888666488711, 0.693888666488711, 0.916515138991168, 0.9789450103725609]
PLOT3 = [0.5806972553108731, 0.8043996665398437, 0.8431152788877544, 0.8431152788877544, 0.8410214463203252, 0.8440971508067067, 0.8243101233681287, 0.9198662110077999, 
         0.8397191227596316, 0.8397191227596316, 0.8623164985025763, 0.8735890880367281, 0.8603834844182798, 0.8374357893586238, 0.835085876453812, 0.8735890880367281, 
         0.9521904571390466, 0.86991767240168, 0.6166698388447784, 0.6236095644623235, 0.6123724356957945, 0.6654751256486924, 0.7803558315797974, 0.6267831705280087, 
         0.5086319569803804, 0.6276459144608478, 0.6413192049055175, 0.8890008890013334, 0.873333764609373, 0.6161409170227454, 0.6642111641550714, 0.6262242910851494, 
         0.6164414002968976, 0.7145896010104964, 0.6123724356957945, 0.8864052604279183, 0.6201736729460423, 0.8735890880367281, 0.6396021490668313, 0.8783100656536799, 
         0.6090712125322324, 0.7071067811865476, 0.5773502691896257, 0.90267093384844, 0.848528137423857, 0.9789450103725609]
PLOT2 = [0.8141195843820602, 0.7896387856258745, 0.8140335388727166, 0.8065992869067975, 0.8410214463203252, 0.82915619758885, 0.8473185457363234, 0.869718492622904, 
         0.8320502943378437, 0.8320502943378437, 0.869718492622904, 0.8506963092234007, 0.8603834844182798, 0.8678978933300583, 0.8735890880367281, 0.8735890880367281, 
         0.8944271909999159, 0.86991767240168, 0.6223535519798788, 0.6236095644623235, 0.6346477588219923, 0.6324555320336759, 0.5730254871776856, 0.6324555320336759, 
         0.6464599351554542, 0.6336522323129238, 0.6413192049055175, 0.8890008890013334, 0.9019752336033946, 0.6382847385042254, 0.6492831643058214, 0.8631906158060839, 
         0.8831760866327847, 0.8991721961325718, 0.5075192189225523, 0.8728715609439694, 0.609749843620211, 0.8885233166386386, 0.6276459144608478, 0.9102589898327995, 
         0.5956833971812706, 0.6526300069150406, 0.6085806194501846, 0.90267093384844, 0.938083151964686, 0.9354143466934853]
PLOT =  [0.44786314354815715, 0.6277878997390947, 0.8984591897591402, 0.8917290636126908, 0.8903274267533648, 0.8944271909999159, 0.9058216273156766, 0.9268086959962983, 
         0.9128709291752769, 0.9198662110077999, 0.9198662110077999, 0.9318911162960933, 0.9397429877987296, 0.9258200997725514, 0.9389243565742775, 0.9528351047490354, 
         0.9660917830792959, 0.9515279320153484, 0.6817541583256872, 0.67700320038633, 0.6718548123582124, 0.6761234037828132, 0.6083989264712285, 0.6813851438692469, 
         0.6691496051182058, 0.674199862463242, 0.6659942845826639, 0.9503819266229829, 0.947789578306157, 0.6666666666666666, 0.6859943405700354, 0.6715507368448513, 
         0.6633249580710799, 0.7989354619369612, 0.6657190234489458, 0.9636241116594315, 0.6698641270570836, 0.9733285267845752, 0.6963106238227914, 0.9710083124552245, 
         0.672021505032247, 0.7071067811865476, 0.693888666488711, 0.6804138174397717, 0.938083151964686, 0.9789450103725609]

diccionario = []
for i in range(0, 53):
    diccionario.append({"VP": 0, "VN": 0, "FP": 0, "FN": 0})

def __calcular_rendimiento(diccionario_evaluaciones):
    rendimiento_semana = []
    for evaluacion in diccionario_evaluaciones:
        if evaluacion["VP"] + evaluacion["FN"] == 0:
            tasa_VP = 1
        else:
            if evaluacion["VP"] / (evaluacion["VP"] + evaluacion["FN"]) == 0:
                tasa_VP = 0.5
            else:
                tasa_VP = evaluacion["VP"] / (evaluacion["VP"] + evaluacion["FN"])
        if evaluacion["VN"] + evaluacion["FP"] == 0:
            tasa_VN = 1
        else:
            tasa_VN = evaluacion["VN"] / (evaluacion["FP"] +  evaluacion["VN"])
        rendimiento_semana.append(np.sqrt(tasa_VP * tasa_VN))
    return rendimiento_semana

def get_numero_actividades(secuencia):
    flat_map = lambda f, xs: reduce(lambda a, b: a + b, map(f, xs))
    actividades_usuario = flat_map(lambda x: x, secuencia.values())
    return len(actividades_usuario)

def main(codigo):
    print("==================== INICIALIZACIÓN DE LOS DATOS ==========================")
    secuencia = input.get_secuencia_local(codigo)
    print("\nGENERADA SECUENCIA DE OBSERVACIONES DE {}:\n{}".format(codigo, secuencia))
    print("==================== OBTENCIÓN DE DATAFRAME PARA APLICACIÓN BAUM WELCH ==========================")
    secuencia_semana = input.obtener_semana_usuario(secuencia,1)
    print("ACTIVIDADES POR SEMANA {}\n".format(get_numero_actividades(secuencia)))
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
        secuencia_semana = input.parse_to_dataframe(prob[1])
        transicion, emision = BaumWelch.aplicar_entrenamiento(secuencia_semana, 100, 0.01, 0.1, 5, 0.5, transicion, emision)
        #secuencia_semana = input.obtener_semana_usuario(secuencia, i)

    resultados_semana = Evaluacion.getEvaluacionSemanas(codigo, plot_y)
    Evaluacion.actualizarDiccionarioEvaluaciones(resultados_semana,diccionario)
    print("============================ EVALUACIÓN COMPLETADA ===========================")
    #plt.plot(plot_x, plot_y)
    #plt.show()
    
    # print("TRANSICIÓN:", transicion)
    # print("EMISION", emision)
    # print("=========================== PREDICCIÓN ====================================")
    # prob, ruta = Predict.viterbi(transicion, emision, BaumWelch.NUMERO_ESTADOS, dataframe_semana1['actividad'].values, BaumWelch.INICIAL[0])
    # print("PROBABILIDAD",prob)
    # print("PREDECCIÓN RUTA",ruta)
    # UTILIZAR LAS PRIMERAS CINCO SEMANAS PARA ENTRENAR EL MODELO
    # PROBABILIDAD <- PREDECIR LA SECUENCIA A PARTIR DEL MODELO

start = time.time()
for i in CODIGOS:
    secuencia = input.get_secuencia_local(i)
    tam = get_numero_actividades(secuencia)
    main(i)
end = time.time()

print("TIEMPO", end - start)
d = [(i,diccionario[i]) for i in range(0,len(diccionario))]
print("DICCIONARIO EVALUACIONES", d)
rendimiento = __calcular_rendimiento(diccionario[:46])
print("RENDIMIENTO", rendimiento)
plot_x = range(0, len(rendimiento))
plt.plot(plot_x, rendimiento)
plt.show()