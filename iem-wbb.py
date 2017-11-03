#!/usr/bin/python3
# -*- coding: utf-8 -*-

#import sys
#import cwiid
#from numpy import arange, pi, random, linspace
#import os
#import time as ptime
#from math import sqrt
#import matplotlib.pyplot as plt
#import pylab as py
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject

import calculos as calc
import conexao as conect
import ManipularArquivo as manArq

from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas
from matplotlib.backends.backend_gtk3 import NavigationToolbar2GTK3 as NavigationToolbar

APs = []
MLs = []
pacient = {}
WBB = {}
dev_names = []
dev_macs = []

global wiimote, battery, child, relative, nt, plotTitle

class Iem_wbb:

    def on_window1_destroy(self, object, data=None):
        print("Quit with cancel")
        Gtk.main_quit()

    def on_gtk_quit_activate(self, menuitem, data=None):
        print("Quit from menu")
        Gtk.main_quit()

    #Destroy and rebuild all
    def on_new_activate(self, menuitem, data=None):
        #self.name_entry.set_text('')
        #self.sex_entry.set_text('')
        #self.age_entry.set_text('')
        #self.height_entry.set_text('')
        #self.name_entry.set_editable(True)
        #self.sex_entry.set_editable(True)
        #self.age_entry.set_editable(True)
        #self.height_entry.set_editable(True)
        self.window.hide()
        self.__init__()

    #Show saved devices window
    def on_connect_to_saved_device_activate(self, menuitem, data=None):
        self.saveddeviceswindow1.show()

    #Saved devices selection
    def combo_box_in_saved_changed(self, widget):
        global dev_macs

        tree_iter = self.combo_box_in_saved.get_active_iter()
        if(tree_iter != None):
            model = self.combo_box_in_saved.get_model()
            index = model.get_path(tree_iter)[0]
            self.mac_entry_in_saved.set_text(dev_macs[index])
            self.connect_in_saved.set_sensitive(True)
            self.instructionslabel_in_saved.set_sensitive(True)
            self.instructionslabel_in_saved.set_visible(True)
            self.image_in_saved.set_sensitive(True)
            self.image_in_saved.set_visible(True)
        return True

    #Show newdevicewindow1
    def on_new_device_activate(self, menuitem, data=None):
        print("Adicionando novo dispositivo")
        self.newdevicewindow1.show()

    #Show searchdevicewindow1
    def on_search_device_activate(self, menuitem, data=None):
        self.searchdevicewindow1.show()
        self.spinner_in_search.start()

    #Disconnet wiimote
    def on_disconnect_activate(self, menuitem, data=None):
        global wiimote
        conect.closeConection(wiimote)
        self.image_statusbar1.set_from_file("red.png")
        self.label_statusbar1.set_text("Não conectado")

    def close_standupwindow1(self, arg1, arg2):
        self.standupwindow1.hide()
        self.window.get_focus()
        return True

    def close_searchdevicewindow1(self, arg1, arg2):
        self.searchdevicewindow1.hide()
        self.window.get_focus()
        return True

    def close_newdevicewindow1(self, arg1, arg2):
        self.newdevicewindow1.hide()
        return True

    def close_saveddeviceswindow1(self, arg1, arg2):
        self.saveddeviceswindow1.hide()
        return True

    def close_advancedgraphswindow(self, arg1, arg2):
        global child, relative, nt
        self.boxAdvanced.remove(child)
        self.boxAdvanced.remove(nt)
        relative.pack_start(child, expand=True, fill=True, padding=0)
        self.advancedgraphswindow.hide()
        return True

    #Adding new device
    def on_add_button_clicked(self, widget):
        global dev_macs, dev_names

        name = self.device_name_in_new.get_text()
        mac = self.device_mac_in_new.get_text()
        if (name == ""):
            self.messagedialog1.format_secondary_text("Nome inválido, tente novamente.")
            self.messagedialog1.show()
        elif((mac == "") or (len(mac)!=17)):
            self.messagedialog1.format_secondary_text("MAC inválido, tente novamente.")
            self.messagedialog1.show()
        else:
            WBB = {'Nome':name, 'MAC':mac}
            manArq.saveWBB(WBB)

            print("Dispositivo adicionado")

            self.device_name_in_new.set_text("")
            self.device_mac_in_new.set_text("")
            self.newdevicewindow1.hide()
            self.window.get_focus()
            self.liststore_devices.clear()
            dev_names, dev_macs = manArq.openWBBs()
            for i in range(len(dev_names)):
                 self.liststore_devices.append([dev_names[i]])

    def on_cancel_in_saved_clicked(self, widget):
        print("Seleção de dispositivo cancelada")
        self.saveddeviceswindow1.hide()

    def on_start_search_button_clicked(self, widget):
        global wiimote, battery

        self.image_statusbar1.set_from_file("red.png")
        self.label_statusbar1.set_text("Não conectado")

        print("Buscando novo dispositivo")

        wiimote, battery = conect.searchWBB()

        self.batterylabel.set_text("Bateria: " + str(int(100*battery))+"%")
        self.batterylabel.set_visible(True)
        
        self.image_statusbar1.set_from_file("green.png")
        self.label_statusbar1.set_text("Conectado")
        self.spinner_in_search.stop()
        self.save_device_in_search.set_sensitive(True)
        self.device_name_in_search.set_sensitive(True)
        self.capture_button.set_sensitive(True)

    def on_connect_in_saved_clicked(self, widget):
        global wiimote, battery

        self.image_statusbar1.set_from_file("red.png")
        self.label_statusbar1.set_text("Não conectado")

        MAC = self.mac_entry_in_saved.get_text()
        print (MAC)

        wiimote, battery = conect.connectToWBB(MAC)

        self.batterylabel.set_text("Bateria: " + str(int(100*battery))+"%")
        self.batterylabel.set_visible(True)

        self.image_statusbar1.set_from_file("green.png")
        self.label_statusbar1.set_text("Conectado")
        self.capture_button.set_sensitive(True)
        self.saveddeviceswindow1.hide()
        self.window.get_focus()

    def on_cancel_button_clicked(self, widget):
        print("Adição de dispositivo cancelada")
        self.newdevicewindow1.hide()

    def on_device_mac_activate(self, widget):
        print("Dispositivo adicionado")
        self.newdevicewindow1.hide()

    def on_boxOriginal_button_press_event(self, widget, event):
        global plotTitle, child, relative, nt
        if event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS and event.button == 1:
            print("Janela Avançada")

            plotTitle = 'Original'

            self.boxOriginal.set_focus_child(self.canvas)
            relative = self.boxOriginal
            child = relative.get_focus_child()
            relative.remove(child)
            self.boxAdvanced.pack_start(child, expand=True, fill=True, padding=0)
            nt = NavigationToolbar(child, self.advancedgraphswindow)
            self.boxAdvanced.pack_start(nt, expand=False, fill=True, padding=0)
            self.advancedgraphswindow.show()

    def on_boxProcessado_button_press_event(self, widget, event):
        global plotTitle, child, relative, nt
        if event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS and event.button == 1:
            print("Janela Avançada")

            plotTitle = 'Processado'

            self.boxProcessado.set_focus_child(self.canvas2)
            relative = self.boxProcessado
            child = relative.get_focus_child()
            relative.remove(child)
            self.boxAdvanced.pack_start(child, expand=True, fill=True, padding=0)
            nt = NavigationToolbar(child, self.advancedgraphswindow)
            self.boxAdvanced.pack_start(nt, expand=False, fill=True, padding=0)
            self.advancedgraphswindow.show()

    def on_boxFourier_button_press_event(self, widget, event):
        global plotTitle, child, relative, nt
        if event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS and event.button == 1:
            print("Janela Avançada")

            plotTitle = 'Fourier'

            self.boxFourier.set_focus_child(self.canvas3)
            relative = self.boxFourier
            child = relative.get_focus_child()
            relative.remove(child)
            self.boxAdvanced.pack_start(child, expand=True, fill=True, padding=0)
            nt = NavigationToolbar(child, self.advancedgraphswindow)
            self.boxAdvanced.pack_start(nt, expand=False, fill=True, padding=0)
            self.advancedgraphswindow.show()

    def on_save_device_in_search_clicked(self, widget):
        self.spinner_in_search.stop()
        self.searchdevicewindow1.hide()
        self.window.get_focus()

    def on_cancel_in_search_clicked(self, widget):
        self.spinner_in_search.stop()
        self.searchdevicewindow1.hide()
        self.window.get_focus()

    def on_cancel_in_standup_clicked(self, widget):
        self.standupwindow1.hide()

    def on_messagedialog1_close_clicked(self, widget):
        self.messagedialog1.hide()

    def on_savepacient_button_clicked(self, widget):
        global pacient

        name = self.name_entry.get_text()
        sex = self.sex_combobox.get_active_text()
        age = self.age_entry.get_text()
        height = self.height_entry.get_text()

        if (name == ""):
            self.messagedialog1.format_secondary_text("Nome inválido, tente novamente.")
            self.messagedialog1.show()
            self.name_entry.grab_focus()
        elif(sex == ""):
            self.messagedialog1.format_secondary_text("Sexo inválido, tente novamente.")
            self.messagedialog1.show()
            self.sex_entry.grab_focus()
        elif(age == ""):
            self.messagedialog1.format_secondary_text("Idade inválida, tente novamente.")
            self.messagedialog1.show()
            self.age_entry.grab_focus()
        elif(height == ""):
            self.messagedialog1.format_secondary_text("Altura inválida, tente novamente.")
            self.messagedialog1.show()
            self.height_entry.grab_focus()
        else:
            ID = manArq.getID()
            self.ID_entry.set_text(ID)
            manArq.makeDir(ID + ' - ' + name)
            height = height.replace(',', '.', 1)
            print("Paciente salvo")
            pacient = {'Nome': name, 'ID': ID, 'Sexo': sex, 'Idade': age, 'Altura': height}
            self.savepacient_button.set_sensitive(False)
            self.name_entry.set_editable(False)
            #self.sex_entry.set_editable(False)
            self.age_entry.set_editable(False)
            self.height_entry.set_editable(False)
            self.height_entry.set_text(height)
            self.ID_entry.set_editable(False)
            self.name_entry.set_sensitive(False)
            self.sex_combobox.set_sensitive(False)
            #self.sex_entry.set_sensitive(False)
            self.age_entry.set_sensitive(False)
            self.height_entry.set_sensitive(False)
            self.ID_entry.set_sensitive(False)

    def on_capture_button_clicked(self, widget):
        self.progressbar1.set_fraction(0)
        self.standupwindow1.show()

    def on_start_capture_button_clicked(self, widget):
        self.standupwindow1.hide()

        global APs, MLs, pacient, wiimote, dev_macs, dev_names

        balance, weights, pontos = calc.calcPontos(self, wiimote)
        midWeight = calc.calcPesoMedio(weights)
        imc = calc.calcIMC(midWeight, float(pacient['Altura']))

        self.points_entry.set_text(str(pontos))

        pacient['Peso'] = midWeight
        pacient['IMC'] = imc

        for (x,y) in balance:
            APs.append(x)
            MLs.append(y)

        max_absoluto_AP = calc.valorAbsoluto(min(APs), max(APs))
        max_absoluto_ML = calc.valorAbsoluto(min(MLs), max(MLs))

        max_absoluto_AP *= 1.25
        max_absoluto_ML *= 1.25

        print('max_absoluto_AP:',max_absoluto_AP,'max_absoluto_ML:',max_absoluto_ML)

        self.axis.clear()
        self.axis.set_ylabel('AP')
        self.axis.set_xlabel('MP')

        self.axis.set_xlim(-max_absoluto_ML, max_absoluto_ML)
        self.axis.set_ylim(-max_absoluto_AP, max_absoluto_AP)
        self.axis.plot(MLs, APs,'-.',color='r')
        self.canvas.draw()

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

        max_absoluto_AP *=1.25
        max_absoluto_ML *=1.25

        print('max_absoluto_AP:', max_absoluto_AP, 'max_absoluto_ML:', max_absoluto_ML)
        self.axis2.clear()

        self.axis2.set_xlim(-max_absoluto_ML, max_absoluto_ML)
        self.axis2.set_ylim(-max_absoluto_AP, max_absoluto_AP)

        self.axis2.plot(MLs, APs,'-.',color='g')
        self.axis2.set_ylabel('AP')
        self.axis2.set_xlabel('ML')
        self.canvas2.draw()
        self.weight.set_text(str(midWeight))
        self.weight.set_max_length(6)
        self.imc.set_text(str(imc))
        self.imc.set_max_length(5)
        self.save_exam_button.set_sensitive(True)

    def on_save_exam_button_clicked(self, widget):
        global pacient
        path = 'Pacients/' + pacient['ID']+ ' - ' + pacient['Nome']
        self.fig.canvas.print_png(str(path + '/grafico original'))
        self.fig2.canvas.print_png(str(path + '/grafico processado'))
        manArq.importXlS(pacient, APs, MLs, path)
        print("Exame Salvo")

    def __init__(self):
        global dev_names, dev_macs

        self.gladeFile = "iem-wbb.glade"
        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.gladeFile)
        go = self.builder.get_object
        self.builder.connect_signals(self)

        #Boxes
        self.vbox1 = go("vbox1")
        self.boxOriginal = go("boxOriginal")
        self.boxProcessado = go("boxProcessado")
        self.boxFourier = go("boxFourier")
        self.boxAdvanced = go("boxAdvanced")

        #Windows
        self.window = go("window1")
        self.newdevicewindow1 = go("newdevicewindow1")
        self.messagedialog1 = go("messagedialog1")
        self.standupwindow1 = go("standupwindow1")
        self.searchdevicewindow1 = go("searchdevicewindow1")
        self.saveddeviceswindow1 = go("saveddeviceswindow1")
        self.advancedgraphswindow = go("advancedgraphswindow")

        #Delete-events
        self.searchdevicewindow1.connect("delete-event", self.close_searchdevicewindow1)
        self.newdevicewindow1.connect("delete-event", self.close_newdevicewindow1)
        self.standupwindow1.connect("delete-event", self.close_standupwindow1)
        self.saveddeviceswindow1.connect("delete-event", self.close_saveddeviceswindow1)
        self.advancedgraphswindow.connect("delete-event", self.close_advancedgraphswindow)

        #Images
        self.image_statusbar1 = go("image_statusbar1")
        self.image_in_saved = go("image_in_saved")

        #Grids
        self.grid_graphs = go("grid_graphs")

        #Buttons
        self.capture_button = go("capture_button")
        self.savepacient_button = go("savepacient_button")
        self.start_capture_button = go("start_capture_button")
        self.save_device_in_search = go("save_device_in_search")
        self.connect_in_saved = go("connect_in_saved")
        self.save_exam_button = go("save_exam_button")

        #Spinners
        self.spinner_in_search = go("spinner_in_search")

        #Labels
        self.label_statusbar1 = go("label_statusbar1")
        self.batterylabel = go("batterylabel")
        self.instructionslabel_in_saved = go("instructionslabel_in_saved")

        #Entrys
        self.name_entry = go("name_entry")
        self.age_entry = go("age_entry")
        self.height_entry = go("height_entry")
        self.ID_entry = go("ID_entry")
        #self.sex_entry = go("sex_entry")
        self.weight = go("weight")
        self.imc = go("imc")
        self.device_name_in_search = go("device_name_in_search")
        self.device_mac_in_search = go("device_mac_in_search")
        self.device_name_in_new = go("device_name_in_new")
        self.device_mac_in_new = go("device_mac_in_new")
        self.mac_entry_in_saved = go("mac_entry_in_saved")

        self.entry_Mdist = go("mdist_")
        self.entry_Rdist_AP = go("rdist_ap")
        self.entry_Rdist_ML = go("rdist_ml")
        self.entry_Rdist_TOTAL = go("rdist_t")
        self.entry_TOTEX_AP = go("totex_ap")
        self.entry_TOTEX_ML = go("totex_ml")
        self.entry_TOTEX_TOTAL = go("totex_t")
        self.entry_MVELO_AP = go("mvelo_ap")
        self.entry_MVELO_ML = go("mvelo_ml")
        self.entry_MVELO_TOTAL = go("mvelo_t")
        self.points_entry = go("points_entry")

        #Combo-boxes
        self.combo_box_in_saved = go("combo_box_in_saved")
        self.sex_combobox = go("sex_combobox")

        #Liststores
        self.liststore_devices = go("liststore_devices")
        self.liststore_devices.clear()
        dev_names, dev_macs = manArq.openWBBs()
        for i in range(len(dev_names)):
             self.liststore_devices.append([dev_names[i]])

        #Change Events
        self.combo_box_in_saved.connect("changed", self.combo_box_in_saved_changed)

        #Bars
        self.progressbar1 = go("progressbar1")

        #Plots
        '''Original Graph'''
        self.fig = Figure(dpi=50)
        self.fig.suptitle('Original', fontsize=20)

        self.axis = self.fig.add_subplot(111)
        self.axis.set_ylabel('AP', fontsize = 16)
        self.axis.set_xlabel('ML', fontsize = 16)
        self.canvas = FigureCanvas(self.fig)
        self.boxOriginal.pack_start(self.canvas, expand=True, fill=True, padding=0)

        '''Processed Graph'''
        self.fig2 = Figure(dpi=50)
        self.fig2.suptitle('Processado', fontsize=20)

        self.axis2 = self.fig2.add_subplot(111)
        self.axis2.set_ylabel('AP', fontsize = 16)
        self.axis2.set_xlabel('ML', fontsize = 16)
        self.canvas2 = FigureCanvas(self.fig2)
        self.boxProcessado.pack_start(self.canvas2, expand=True, fill=True, padding=0)

        '''Frequency Graph'''
        self.fig3 = Figure(dpi=50)
        self.fig3.suptitle('Transformada de Fourier', fontsize=20)
        self.axis3 = self.fig3.add_subplot(111)
        self.axis3.set_ylabel('AP', fontsize = 16)
        self.axis3.set_xlabel('ML', fontsize = 16)
        self.canvas3 = FigureCanvas(self.fig3)
        self.boxFourier.pack_start(self.canvas3, expand=True, fill=True, padding=0)

        self.window.show_all()

if __name__ == "__main__":
    main = Iem_wbb()
    Gtk.main()
