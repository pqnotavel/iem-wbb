# -*- coding: utf-8 -*-


#import csv
import os
import xlrd
import xlwt
from xlutils.copy import copy
from datetime import datetime

#cria diretorio, com o nome dos pacientes, onde será guardados seus respectivos arquivos
def makeDir(path):
    if os.path.isdir('./pacients/'+path):
        return False
    os.mkdir('./pacients/'+path)
    return True

def renameDir(pathOld, pathNew):
    #if not os.path.isdir('.pacients/'+pathOld):
    #    return False
    os.rename('./pacients/'+pathOld, './pacients/'+pathNew)

def saveWBB(dict_WBB):
    #Lendo arquivo
    workbook_read = xlrd.open_workbook('Devices.xls', formatting_info = True)
    worksheet_read = workbook_read.sheet_by_index(0)
    lin = worksheet_read.nrows

    #Copiando arquivo
    workbook_write = copy(workbook_read)
    worksheet_write = workbook_write.get_sheet(0)

    #Escrevendo dados no arquivo
    worksheet_write.write(lin, 0, dict_WBB['Nome'])
    worksheet_write.write(lin, 1, dict_WBB['MAC'])
    worksheet_write.write(lin, 2, dict_WBB['Padrao'])

    #Salvando Arquivo editado
    workbook_write.save('Devices.xls')

def openWBBs():
    names = []
    macs = []
    workbook = xlrd.open_workbook('Devices.xls')
    worksheet = workbook.sheet_by_index(0)

    for row in range(1, worksheet.nrows):
        names.append(str(worksheet.cell(row,0).value))
        macs.append(str(worksheet.cell(row,1).value))

    return names, macs

def loadPacient(self, dict_paciente, path):
    lin, col = (0 ,0)
    workbook = xlrd.open_workbook(path)
    worksheet = workbook.sheet_by_index(1)
    workbook.save(path+'/'+dict_paciente['Nome']+'.xls')
    return

def savePacient(dict_paciente, path):
    workbook = xlwt.Workbook()
    worksheet = workbook.add_sheet(u'Dados do Paciente')

    worksheet.write(0, 0,u'Nome')
    worksheet.write(0, 1, dict_paciente['Nome'])
    worksheet.write(1, 0,u'Sexo')
    worksheet.write(1, 1, dict_paciente['Sexo'])
    worksheet.write(2, 0,u'Idade')
    worksheet.write(2, 1, dict_paciente['Idade'])
    worksheet.write(3, 0,u'Altura')
    worksheet.write(3, 1, dict_paciente['Altura'])

    workbook.save('pacients/'+path+'/'+dict_paciente['Nome']+'.xls')

def saveExam(dict_paciente, APs, MLs, path):
    #Lendo arquivo
    workbook_read = xlrd.open_workbook(path+'/'+dict_paciente['Nome']+'.xls', formatting_info = True)

    #Copiando arquivo
    workbook_write = copy(workbook_read)
    worksheet_write = workbook_write.get_sheet(0)

    worksheet_write.write(4, 0,u'Peso')
    worksheet_write.write(4, 1, dict_paciente['Peso'])
    worksheet_write.write(5, 0,u'IMC')
    worksheet_write.write(5, 1, dict_paciente['IMC'])

    #Extraindo Data e Hora
    td = datetime.now()
    td = str(td)
    td = td.replace(':', 'h', 1)
    td = td.replace(':', 'm', 1)
    td = td+'s'

    #Criando nova planilha
    worksheetnew = workbook_write.add_sheet(u''+str(td))

    #salvando os resultados de ap e ml
    worksheetnew.write(0, 0, u'APs')
    worksheetnew.write(0, 1, u'MLs')

    #salvando os valores de APs
    for linha, valor in enumerate(APs):
        worksheetnew.write(linha +1, 0, valor)

    #salvando os valores de MLs
    for linha, valor in enumerate(MLs):
        worksheetnew.write(linha +1, 1, valor)

    #Salvando Arquivo editado
    workbook_write.save(path+'/'+dict_paciente['Nome']+'.xls')

def importXlS(dict_paciente, APs, MLs, data, path):

    #lin, col= (0,0)
    workbook = xlwt.Workbook()
    worksheet = workbook.add_sheet(u'Dados do Paciente')
    #salvando a primeira tabela do excel
    #for x in dict_paciente:
    #    worksheet.write(lin, col,u''+str(x))
    #    worksheet.write(lin, col +1, dict_paciente[x])
    #    lin+=1
    worksheet.write(0, 0,u'Nome')
    worksheet.write(0, 1, dict_paciente['Nome'])
    worksheet.write(1, 0,u'Sexo')
    worksheet.write(1, 1, dict_paciente['Sexo'])
    worksheet.write(2, 0,u'Idade')
    worksheet.write(2, 1, dict_paciente['Idade'])
    worksheet.write(3, 0,u'Altura')
    worksheet.write(3, 1, dict_paciente['Altura'])
    worksheet.write(4, 0,u'Peso')
    worksheet.write(4, 1, dict_paciente['Peso'])
    worksheet.write(5, 0,u'IMC')
    worksheet.write(5, 1, dict_paciente['IMC'])

    #Extraindo Data e Hora
    td = data
    td = str(td)
    l = len(td) - 6
    td = td[0:l]
    td = td.replace(':', 'h', 1)
    td = td.replace(':', 'm', 1)
    td = td+'s'

    #Criando nova planilha
    worksheetnew = workbook.add_sheet(u''+str(td))

    #salvando os resultados de ap e ml
    worksheetnew.write(0, 0, u'APs')
    worksheetnew.write(0, 1, u'MLs')

    #salvando os valores de APs
    for linha, valor in enumerate(APs):
        worksheetnew.write(linha +1, 0, valor)

    #salvando os valores de MLs
    for linha, valor in enumerate(MLs):
        worksheetnew.write(linha +1, 1, valor)

    #-------salvar a data------
    workbook.save(path)
    #workbook.save(path)

def getID():
    IDpaciente = open('ID.txt', mode='r+')
    number = int(IDpaciente.read())
    number += 1
    IDpaciente.seek(0)
    IDpaciente.write(str(number))
    IDpaciente.close()

    return str(number)

# openXLS(path):
#    workbook = xlrd.open_workbook(path)
#    worksheet = workbook.sheet_by_index(1)
#
#    for row_num in range(worksheet.nrows):
#        if row_num == 0:
#            continue
#        row = worksheet.row_values(row_num)


#if __name__ =="__main__":
#    print(getID())
