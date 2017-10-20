import csv
import os
import xlrd
import xlwt
from datetime import datetime

#cria diretorio, com o nome dos pacientes, onde será guardados seus respectivos arquivos
def makeDir(path):
   os.mkdir('./'+path)

def carregaPaciente(name):
    return

def salvaPaciente(dict_paciente, path):
    lin, col = (0, 0)
    workbook = xlwt.Workbook()
    worksheet = workbook.add_sheet(u'Dados do Paciente')

    for x in dict_paciente:
        worksheet.write(lin, col,u''+str(x))
        worksheet.write(lin, col +1, dict_paciente[x])
        lin+=1

    workbook.save(path + '/teste.xls')

def importarXls(dict_paciente, APs, MLs, path):

    lin, col= (0,0)
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
    td = datetime.now()
    td = str(td)
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
    workbook.save(path+'/'+dict_paciente['Nome']+'.xls')

def abrirXLS(path):
    workbook = xlrd.open_workbook(path)
    worksheet = workbook.sheet_by_index(1)

    for row_num in range(worksheet.nrows):
        if row_num == 0:
            continue
        row = worksheet.row_values(row_num)

'''def salvar(dados):
    f = open('dados.txt', 'w')
    for linha in dados:
'''

#if __name__ =="__main__":
 #   importarXls()
