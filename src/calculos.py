    # -*- coding: utf-8 -*-

import numpy as np

def distanciaMedia (RD):
    #return sum(list(lista_valores)) / len(lista_valores)
    return RD.mean()

def distanciaMedia_(APouML):
    #return sum(list(lista_valores)) / len(lista_valores)
    return np.absolute(APouML).mean()

def distanciaResultante(AP, ML):
    distancia_result = np.zeros_like(AP)

    #for i in range(len(AP)):
    #    DR = sqrt((AP[i]**2)+(ML[i]**2))
    #    distancia_result.append(DR)

    distancia_result = np.sqrt(AP**2 + ML**2)
    return distancia_result

def distanciaResultanteParcial(APouML):
    distancia_resultparcial = np.zeros_like(APouML)

    #for i in range(len(APouML)):
    #    DR = sqrt(APouML[i]**2)
    #    distancia_resultparcial.append(DR)

    distancia_resultparcial = np.sqrt(APouML**2)
    return distancia_resultparcial

def distRMS (dist_resultante):
    #d_R_quadrada =np.zeros_like(dist_resultante)

    #for _ in range(len(dist_resultante)):
    #    dist_result_quadrada = (dist_resultante[_]**2)
    #    d_R_quadrada.append(dist_result_quadrada)

    #soma = sum(list(d_R_quadrada))
    #disRMS =sqrt(soma/len(dist_resultante))

    RMS = np.sqrt((dist_resultante**2).sum())/dist_resultante.size

    return RMS

def geraAP_ML(valy, valx):
    #soma_AP0 = soma_ML0 = 0.0   #variáveis referentes ao somatorio
    valores_AP = np.zeros_like(valy)    #ndarray que receberá os valores de AP
    valores_ML = np.zeros_like(valx)    #ndarray que receberá os valores de ML

    #for ele in range(len(valy)):
    #    soma_AP0 = soma_AP0 + valx[ele]
    #    soma_ML0 = soma_ML0 + valy[ele]

    #AP_barra = soma_AP0 / len(valx)
    #ML_barra = soma_ML0 / len(valy
    AP_barra = sum(valy) / len(valy)
    ML_barra = sum(valx) / len(valx)

    valores_AP = valy - AP_barra
    valores_ML = valx - ML_barra
    #for i in range(len(valy)):
    #    ap = valx[i] - AP_barra
    #    ml = valy[i] - ML_barra
    #    valores_AP.append(ap)
    #    valores_ML.append(ml)


    return valores_AP, valores_ML, AP_barra, ML_barra

from random import*

def mVelo(totex, tempo):
    velocidademedia = totex/tempo
    return velocidademedia

from math import sqrt

def totex(AP, ML):
    #dist = []
    #for i in range(len(AP)-1):
    #    distancia = sqrt((AP[i+1] - AP[i])**2 + (ML[i+1] - ML[i])**2)
    #    dist.append(distancia)
    #Totex = sum(list(dist))
    Totex_ = np.sqrt(((AP[1:] - AP[:-1])**2) + ((ML[1:] - ML[:-1])**2))
    Totex = Totex_.sum()
    return Totex

def totexParcial(APouML):
    #dist = []
    #for i in range(len(APouML)-1):
    #    distancia = sqrt((APouML[i+1] - APouML[i])**2)
    #    dist.append(distancia)
    #Totexparcial = sum(list(dist))
    Totexparcial = np.absolute(APouML[1:] - APouML[:-1]).sum()
    return Totexparcial

#retorna o maior valor absoluto de dois elementos
def valorAbsoluto(minimo, maximo):
    if abs(minimo) > abs(maximo):
        return abs(minimo)
    else:
        return abs(maximo)
