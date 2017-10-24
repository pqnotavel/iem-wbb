#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import cwiid
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk

from matplotlib.figure import Figure
from numpy import arange, pi, random, linspace
import os
import time as ptime
from math import sqrt
import matplotlib.pyplot as plt
import calculos as calc
import conexao as conect
import ManipularArquivo as manArq
from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas
import pylab as py

APs = []
MLs = []
pacient = {}
WBB = {}
dev_names = []
dev_macs = []

global wiimote

class Iem_wbb:
    global pacient

    def on_window1_destroy(self, object, data=None):
        print("Quit with cancel")
        Gtk.main_quit()

    def on_gtk_quit_activate(self, menuitem, data=None):
        print("Quit from menu")
        Gtk.main_quit()

    #Clear all* buffers to create a new consult
    def on_new_activate(self, menuitem, data=None):
        self.name_entry.set_text('')
        self.sex_entry.set_text('')
        self.age_entry.set_text('')
        self.height_entry.set_text('')
        self.name_entry.set_editable(True)
        self.sex_entry.set_editable(True)
        self.age_entry.set_editable(True)
        self.height_entry.set_editable(True)

    #Nothing to do (not implemented yet)
    def on_connect_to_saved_device_activate(self, menuitem, data=None):
        self.saveddeviceswindow1.show()


    def combo_box_in_saved_changed(self, widget):
        global dev_macs

        tree_iter = self.combo_box_in_saved.get_active_iter()
        if(tree_iter != None):
            model = self.combo_box_in_saved.get_model()
            index = model.get_path(tree_iter)[0]
            self.mac_entry_in_saved.set_text(dev_macs[index])
            self.connect_in_saved.set_sensitive(True)
        return True

    #Show newdevicewindow1
    def on_new_device_activate(self, menuitem, data=None):
        print("Adicionando novo dispositivo")
        self.newdevicewindow1.show()

    def on_search_device_activate(self, menuitem, data=None):
        global wiimote
        self.searchdevicewindow1.show()
        self.spinner_in_search.start()

        print("Buscando novo dispositivo")

        wiimote = conect.searchWBB(self)

        self.image_statusbar1.set_from_file("green.png")
        self.label_statusbar1.set_text("Conectado")
        self.spinner_in_search.stop()
        self.save_device_in_search.set_sensitive(True)
        self.device_name_in_search.set_sensitive(True)
        self.capture_button.set_sensitive(True)

    def on_disconnect_activate(self, menuitem, data=None):
        global wiimote
        conect.closeConection(wiimote)
        self.image_statusbar1.set_from_file("red.png")
        self.label_statusbar1.set_text("Não conectado")

    def close_standupwindow1(self, arg1, arg2):
        self.standupwindow1.hide()
        return True

    def close_searchdevicewindow1(self, arg1, arg2):
        self.searchdevicewindow1.hide()
        return True

    def close_newdevicewindow1(self, arg1, arg2):
        self.newdevicewindow1.hide()
        return True

    def close_saveddeviceswindow1(self, arg1, arg2):
        self.saveddeviceswindow1.hide()
        return True

    #Hide newdevicewindow1
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

            self.liststore_devices.clear()
            dev_names, dev_macs = manArq.openWBBs()
            for i in range(len(dev_names)):
                 self.liststore_devices.append([dev_names[i]])

    def on_cancel_in_saved_clicked(self, widget):
        print("Seleção de dispositivo cancelada")
        self.saveddeviceswindow1.hide()

    def on_cancel_button_clicked(self, widget):
        print("Adição de dispositivo cancelada")
        self.newdevicewindow1.hide()

    def on_device_mac_activate(self, widget):
        print("Dispositivo adicionado")
        self.newdevicewindow1.hide()

    def on_scrolledwindow1_button_press_event(self, widget, event):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            self.popoverwindow1.popup()

    def on_savegraph_button_clicked(self, widget):
        self.popoverwindow1.popdown()
        self.fig.canvas.print_png(pacient['Nome'] + '/grafico original')
        print("Gráfico salvo")

    def on_advancedwindow_button_clicked(self, widget):
        self.popoverwindow1.popdown()
        print("Janela Avançada")
        #mng = plt.get_current_fig_manager()
        #mng.resize(*mng.window.maxsize())
        py.show(self.fig.canvas)

    def on_save_device_in_search_clicked(self, widget):
        self.spinner_in_search.stop()
        self.searchdevicewindow1.hide()

    def on_cancel_in_search_clicked(self, widget):
        self.spinner_in_search.stop()
        self.searchdevicewindow1.hide()

    def on_connect_in_saved_clicked(self, widget):
        global wiimote

        MAC = self.mac_entry_in_saved.get_text()
        print (MAC)

        wiimote = conect.connectToWBB(MAC)
        self.image_statusbar1.set_from_file("green.png")
        self.label_statusbar1.set_text("Conectado")
        self.capture_button.set_sensitive(True)
        self.saveddeviceswindow1.hide()
        return

    def on_cancel_in_standup_clicked(self, widget):
        self.standupwindow1.hide()

    def on_messagedialog1_close_clicked(self, widget):
        self.messagedialog1.hide()

    def on_savepacient_button_clicked(self, widget):
        global pacient

        if (self.name_entry.get_text() == ""):
            self.messagedialog1.format_secondary_text("Nome inválido, tente novamente.")
            self.messagedialog1.show()
        elif(self.sex_entry.get_text() == ""):
            self.messagedialog1.format_secondary_text("Sexo inválido, tente novamente.")
            self.messagedialog1.show()
        elif(self.age_entry.get_text() == ""):
            self.messagedialog1.format_secondary_text("Idade inválida, tente novamente.")
            self.messagedialog1.show()
        elif(self.height_entry.get_text() == ""):
            self.messagedialog1.format_secondary_text("Altura inválida, tente novamente.")
            self.messagedialog1.show()
        else:
            name = self.name_entry.get_text()
            sex = self.sex_entry.get_text()
            age = self.age_entry.get_text()
            height = self.height_entry.get_text()
            self.name_entry.set_editable(False)
            self.sex_entry.set_editable(False)
            self.age_entry.set_editable(False)
            self.height_entry.set_editable(False)
            self.name_entry.set_sensitive(False)
            self.sex_entry.set_sensitive(False)
            self.age_entry.set_sensitive(False)
            self.height_entry.set_sensitive(False)

            manArq.makeDir(name)

            print ("Paciente salvo")

            pacient = {'Nome': name, 'Sexo': sex, 'Idade': age, 'Altura': height}
            self.savepacient_button.set_sensitive(False)

    def on_capture_button_clicked(self, widget):
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
        self.axis.plot(MLs, APs,'-',color='r')
        self.canvas.draw()
        #plt.savefig(pacient['Nome'] + '/grafico original.png', dpi=500)
        self.fig.canvas.print_png(pacient['Nome'] + '/grafico original')
        manArq.importXlS(pacient, APs, MLs, pacient['Nome'])
        APs, MLs = calc.geraAP_ML(APs, MLs)

        dis_resultante_total = calc.distanciaResultante(APs, MLs)
        dis_resultante_AP = calc.distanciaResultanteParcial(APs)
        dis_resultante_ML = calc.distanciaResultanteParcial(MLs)

        dis_media = calc.distanciaMedia(dis_resultante_total)

        dis_rms_total = calc.dist_RMS(dis_resultante_total)
        dis_rms_AP = calc.dist_RMS(dis_resultante_AP)
        dis_rms_ML = calc.dist_RMS(dis_resultante_ML)

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

        self.axis2.plot(MLs, APs,'-',color='g')
        self.axis2.set_ylabel('AP')
        self.axis2.set_xlabel('ML')
        self.canvas2.draw()
        self.weight.set_text(str(weight))
        self.weight.set_max_length(6)
        self.imc.set_text(str(imc))
        self.imc.set_max_length(5)
        #plt.savefig(pacient['Nome'] + '/grafico processado.png', dpi=500)
        self.fig2.canvas.print_png(pacient['Nome'] + '/grafico processado')

    def __init__(self):
        global dev_names, dev_macs

        self.gladeFile = "iem-wbb.glade"
        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.gladeFile)

        self.builder.connect_signals(self)

        #Windows
        self.window = self.builder.get_object("window1")
        self.scrolledwindow1 = self.builder.get_object("scrolledwindow1")
        self.scrolledwindow2 = self.builder.get_object("scrolledwindow2")
        self.scrolledwindow3 = self.builder.get_object("scrolledwindow3")
        self.newdevicewindow1 = self.builder.get_object("newdevicewindow1")
        self.popoverwindow1 = self.builder.get_object("popoverwindow1")
        self.messagedialog1 = self.builder.get_object("messagedialog1")
        self.standupwindow1 = self.builder.get_object("standupwindow1")
        self.searchdevicewindow1 = self.builder.get_object("searchdevicewindow1")
        self.saveddeviceswindow1 = self.builder.get_object("saveddeviceswindow1")

        #Delete-events
        self.searchdevicewindow1.connect("delete-event", self.close_searchdevicewindow1)
        self.newdevicewindow1.connect("delete-event", self.close_newdevicewindow1)
        self.standupwindow1.connect("delete-event", self.close_standupwindow1)
        self.saveddeviceswindow1.connect("delete-event", self.close_saveddeviceswindow1)

        #Images
        self.image_statusbar1 = self.builder.get_object("image_statusbar1")

        #Grids
        self.grid_graphs = self.builder.get_object("grid_graphs")

        #Buttons
        self.capture_button = self.builder.get_object("capture_button")
        self.savepacient_button = self.builder.get_object("savepacient_button")
        self.start_capture_button = self.builder.get_object("start_capture_button")
        self.save_device_in_search = self.builder.get_object("save_device_in_search")
        self.connect_in_saved = self.builder.get_object("connect_in_saved")

        #Spinners
        self.spinner_in_search = self.builder.get_object("spinner_in_search")

        #Labels
        self.label_statusbar1 = self.builder.get_object("label_statusbar1")

        #Entrys
        self.name_entry = self.builder.get_object("name_entry")
        self.age_entry = self.builder.get_object("age_entry")
        self.height_entry = self.builder.get_object("height_entry")
        self.sex_entry = self.builder.get_object("sex_entry")
        self.weight = self.builder.get_object("weight")
        self.imc = self.builder.get_object("imc")
        self.device_name_in_search = self.builder.get_object("device_name_in_search")
        self.device_mac_in_search = self.builder.get_object("device_mac_in_search")
        self.device_name_in_new = self.builder.get_object("device_name_in_new")
        self.device_mac_in_new = self.builder.get_object("device_mac_in_new")
        self.mac_entry_in_saved = self.builder.get_object("mac_entry_in_saved")

        self.entry_Mdist = self.builder.get_object("mdist_")
        self.entry_Rdist_AP = self.builder.get_object("rdist_ap")
        self.entry_Rdist_ML = self.builder.get_object("rdist_ml")
        self.entry_Rdist_TOTAL = self.builder.get_object("rdist_t")
        self.entry_TOTEX_AP = self.builder.get_object("totex_ap")
        self.entry_TOTEX_ML = self.builder.get_object("totex_ml")
        self.entry_TOTEX_TOTAL = self.builder.get_object("totex_t")
        self.entry_MVELO_AP = self.builder.get_object("mvelo_ap")
        self.entry_MVELO_ML = self.builder.get_object("mvelo_ml")
        self.entry_MVELO_TOTAL = self.builder.get_object("mvelo_t")
        self.points_entry = self.builder.get_object("points_entry")

        #Combo-boxes
        self.combo_box_in_saved = self.builder.get_object("combo_box_in_saved")

        #Liststores
        self.liststore_devices = self.builder.get_object("liststore_devices")
        self.liststore_devices.clear()
        dev_names, dev_macs = manArq.openWBBs()
        for i in range(len(dev_names)):
             self.liststore_devices.append([dev_names[i]])

        #Change Events
        self.combo_box_in_saved.connect("changed", self.combo_box_in_saved_changed)

        #Plots
        '''Original Graph'''
        self.fig = plt.figure()

        self.axis = self.fig.add_subplot(111)
        self.axis.set_ylabel('AP')
        self.axis.set_xlabel('ML')
        self.canvas = FigureCanvas(self.fig)
        self.scrolledwindow1.add_with_viewport(self.canvas)

        '''Processed Graph'''
        self.fig2 = plt.figure()

        self.axis2 = self.fig2.add_subplot(111)
        self.axis2.set_ylabel('AP')
        self.axis2.set_xlabel('ML')
        self.canvas2 = FigureCanvas(self.fig2)
        self.scrolledwindow2.add_with_viewport(self.canvas2)

        '''Frequency Graph'''
        self.fig3 = plt.figure()

        self.axis3 = self.fig3.add_subplot(111)
        self.axis3.set_ylabel('AP')
        self.axis3.set_xlabel('ML')
        self.canvas3 = FigureCanvas(self.fig3)
        self.scrolledwindow3.add_with_viewport(self.canvas3)

        self.window.show_all()
        self.grid_graphs.set_sensitive(True)

if __name__ == "__main__":
    main = Iem_wbb()
    Gtk.main()
