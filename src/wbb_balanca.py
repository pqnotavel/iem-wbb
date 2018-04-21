#!/usr/bin/env python3

import sys
import os
import time
import numpy as np

try:
    import cwiid
except:
    print("Desculpe, não consigo importar o cwiid por algum motivo.")
    print("Por favor, verifique se ele e suas ligações python estão instaladas,")
    print("e também o patch da Wii Balance Board.")
    sys.exit(1)

import wbb_calitera as wbb

def main():
    #WBB_ESBEL - calibração padrão
    #calibrations = {'right_top': [2502, 4194, 5896],
    #                'right_bottom': [3242, 4948, 6664],
    #                'left_top': [4288, 5969, 7655],
    #                'left_bottom': [3999, 5772, 7555]}

    #WBB_ESBEL escala_jp
    #calibrations = {'right_top': [2319.0, 4069.126333935299, 5775.0145053375581],
    #                'right_bottom': [3005.0, 4752.6321321028445, 6527.5105130230777],
    #                'left_top': [4161.0, 5903.4542489608284, 7621.8832705473778],
    #                'left_bottom': [4039.0, 5863.4483223686375, 7697.2316566585223]}

    #WBB_ESBEL escala_eu
    #calibrations = {'right_top': [2319.0, 4249.2863977227562, 6123.3200972029945],
    #                'right_bottom': [3005.0, 4932.535439819314, 6894.5571308433591],
    #                'left_top': [4161.0, 6082.8245392950312, 7974.3120731868639],
    #                'left_bottom': [4039.0, 6051.2591790830556, 8075.457648501033]}

    #WBB_DEV - calibração padrão
    calibrations = {'right_top': [5251, 7001, 8764],
                    'right_bottom': [19881, 21714, 23556],
                    'left_top': [2255, 4019, 5795],
                    'left_bottom': [17203, 18889, 20582]}

    #WBB_DEV
    #calibrations = {'right_top': [5129.0, 7000.2527202635247, 8673.753146324183],
    #                'right_bottom': [19824.0, 21776.951434339429, 23546.832586428671],
    #                'left_top': [2371.0, 4268.7978532247189, 5983.5125723310794],
    #                'left_bottom': [17340.0, 19136.878015404596, 20761.645463499703]}

    #mac = "00:26:59:DD:0A:6F"  #WBB_ESBEL
    mac = "00:22:4C:56:D3:F4"   #WBB_DEV
    #mac = "00:27:09:AC:29:22"   #WBB_MARCILIO

    wiimote, bateria = wbb.conecta(mac)

    escala = wbb.escala_eu
    '''rep = 0
                while(rep < 5):
                    print(rep, " - Pronto para aferir o peso!")
                    time.sleep(10)
                    sinal = wbb.captura(wiimote, False, 10)
                    print("Sinal = ", sinal)
                    j = 0
                    readings = {'right_top': 0, 'right_bottom': 0, 'left_top': 0, 'left_bottom': 0}
                    for sensor in ('right_top', 'right_bottom', 'left_top', 'left_bottom'):
                        readings[sensor] = sinal[j]
                        j += 1
            
                    peso = wbb.calcWeight(readings, calibrations, escala)
                    print("right_top : ",readings['right_top'])
                    print("right_bottom : ",readings['right_bottom'])
                    print("left_top : ",readings['left_top'])
                    print("right_bottom : ",readings['right_bottom'])
                    print("Peso = ", peso)
            
                    x,y = wbb.calPos(readings, calibrations, escala)
                    print("X = ", x*(433/2))
                    print("Y = ", y*(238/2))
            
                    CoP_x, CoP_y =  wbb.calCoP(readings, calibrations, escala)
                    print("CoP_x = ", CoP_x)
                    print("CoP_y = ", CoP_y)
                    rep += 1'''

    return


if __name__ == "__main__":
    main()
