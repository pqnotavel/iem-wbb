import csv
import os
import xlrd
import xlwt

#cria diretorio, com o nome dos pacientes, onde será guardados seus respectivos arquivos
def makeDir(path):
   os.mkdir('./'+path)

def importarXls(dict_paciente, APs, MLs, path):

    lin, col= (0,0)
    workbook = xlwt.Workbook()
    worksheet = workbook.add_sheet(u'Dados do Paciente')
    worksheetnew = workbook.add_sheet(u'Resultado')

    #salvando a primeira tabela do excel
    for x in dict_paciente:
        worksheet.write(lin, col,u''+str(x))
        worksheet.write(lin, col +1, dict_paciente[x])
        lin+=1


    #salvando os resultados de ap e ml
    worksheetnew.write(0, 0, u'APs')
    worksheetnew.write(0, 1, u'Mls')

    #salvando os valores de APs
    for linha, valor in enumerate(APs):
        worksheetnew.write(linha +1, 0, valor)

    #salvando os valores de MLs
    for linha, valor in enumerate(MLs):
        worksheetnew.write(linha +1, 1, valor)



    workbook.save(path+'/teste.xls')

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