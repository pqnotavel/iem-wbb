#!/usr/bin/python3

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

    #Show status
    def on_statusbar1_text_pushed(self, menuitem, data=None):
        self.statusbar.push(self.context_id, "Não conectado")

    #Nothing to do (not implemented yet)
    def on_search_device_activate(self, menuitem, data=None):
        print

    def on_connect_to_saved_device_activate(self, menuitem, data=None):
        print

    #Show new_device_window
    def on_new_device_activate(self, menuitem, data=None):
        print("Adicionando novo dispositivo")
        self.new_device_window.show()

    #Hide new_device_window
    def on_add_button_clicked(self, menuitem, data=None):
        print("Dispositivo adicionado")
        self.new_device_window.hide()

    def on_cancel_button_clicked(self, menuitem, data=None):
        print("Adição de dispositivo cancelada")
        self.new_device_window.hide()

    def on_device_mac_activate(self, menuitem, data=None):
        print("Dispositivo adicionado")
        self.new_device_window.hide()

    def on_scrolledwindow1_button_press_event(self, widget, event):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            self.popoverwindow1.popup()

    def on_savegraph_button_clicked(self, widget):
        self.popoverwindow1.popdown()
        print("Gráfico salvo")
        plt.savefig('grafico original.png', dpi=500)

    def on_advancedwindow_button_clicked(self, widget):
        self.popoverwindow1.popdown()
        print("Janela Avançada")
        mng = plt.get_current_fig_manager()
        mng.resize(*mng.window.maxsize())
        py.show(self.canvas)

    def on_savepacient_button_clicked(self, widget):
        name = self.name_entry.get_text()
        sex = self.sex_entry.get_text()
        age = self.age_entry.get_text()
        height = self.height_entry.get_text()
        self.name_entry.set_editable(False)
        self.sex_entry.set_editable(False)
        self.age_entry.set_editable(False)
        self.height_entry.set_editable(False)
        manArq.makeDir(name)
        print ("Paciente salvo")
        pacient = {'Nome': name, 'Sexo': sex, 'Idade': age, 'Altura': height}

    def on_button1_clicked(self, widget):
        global APs, MLs

        balance = conect.readWBB()

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

    #def on_button2_clicked(self, widget):
        #global APs, MLs
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

    def __init__(self):
        self.gladeFile = "iem-wbb2.glade"
        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.gladeFile)

        self.builder.connect_signals(self)

        self.window = self.builder.get_object("window1")
        self.scrolledwindow1 = self.builder.get_object("scrolledwindow1")
        self.scrolledwindow2 = self.builder.get_object("scrolledwindow2")
        self.scrolledwindow3 = self.builder.get_object("scrolledwindow3")
        self.statusbar = self.builder.get_object("statusbar1")
        self.context_id = self.statusbar.get_context_id("status")
        self.new_device_window = self.builder.get_object("new_device_window")
        self.popoverwindow1 = self.builder.get_object("popoverwindow1")

        self.name_entry = self.builder.get_object("name_entry")
        self.age_entry = self.builder.get_object("age_entry")
        self.height_entry = self.builder.get_object("height_entry")
        self.sex_entry = self.builder.get_object("sex_entry")

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

if __name__ == "__main__":
    main = Iem_wbb()
    Gtk.main()
