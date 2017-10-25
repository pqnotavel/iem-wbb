#!/usr/bin/python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from math import sqrt
import matplotlib.pyplot as plt
import calculos as calc
from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas


APs = []
MLs = []


class MyWindow(Gtk.Window):
    def __init__(self):


        #Janela
        Gtk.Window.__init__(self, title="Testando")
        self.set_resizable(False)
        self.set_size_request(600, 600)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.set_border_width(10)

        principal = Gtk.Box(spacing=10)
        principal.set_homogeneous(False)

        vbox_left = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox_left.set_homogeneous(False)
        vbox_right = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox_right.set_homogeneous(False)

            ### Boxes que ficarão dentro da vbox_left ###
        hbox_MDIST = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hbox_MDIST.set_homogeneous(False)
        hbox_labels = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hbox_labels.set_homogeneous(False)
        hbox_RDIST = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hbox_RDIST.set_homogeneous(True)
        hbox_TOTEX = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hbox_TOTEX.set_homogeneous(True)
        hbox_MVELO = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hbox_MVELO.set_homogeneous(True)

        #criando os elementos das boxes Mdist, Labels, Rdist, TOTEX, Mvelo
                ##MDIST##
        label_Mdist = Gtk.Label('MDIST')
        self.entry_Mdist = Gtk.Entry()
        self.entry_Mdist.set_editable(False)
        self.entry_Mdist.set_max_length(max=8)
                ##LABELS##
        label_vazia = Gtk.Label('     ')
        label_AP = Gtk.Label('AP')
        label_ML = Gtk.Label('ML')
        label_TOTAL = Gtk.Label('TOTAL')
                ##RDIST##
        label_Rdist = Gtk.Label('RDIST')
        self.entry_Rdist_AP = Gtk.Entry()
        self.entry_Rdist_AP.set_editable(False)
        self.entry_Rdist_AP.set_max_length(max=8)
        self.entry_Rdist_ML = Gtk.Entry()
        self.entry_Rdist_ML.set_editable(False)
        self.entry_Rdist_ML.set_max_length(max=8)
        self.entry_Rdist_TOTAL = Gtk.Entry()
        self.entry_Rdist_TOTAL.set_editable(False)
        self.entry_Rdist_TOTAL.set_max_length(max=8)
                ##TOTEX##
        label_TOTEX = Gtk.Label('TOTEX')
        self.entry_TOTEX_AP = Gtk.Entry()
        self.entry_TOTEX_AP.set_editable(False)
        self.entry_TOTEX_AP.set_max_length(max=8)
        self.entry_TOTEX_ML = Gtk.Entry()
        self.entry_TOTEX_ML.set_editable(False)
        self.entry_TOTEX_ML.set_max_length(max=8)
        self.entry_TOTEX_TOTAL = Gtk.Entry()
        self.entry_TOTEX_TOTAL.set_editable(False)
        self.entry_TOTEX_TOTAL.set_max_length(max=8)
                ##MVELO##
        label_MVELO = Gtk.Label('MVELO')
        self.entry_MVELO_AP = Gtk.Entry()
        self.entry_MVELO_AP.set_editable(False)
        self.entry_MVELO_AP.set_max_length(max=8)
        self.entry_MVELO_ML = Gtk.Entry()
        self.entry_MVELO_ML.set_editable(False)
        self.entry_MVELO_ML.set_max_length(max=8)
        self.entry_MVELO_TOTAL = Gtk.Entry()
        self.entry_MVELO_TOTAL.set_editable(False)
        self.entry_MVELO_TOTAL.set_max_length(max=8)

        #colocando cada elemento dentro da sua box
        hbox_MDIST.pack_start(label_Mdist,True,True,0)
        hbox_MDIST.pack_start(self.entry_Mdist,True,True,0)

        hbox_labels.pack_start(label_vazia,True,True,0)
        hbox_labels.pack_start(label_AP,True,True,0)
        hbox_labels.pack_start(label_ML,True,True,0)
        hbox_labels.pack_start(label_TOTAL,True,True,0)

        hbox_RDIST.pack_start(label_Rdist,True,True,0)
        hbox_RDIST.pack_start(self.entry_Rdist_AP,True,True,0)
        hbox_RDIST.pack_start(self.entry_Rdist_ML,True,True,0)
        hbox_RDIST.pack_start(self.entry_Rdist_TOTAL,True,True,0)

        hbox_TOTEX.pack_start(label_TOTEX, True, True, 0)
        hbox_TOTEX.pack_start(self.entry_TOTEX_AP, True, True, 0)
        hbox_TOTEX.pack_start(self.entry_TOTEX_ML, True, True, 0)
        hbox_TOTEX.pack_start(self.entry_TOTEX_TOTAL, True, True, 0)

        hbox_MVELO.pack_start(label_MVELO, True, True, 0)
        hbox_MVELO.pack_start(self.entry_MVELO_AP, True, True, 0)
        hbox_MVELO.pack_start(self.entry_MVELO_ML, True, True, 0)
        hbox_MVELO.pack_start(self.entry_MVELO_TOTAL, True, True, 0)

        #colocando as boxes pequenas dentro das box vbox_left
        vbox_left.pack_start(hbox_MDIST, True, True, 0)
        vbox_left.pack_start(hbox_labels, True, True, 0)
        vbox_left.pack_start(hbox_RDIST, True, True, 0)
        vbox_left.pack_start(hbox_TOTEX, True, True, 0)
        vbox_left.pack_start(hbox_MVELO, True, True, 0)

        #elementos da vbox_right)
        #Notebook
        self.notebook = Gtk.Notebook()
        self.fig = plt.figure()


        self.axis = self.fig.add_subplot(111)
        self.axis.set_ylabel('ML')
        self.axis.set_xlabel('AP')
        self.canvas = FigureCanvas(self.fig)
        self.canvas.set_size_request(500, 500)



        self.page1 = Gtk.Box()
        self.page1.set_border_width(10)
        self.page1.add(self.canvas)
        self.notebook.append_page(self.page1, Gtk.Label('Gráfico do CoP'))

        ##aqui fica a segunda janela do notebook
        self.fig2 = plt.figure()
        self.axis2 = self.fig2.add_subplot(111)
        self.axis2.set_ylabel('ML')
        self.axis2.set_xlabel('AP')
        self.canvas2 = FigureCanvas(self.fig2)
        self.canvas2.set_size_request(500, 500)

        self.page2 = Gtk.Box()
        self.page2.set_border_width(10)
        self.page2.add(self.canvas2)
        self.notebook.append_page(self.page2, Gtk.Label('Gráfico na frequência'))

        #criando os botoes
        hbox_botoes = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hbox_botoes.set_homogeneous(True)

        self.button1 = Gtk.Button(label="Capturar")
        self.button1.connect("clicked", self.on_button1_clicked)

        self.button2 = Gtk.Button(label="Processar")
        self.button2.connect("clicked", self.on_button2_clicked)
        #self.set_resizable(True
        #colocando os botoes nas boxes
        hbox_botoes.pack_start(self.button1, True, True,0)
        hbox_botoes.pack_start(self.button2, True, True, 0)

        vbox_right.pack_start(self.notebook, True, True, 0)
        vbox_right.pack_start(hbox_botoes, True, True, 0)
        # colocando as boxes verticais dentro da box principal
        principal.pack_start(vbox_left, True, True, 0)
        principal.pack_start(vbox_right, True, True, 0)

        #Adicionano os elementos na box exterior
        self.add(principal)

    def on_button1_clicked(self, widget):
        global APs, MLs
    
        pos_AP = []
        pos_ML = []
        
        AP_aux = []
        ML_aux = []

        ref_arquivo_x_diferente = open("/home/thales/wiibalance/cwiid/python/xdiferente.txt", "r")
        ref_arquivo_y_diferente = open("/home/thales/wiibalance/cwiid/python/ydiferente.txt", "r")

        for linhax in ref_arquivo_x_diferente:
            AP_aux.append(ref_arquivo_x_diferente.readline(13))

        for linhay in ref_arquivo_y_diferente:
            ML_aux.append(ref_arquivo_y_diferente.readline(13))

        ref_arquivo_x_diferente.close()
        ref_arquivo_y_diferente.close()

        for i in range(len(AP_aux)):
            e = AP_aux[i]

            try:
                APs.append(float(e))
            except:
                #print('posicao de x que nao conseguiu pegar o valor real:', i)
                pos_AP.append(i)
                
        for j in range(len(ML_aux)):
            e = ML_aux[j]

            try:
                MLs.append(float(e))
            except:
                #print('posicao de y que nao conseguiu pegar o valor real:', j)
                pos_ML.append(j)
                
        APs, MLs = calc.geraNumeroAleatorio(-3, 7, -4, 6, 40)

        if calc.diferentes(APs,MLs):
            if len(APs) > len(MLs):
                APs = calc.delEleAP(APs, pos_ML)
            else:
                MLs =calc.delEleML(MLs, pos_AP)

        max_absoluto_AP = calc.valorAbsoluto(min(APs), max(APs))
        max_absoluto_ML = calc.valorAbsoluto(min(MLs), max(MLs))

        print('max_absoluto_AP:',max_absoluto_AP,'max_absoluto_ML:',max_absoluto_ML)

        self.axis.clear()
        self.axis.set_ylabel('ML')
        self.axis.set_xlabel('AP')

        self.axis.set_xlim(-max_absoluto_AP, max_absoluto_AP)
        self.axis.set_ylim(-max_absoluto_ML, max_absoluto_ML)
        self.axis.plot(APs, MLs,'-',color='r')
        self.canvas.draw()


    def on_button2_clicked(self, widget):
        global APs, MLs
        APs, MLs = calc.geraAP_ML(APs, MLs)

        dis_resultante_total = calc.distanciaResultante(APs, MLs)
        dis_resultante_AP = calc.distanciaResultanteParcial(APs)
        dis_resultante_ML = calc.distanciaResultanteParcial(MLs)

        dis_media = calc.distanciaMedia(dis_resultante_total)

        dis_rms_total = calc.distRMS(dis_resultante_total)
        dis_rms_AP = calc.distRMS(dis_resultante_AP)
        dis_rms_ML = calc.distRMS(dis_resultante_ML)

        totex_total = calc.totex(APs, MLs)
        totex_AP = calc.totexParcial(APs)
        totex_ML = calc.totexParcial(MLs)

        mvelo_total = calc.mVelo(totex_total, 20)
        mvelo_AP = calc.mVelo(totex_AP, 20)
        mvelo_ML =  calc.mVelo(totex_ML, 20)

        self.entry_Mdist.set_text(str(dis_media))

        self.entry_Rdist_TOTAL.set_text(str(dis_rms_total))
        self.entry_Rdist_AP.set_text(str(dis_rms_AP))
        self.entry_Rdist_ML.set_text(str(dis_rms_ML))

        self.entry_TOTEX_TOTAL.set_text(str(totex_total))
        self.entry_TOTEX_AP.set_text(str(totex_AP))
        self.entry_TOTEX_ML.set_text(str(totex_ML))

        self.entry_MVELO_TOTAL.set_text(str(mvelo_total))
        self.entry_MVELO_AP.set_text(str(mvelo_AP))
        self.entry_MVELO_ML.set_text(str(mvelo_ML))

        max_absoluto_AP = calc.valorAbsoluto(min(APs), max(APs))
        max_absoluto_ML = calc.valorAbsoluto(min(MLs), max(MLs))

        print('max_absoluto_AP:', max_absoluto_AP, 'max_absoluto_ML:', max_absoluto_ML)
        self.axis.clear()

        self.axis.set_xlim(-max_absoluto_AP, max_absoluto_AP)
        self.axis.set_ylim(-max_absoluto_ML, max_absoluto_ML)

        self.axis.plot(APs, MLs,'.-',color='g')

        self.axis.set_ylabel('ML')
        self.axis.set_xlabel('AP')
        self.canvas.draw()


if __name__ == '__main__':
	win = MyWindow()
	win.connect("delete-event", Gtk.main_quit)
	win.show_all()
	Gtk.main()
	
