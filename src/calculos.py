    # -*- coding: utf-8 -*-

def distanciaMedia (lista_valores):
    return sum(list(lista_valores)) / len(lista_valores)

def distanciaResultante(AP, ML):
    distancia_result = []

    for i in range(len(AP)):
        DR = sqrt((AP[i]**2)+(ML[i]**2))
        distancia_result.append(DR)

    return distancia_result

def distanciaResultanteParcial(APouML):
    distancia_resultparcial = []

    for i in range(len(APouML)):
        DR = sqrt(APouML[i]**2)
        distancia_resultparcial.append(DR)

    return distancia_resultparcial

def distRMS (dist_resultante):
    d_R_quadrada =[]

    for _ in range(len(dist_resultante)):
        dist_result_quadrada = (dist_resultante[_]**2)
        d_R_quadrada.append(dist_result_quadrada)

    soma = sum(list(d_R_quadrada))
    disRMS =sqrt(soma/len(dist_resultante))

    return disRMS

def geraAP_ML(valx, valy):
    #soma_AP0 = soma_ML0 = 0.0   #variáveis referentes ao somatorio
    valores_AP = []             #lista que receberá os valores de AP
    valores_ML = []             #Lista que receberá os valores de ML

    #for ele in range(len(valy)):
    #    soma_AP0 = soma_AP0 + valx[ele]
    #    soma_ML0 = soma_ML0 + valy[ele]

    #AP_barra = soma_AP0 / len(valx)
    #ML_barra = soma_ML0 / len(valy
    AP_barra = sum(valx) / len(valx)
    ML_barra = sum(valy) / len(valy)

    for i in range(len(valy)):
        ap = valx[i] - AP_barra
        ml = valy[i] - ML_barra
        valores_AP.append(ap)
        valores_ML.append(ml)
    return valores_AP, valores_ML

from random import*

def mVelo(totex, tempo):
    velocidademedia = totex/tempo
    return velocidademedia

from math import sqrt

def totex(AP, ML):
    dist = []
    for i in range(len(AP)-1):
        distancia = sqrt((AP[i+1] - AP[i])**2 + (ML[i+1] - ML[i])**2)
        dist.append(distancia)
    Totex = sum(list(dist))
    return Totex

def totexParcial(APouML):
    dist = []
    for i in range(len(APouML)-1):
        distancia = sqrt((APouML[i+1] - APouML[i])**2)
        dist.append(distancia)
    Totexparcial = sum(list(dist))
    return Totexparcial

#retorna o maior valor absoluto de dois elementos
def valorAbsoluto(minimo, maximo):
    if abs(minimo) > abs(maximo):
        return abs(minimo)
    else:
        return abs(maximo)