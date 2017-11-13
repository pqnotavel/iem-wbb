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
#from gi.repository import GObject

import calculos as calc
import conexao as conect
import ManipularArquivo as manArq

from matplotlib.figure import Figure
from matplotlib import pyplot as plt
from matplotlib import cm
from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas
from matplotlib.backends.backend_gtk3 import NavigationToolbar2GTK3 as NavigationToolbar

import psycopg2

from bluetooth.btcommon import is_valid_address as iva

APs = []
MLs = []
pacient = {}
WBB = {}

global devices, wiimote, battery, child, relative, nt, conn, cur, modifying, is_connected, is_pacient, user_ID

class Iem_wbb:

    def on_cancel_button_in_login_clicked(self, widget):
        print("Quit in login with cancel_button")
        cur.close()
        conn.close()
        Gtk.main_quit()

    def on_login_window_destroy(self, object, data=None):
        print("Quit in login from menu")
        cur.close()
        conn.close()
        Gtk.main_quit()

    def on_login_button_clicked(self, widget):
        global cur, user_ID

        self.messagedialog1.set_transient_for(self.login_window)
        username = self.username_entry_in_login.get_text()
        password = self.password_entry_in_login.get_text()

        cur.execute("SELECT username FROM users;")
        rows = cur.fetchall()
        user_exists = False
        i = 0
        while (not (user_exists)) and (i<len(rows)):
            if(rows[i][0] == username):
                user_exists = True
            i+=1

        cur.execute("SELECT crypt(%s, password) = password FROM users WHERE username = %s;", (password, username))
        row = cur.fetchall()

        if(username == "" or not (user_exists)):
            self.messagedialog1.format_secondary_text("Nome de usuário inválido, tente novamente.")
            self.messagedialog1.show()
            self.username_entry_in_register.grab_focus()
        elif(password == "" or len(password) < 8 or not (row[0][0])):
            self.messagedialog1.format_secondary_text("Senha inválida, tente novamente.")
            self.messagedialog1.show()
            self.password_entry_in_register.grab_focus()
        else:
            if not (user_exists):
                self.messagedialog1.format_secondary_text("Nome de usuário inválido, tente novamente.")
                self.messagedialog1.show()
                self.username_entry_in_register.grab_focus()
            else:
                user_ID = str(i)
                print("Login as " + username)
                self.login_window.hide()
                self.window.set_title(self.window.get_title() + " - " + username)
                self.window.show_all()
                self.progressbar1.set_visible(False)
        
    def on_register_new_user_button_clicked(self, widget):
        print("Register Window")
        self.full_name_entry_in_register.set_text("")
        self.username_entry_in_register.set_text("")
        self.password_entry_in_register.set_text("")
        self.password_check_entry_in_register.set_text("")
        self.email_entry_in_register.set_text("")
        self.adm_password_entry_in_register.set_text("")
        self.register_window.show()

    def on_register_user_button_clicked(self, widget):
        global cur

        self.messagedialog1.set_transient_for(self.register_window)
        name = self.full_name_entry_in_register.get_text()
        username = self.username_entry_in_register.get_text()
        password = self.password_entry_in_register.get_text()
        password_check = self.password_check_entry_in_register.get_text()
        email = self.email_entry_in_register.get_text()
        adm_password = self.adm_password_entry_in_register.get_text()

        cur.execute("SELECT username FROM users;")
        rows = cur.fetchall()
        user_exists = False
        i = 0
        while (not (user_exists)) and (i<len(rows)):
            if(rows[i][0] == username):
                user_exists = True
            i+=1

        adm_pass = False
        select = "SELECT crypt(%s, password) = password FROM users WHERE is_adm = TRUE;" % (adm_password)
        cur.execute(select)
        rows = cur.fetchall()
        for i in range(len(rows[0])):
            if(rows[0][i]):
                adm_pass = True

        if(name == ""):
            self.messagedialog1.format_secondary_text("Nome inválido, tente novamente.")
            self.messagedialog1.show()
            self.full_name_entry_in_register.grab_focus()
        elif(username == "" or user_exists):
            self.messagedialog1.format_secondary_text("Nome de usuário inválido, tente novamente.")
            self.messagedialog1.show()
            self.username_entry_in_register.grab_focus()
        elif(password == "" or len(password) < 8):
            self.messagedialog1.format_secondary_text("Senha inválida, tente novamente.")
            self.messagedialog1.show()
            self.password_entry_in_register.grab_focus()
        elif(password != password_check):
            self.messagedialog1.format_secondary_text("Senhas não correspondem, tente novamente.")
            self.messagedialog1.show()
            self.password_check_entry_in_register.grab_focus()
        elif(email == ""):
            self.messagedialog1.format_secondary_text("E-mail inválido, tente novamente.")
            self.messagedialog1.show()
            self.email_entry_in_register.grab_focus()
        elif(adm_password == "" or  not (adm_pass)):
            self.messagedialog1.format_secondary_text("Senha do administrador inválida, tente novamente.")
            self.messagedialog1.show()
            self.email_entry_in_register.grab_focus()
        else:
            cur.execute("INSERT INTO users (name, username, password, email) VALUES (%s, %s, crypt(%s, gen_salt('md5')), %s);", (name, username, password, email))
            conn.commit()
            self.register_window.hide()
            self.username_entry_in_login.grab_focus()


    def close_register_window(self, arg1, arg2):
        self.register_window.hide()
        self.username_entry_in_login.grab_focus()

        return True
        
    def on_cancel_in_register_button_clicked(self, widget):
        self.register_window.hide()
        self.username_entry_in_login.grab_focus()
        
    def on_window1_destroy(self, object, data=None):
        print("Quit with cancel")
        cur.close()
        conn.close()
        Gtk.main_quit()

    def on_gtk_quit_activate(self, menuitem, data=None):
        print("Quit from menu")
        cur.close()
        conn.close()
        Gtk.main_quit()

    #Destroy and rebuild all
    def on_new_activate(self, menuitem, data=None):
        global is_pacient, pacient

        pacient = {}
        is_pacient = False

        self.ID_entry.set_text('')
        self.name_entry.set_text('')
        self.sex_combobox.set_active_id()
        self.age_entry.set_text('')
        self.height_entry.set_text('')
        self.weight.set_text('')
        self.imc.set_text('')
        self.name_entry.set_editable(True)
        self.age_entry.set_editable(True)
        self.height_entry.set_editable(True)
        self.name_entry.set_sensitive(True)
        self.age_entry.set_sensitive(True)
        self.height_entry.set_sensitive(True)
        self.sex_combobox.set_sensitive(True)

        self.combo_box_set_exam.remove_all()
        self.load_exam_button.set_sensitive(False)
        self.savepacient_button.set_sensitive(True)
        self.changepacientbutton.set_sensitive(False)
        self.axis.clear()
        self.axis.set_ylabel('AP')
        self.axis.set_xlabel('ML')
        self.axis2.clear()
        self.axis2.set_ylabel('AP')
        self.axis2.set_xlabel('ML')
        self.axis3.clear()
        self.axis3.set_ylabel('AP')
        self.axis3.set_xlabel('MP')
        self.progressbar1.set_visible(False)

    def on_open_activate(self, menuitem, data=None):
        global cur, is_pacient

        is_pacient = False

        self.pacient_label_in_load.set_text("")

        #Fills the combobox with pacients names
        self.combobox_in_load_pacient.remove_all()
        cur.execute("SELECT id, name FROM pacients ORDER BY id;")
        rows = cur.fetchall()
        for row in rows:
            self.combobox_in_load_pacient.append(str(row[0]),str(row[0]) + ' - ' + row[1])

        #Shows the window to load a pacient
        self.load_pacient_window.show()

    #Gets the signal of changing at pacients_combobox
    def on_combobox_in_load_pacient_changed(self, widget):
        global cur, pacient

        self.pacient_label_in_load.set_text("")

        #Gets the active row ID at pacients_combobox
        ID = self.combobox_in_load_pacient.get_active_id()
        ID = str(ID)

        if(ID != "None"):
            #Selects the active row from table pacients
            select = "SELECT * FROM pacients WHERE id = %s;" % (ID)
            cur.execute(select)
            row = cur.fetchall()

            #Fills the pacient with row content
            name = str(row[0][1])
            sex = str(row[0][2])
            sex = sex[0]
            age = str(row[0][3])
            height = str(row[0][4])
            weight = str(row[0][5])
            imc = str(row[0][6])

            self.pacient_label_in_load.set_text('Nome: ' + name +
                '\n' + 'Sexo: ' + sex +
                '\n' + 'Idade: ' + age +
                '\n' + 'Altura: ' + height +
                '\n' + 'Peso: ' + weight +
                '\n' + 'IMC: ' + imc)

            pacient = {'Nome': name, 'ID': ID, 'Sexo': sex, 'Idade': age, 'Altura': height, 'Peso' : weight, 'IMC': imc}


    def on_load_pacient_button_clicked(self, widget):
        global pacient, cur, is_pacient

        is_pacient = True

        #Clears graphs and label contents
        self.pacient_label_in_load.set_text("")
        self.combo_box_set_exam.remove_all()
        self.axis.clear()
        self.axis.set_ylabel('AP')
        self.axis.set_xlabel('ML')
        self.axis2.clear()
        self.axis2.set_ylabel('AP')
        self.axis2.set_xlabel('ML')

        #Fill the main window with pacient data
        self.ID_entry.set_text(pacient['ID'])
        self.name_entry.set_text(pacient['Nome'])
        self.age_entry.set_text(pacient['Idade'])
        self.height_entry.set_text(pacient['Altura'])
        if(pacient['Sexo'] == 'M'):
            self.sex_combobox.set_active_id('0')
        elif(pacient['Sexo'] == 'F'):
            self.sex_combobox.set_active_id('1')
        else:
            self.sex_combobox.set_active_id('2')
        self.weight.set_text(pacient['Peso'])
        self.imc.set_text(pacient['IMC'])
        self.sex_combobox.set_sensitive(False)
        self.name_entry.set_sensitive(False)
        self.age_entry.set_sensitive(False)
        self.height_entry.set_sensitive(False)
        self.savepacient_button.set_sensitive(False)
        self.changepacientbutton.set_sensitive(True)
        self.load_pacient_window.hide()
        self.capture_button.set_sensitive(True)

        #Fills the exams_combobox with the dates of current pacient exams
        cur.execute("SELECT * FROM exams WHERE pac_id = (%s)", (pacient['ID']))
        rows = cur.fetchall()
        i=1
        for row in rows:
            self.combo_box_set_exam.append(str(row[0]), str(i) + ' - ' + str(row[3]))
            i+=1

        if(len(rows)):
            self.combo_box_set_exam.set_sensitive(True)
            self.load_exam_button.set_sensitive(True)
        else:
            self.combo_box_set_exam.set_sensitive(False)
            self.load_exam_button.set_sensitive(False)

    def on_cancel_in_load_button_clicked(self, widget):
        self.pacient_label_in_load.set_text("")
        self.load_pacient_window.hide()

    #Gets the signal of changing at exams_combobox
    def on_combo_box_set_exam_changed(self, widget):
        global cur, pacient, APs, MLs

        #Gets the active row ID at exams_combobox
        ID = self.combo_box_set_exam.get_active_id()
        ID = str(ID)

        if(ID != "None"):
            #Selects the active row from table exams
            select = "SELECT aps, mls FROM exams WHERE id = %s" % (ID)
            cur.execute(select)
            row = cur.fetchall()

            APs = []
            MLs = []

            for x in row[0][0]:
                APs.append(float(x))
            for x in row[0][1]:
                MLs.append(float(x))

    def on_load_exam_button_clicked(self, widget):
        global APs, MLs

        max_absoluto_AP = calc.valorAbsoluto(min(APs), max(APs))
        max_absoluto_ML = calc.valorAbsoluto(min(MLs), max(MLs))

        max_absoluto_AP *= 1.25
        max_absoluto_ML *= 1.25

        print('max_absoluto_AP:',max_absoluto_AP,'max_absoluto_ML:',max_absoluto_ML)

        self.axis.clear()
        self.axis.set_ylabel('AP')
        self.axis.set_xlabel('ML')
        self.axis.set_xlim(-max_absoluto_ML, max_absoluto_ML)
        self.axis.set_ylim(-max_absoluto_AP, max_absoluto_AP)
        self.axis.plot(MLs, APs,'.-',color='r')
        self.canvas.draw()

        APs_Processado, MLs_Processado = calc.geraAP_ML(APs, MLs)

        dis_resultante_total = calc.distanciaResultante(APs_Processado, MLs_Processado)
        dis_resultante_AP = calc.distanciaResultanteParcial(APs_Processado)
        dis_resultante_ML = calc.distanciaResultanteParcial(MLs_Processado)

        dis_media = calc.distanciaMedia(dis_resultante_total)

        dis_rms_total = calc.distRMS(dis_resultante_total)
        dis_rms_AP = calc.distRMS(dis_resultante_AP)
        dis_rms_ML = calc.distRMS(dis_resultante_ML)

        totex_total = calc.totex(APs_Processado, MLs_Processado)
        totex_AP = calc.totexParcial(APs_Processado)
        totex_ML = calc.totexParcial(MLs_Processado)

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

        max_absoluto_AP = calc.valorAbsoluto(min(APs_Processado), max(APs_Processado))
        max_absoluto_ML = calc.valorAbsoluto(min(MLs_Processado), max(MLs_Processado))

        max_absoluto_AP *=1.25
        max_absoluto_ML *=1.25

        print('max_absoluto_AP:', max_absoluto_AP, 'max_absoluto_ML:', max_absoluto_ML)
        
        self.axis2.clear()
        self.axis2.set_xlim(-max_absoluto_ML, max_absoluto_ML)
        self.axis2.set_ylim(-max_absoluto_AP, max_absoluto_AP)
        self.axis2.plot(MLs_Processado, APs_Processado,'.-',color='g')
        self.axis2.set_ylabel('AP')
        self.axis2.set_xlabel('ML')
        self.canvas2.draw()
        
    #Show newdevicewindow1
    def on_new_device_activate(self, menuitem, data=None):
        print("Adicionando novo dispositivo")
        self.add_as_default_button_in_add_device.set_active(False)
        self.newdevicewindow1.show()

    def on_add_button_in_add_device_clicked(self, widget):

        self.messagedialog1.set_transient_for(self.newdevicewindow1)
        name = self.device_name_in_new.get_text()
        mac = self.device_mac_in_new.get_text()
        is_default = self.add_as_default_button_in_add_device.get_active()

        if (name == ""):
            self.messagedialog1.format_secondary_text("Nome inválido, tente novamente.")
            self.messagedialog1.show()
        elif((mac == "") or not (iva(mac))):
            self.messagedialog1.format_secondary_text("MAC inválido, tente novamente.")
            self.messagedialog1.show()
        else:
            WBB = {'Nome':name, 'MAC':mac, 'Padrao' : is_default}
            #manArq.saveWBB(WBB)
            if(is_default):
                cur.execute("SELECT * FROM devices_id_seq;")
                row = cur.fetchall()
                ID = row[0][1]
                cur.execute("UPDATE devices SET is_default = FALSE;")
            cur.execute("INSERT INTO devices (name, mac, is_default) VALUES (%s, %s, %s);", (name, mac, is_default))
            conn.commit()
            self.device_name_in_new.set_text("")
            self.device_mac_in_new.set_text("")
            self.newdevicewindow1.hide()
            self.window.get_focus()

    #Disconnet wiimote
    def on_disconnect_activate(self, menuitem, data=None):
        global wiimote, is_connected
        conect.closeConection(wiimote)
        is_connected = False
        self.batterylabel.set_text("Bateria:")
        self.image_statusbar1.set_from_file("red.png")
        self.label_statusbar1.set_text("Não conectado")

    def close_load_pacient_window(self, arg1, arg2):
        self.load_pacient_window.hide()
        self.window.get_focus()
        return True

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

    def on_cancel_in_saved_button_clicked(self, widget):
        print("Seleção de dispositivo cancelada")
        self.saveddeviceswindow1.hide()

        #Show searchdevicewindow1
    def on_search_device_activate(self, menuitem, data=None):
        self.combo_box_text_in_search.remove_all()
        self.spinner_in_search.start()
        self.searchdevicewindow1.show()

    def on_start_search_button_clicked(self, widget):
        global is_connected, devices

        self.batterylabel.set_text("Bateria:")
        is_connected = False

        self.image_statusbar1.set_from_file("red.png")
        self.label_statusbar1.set_text("Não conectado")

        print("Buscando novo dispositivo")

        devices = conect.searchWBB()
        
        self.combo_box_text_in_search.remove_all()
        device_ID = 0
        for addr, name in devices:
            self.combo_box_text_in_search.append(str(device_ID), 'Nome: ' + name + '\nMAC: ' + addr)
            device_ID += 1

        self.connect_button_in_search.set_sensitive(True)
        self.save_device_in_search.set_sensitive(True)
        self.spinner_in_search.stop()

    def on_connect_button_in_search_clicked(self, widget):
        global wiimote, battery, is_connected, devices

        device_ID = int(self.combo_box_text_in_search.get_active_id())

        wiimote, battery = conect.connectToWBB(devices[device_ID][0])

        if(wiimote):
            is_connected = True
            self.batterylabel.set_text("Bateria: " + str(int(100*battery))+"%")
            self.batterylabel.set_visible(True)
            self.image_statusbar1.set_from_file("green.png")
            self.label_statusbar1.set_text("Conectado")
            self.capture_button.set_sensitive(True)
    
    def on_save_device_in_search_clicked(self, widget):
        global devices

        device_ID = int(self.combo_box_text_in_search.get_active_id())

        self.device_name_in_new.set_text(devices[device_ID][1])
        self.device_mac_in_new.set_text(devices[device_ID][0])
        self.device_mac_in_new.set_sensitive(False)
        self.newdevicewindow1.show()

    def on_cancel_in_search_clicked(self, widget):
        self.connect_button_in_search.set_sensitive(False)
        self.save_device_in_search.set_sensitive(False)
        self.spinner_in_search.stop()
        self.searchdevicewindow1.hide()
        self.window.get_focus()

    #Show saved devices window
    def on_connect_to_saved_device_activate(self, menuitem, data=None):
        global cur, is_connected

        is_connected = False

        #Fills the combobox with devices names
        self.combo_box_in_saved.remove_all()
        cur.execute("SELECT id, name, is_default FROM devices;")
        rows = cur.fetchall()
        for row in rows:
            self.combo_box_in_saved.append(str(row[0]), row[1])
            if(row[2]):
                self.combo_box_in_saved.set_active_id(str(row[0]))
        self.saveddeviceswindow1.show()

       #Saved devices selection
    def on_combo_box_in_saved_changed(self, widget):
        global cur

        #Gets the active row ID at pacients_combobox
        ID = self.combo_box_in_saved.get_active_id()
        ID = str(ID)

        if(ID != "None"):
            #Selects the active row from table devices
            cur.execute("SELECT mac FROM devices WHERE id = (%s);", (ID))
            row = cur.fetchall()

            self.mac_entry_in_saved.set_text(row[0][0])
            self.connect_in_saved_button.set_sensitive(True)
            self.instructions_on_saved_box.set_visible(True)

    def on_connect_in_saved_button_clicked(self, widget):
        global wiimote, battery, is_connected

        self.batterylabel.set_text("Bateria:")
        self.image_statusbar1.set_from_file("red.png")
        self.label_statusbar1.set_text("Não conectado")

        MAC = self.mac_entry_in_saved.get_text()
        print (MAC)

        wiimote, battery = conect.connectToWBB(MAC)

        if(wiimote):
            is_connected = True

            self.batterylabel.set_text("Bateria: " + str(int(100*battery))+"%")
            self.batterylabel.set_visible(True)

            self.image_statusbar1.set_from_file("green.png")
            self.label_statusbar1.set_text("Conectado")
            self.instructions_on_saved_box.set_visible(False)
            self.connect_in_saved_button.set_sensitive(False)
            self.saveddeviceswindow1.hide()
            self.window.get_focus()
            self.capture_button.set_sensitive(True)

    def on_cancel_button_in_add_device_clicked(self, widget):
        print("Adição de dispositivo cancelada")
        self.newdevicewindow1.hide()

    def on_device_mac_activate(self, widget):
        print("Dispositivo adicionado")
        self.newdevicewindow1.hide()

    def on_boxOriginal_button_press_event(self, widget, event):
        global child, relative, nt
        if event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS and event.button == 1:
            print("Janela Avançada")

            self.boxOriginal.set_focus_child(self.canvas)
            relative = self.boxOriginal
            child = relative.get_focus_child()
            relative.remove(child)
            self.boxAdvanced.pack_start(child, expand=True, fill=True, padding=0)
            nt = NavigationToolbar(child, self.advancedgraphswindow)
            self.boxAdvanced.pack_start(nt, expand=False, fill=True, padding=0)
            self.advancedgraphswindow.show()

    def on_boxProcessado_button_press_event(self, widget, event):
        global child, relative, nt
        if event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS and event.button == 1:
            print("Janela Avançada")

            self.boxProcessado.set_focus_child(self.canvas2)
            relative = self.boxProcessado
            child = relative.get_focus_child()
            relative.remove(child)
            self.boxAdvanced.pack_start(child, expand=True, fill=True, padding=0)
            nt = NavigationToolbar(child, self.advancedgraphswindow)
            self.boxAdvanced.pack_start(nt, expand=False, fill=True, padding=0)
            self.advancedgraphswindow.show()

    def on_boxFourier_button_press_event(self, widget, event):
        global child, relative, nt
        if event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS and event.button == 1:
            print("Janela Avançada")

            self.boxFourier.set_focus_child(self.canvas3)
            relative = self.boxFourier
            child = relative.get_focus_child()
            relative.remove(child)
            self.boxAdvanced.pack_start(child, expand=True, fill=True, padding=0)
            nt = NavigationToolbar(child, self.advancedgraphswindow)
            self.boxAdvanced.pack_start(nt, expand=False, fill=True, padding=0)
            self.advancedgraphswindow.show()

    def on_cancel_in_standup_clicked(self, widget):
        self.standupwindow1.hide()

    def on_messagedialog1_close_clicked(self, widget):
        self.messagedialog1.hide()

    def on_savepacient_button_clicked(self, widget):
        global pacient, cur, conn, modifying, is_pacient

        is_pacient = False

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
            self.sex_combobox.grab_focus()
        elif(age == ""):
            self.messagedialog1.format_secondary_text("Idade inválida, tente novamente.")
            self.messagedialog1.show()
            self.age_entry.grab_focus()
        elif(height == ""):
            self.messagedialog1.format_secondary_text("Altura inválida, tente novamente.")
            self.messagedialog1.show()
            self.height_entry.grab_focus()
        else:
            height = height.replace(',', '.', 1)
            self.savepacient_button.set_sensitive(False)
            self.name_entry.set_editable(False)
            self.age_entry.set_editable(False)
            self.height_entry.set_editable(False)
            self.height_entry.set_text(height)
            self.ID_entry.set_editable(False)
            self.name_entry.set_sensitive(False)
            self.sex_combobox.set_sensitive(False)
            self.age_entry.set_sensitive(False)
            self.height_entry.set_sensitive(False)
            self.ID_entry.set_sensitive(False)
            self.capture_button.set_sensitive(True)
            if not modifying:
                cur.execute("INSERT INTO pacients (name, sex, age, height) VALUES (%s, %s, %s, %s);",(name, sex, age, height))
                conn.commit()
                cur.execute("SELECT * FROM pacients ORDER BY id;")
                rows = cur.fetchall()
                print ("\nShow me the databases:\n")
                for row in rows:
                    print (row)
                cur.execute("SELECT * FROM pacients_id_seq;")
                row = cur.fetchall()
                ID = row[0][1]
                pacient = {'Nome': name, 'ID': ID, 'Sexo': sex, 'Idade': age, 'Altura': height}
                self.ID_entry.set_text(str(ID))
                #manArq.makeDir(str(ID) + ' - ' + name)
                #path = str(pacient['ID']) + ' - ' + pacient['Nome']
                #manArq.savePacient(pacient, path)
            else:
                #pathOld = str(pacient['ID']) + ' - ' + pacient['Nome']
                #pathNew = str(pacient['ID']) + ' - ' + name
                #manArq.renameDir(pathOld, pathNew)
                #pathOld = pathNew + '/' + pacient['Nome'] + ".xls"
                #pathNew = str(pacient['ID']) + ' - ' + name + '/' + name + ".xls"
                #manArq.renameDir(pathOld, pathNew)
                cur.execute("UPDATE pacients SET sex = (%s), age = (%s), height = (%s), name = (%s) WHERE id = (%s);", (sex, age, height, name, pacient['ID']))
                conn.commit()
                pacient['Nome'] = name
                pacient['Sexo'] = sex
                pacient['Idade'] = age
                pacient['Altura'] = height
                #manArq.savePacient(pacient, str(pacient['ID']) + ' - ' + name)
            print("Paciente salvo")
            self.changepacientbutton.set_sensitive(True)
            is_pacient = True

    def on_changepacientbutton_clicked(self, widget):
        global modifying
        modifying = True
        self.savepacient_button.set_sensitive(True)
        self.name_entry.set_editable(True)
        self.age_entry.set_editable(True)
        self.height_entry.set_editable(True)
        self.ID_entry.set_editable(True)
        self.name_entry.set_sensitive(True)
        self.sex_combobox.set_sensitive(True)
        self.age_entry.set_sensitive(True)
        self.height_entry.set_sensitive(True)
        self.changepacientbutton.set_sensitive(False)

    def on_capture_button_clicked(self, widget):
        global is_connected, is_pacient

        if(not is_pacient):
            self.messagedialog1.format_secondary_text("É preciso cadastrar ou carregar um paciente para realizar o processo de captura.")
            self.messagedialog1.show()
        elif(not is_connected):
            self.messagedialog1.format_secondary_text("É preciso conectar a um dispositivo para realizar o processo de captura..")
            self.messagedialog1.show()
        else:
            self.progressbar1.set_fraction(0)
            self.standupwindow1.show()

    def on_start_capture_button_clicked(self, widget):
        self.standupwindow1.hide()
        self.axis.clear()
        self.axis.set_ylabel('AP')
        self.axis.set_xlabel('ML')
        self.axis2.clear()
        self.axis2.set_ylabel('AP')
        self.axis2.set_xlabel('ML')
        self.axis3.clear()
        self.axis.set_ylabel('AP')
        self.axis.set_xlabel('ML')

        self.progressbar1.set_visible(True)

        global APs, MLs, pacient, wiimote, cur, conn

        balance, weights, pontos = calc.calcPontos(self, wiimote)
        midWeight = calc.calcPesoMedio(weights)
        imc = calc.calcIMC(midWeight, float(pacient['Altura']))

        self.points_entry.set_text(str(pontos))

        pacient['Peso'] = round(midWeight, 2)
        pacient['IMC'] = round(imc,1)

        cur.execute("UPDATE pacients SET weight = (%s), imc = (%s) WHERE name = (%s);", (pacient['Peso'], pacient['IMC'], pacient['Nome']))
        conn.commit()

        APs = []
        MLs = []

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
        self.axis.set_xlabel('ML')
        self.axis.set_xlim(-max_absoluto_ML, max_absoluto_ML)
        self.axis.set_ylim(-max_absoluto_AP, max_absoluto_AP)
        self.axis.plot(MLs, APs,'.-',color='r')
        self.canvas.draw()

        APs_Processado, MLs_Processado = calc.geraAP_ML(APs, MLs)

        dis_resultante_total = calc.distanciaResultante(APs_Processado, MLs_Processado)
        dis_resultante_AP = calc.distanciaResultanteParcial(APs_Processado)
        dis_resultante_ML = calc.distanciaResultanteParcial(MLs_Processado)

        dis_media = calc.distanciaMedia(dis_resultante_total)

        dis_rms_total = calc.distRMS(dis_resultante_total)
        dis_rms_AP = calc.distRMS(dis_resultante_AP)
        dis_rms_ML = calc.distRMS(dis_resultante_ML)

        totex_total = calc.totex(APs_Processado, MLs_Processado)
        totex_AP = calc.totexParcial(APs_Processado)
        totex_ML = calc.totexParcial(MLs_Processado)

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

        max_absoluto_AP = calc.valorAbsoluto(min(APs_Processado), max(APs_Processado))
        max_absoluto_ML = calc.valorAbsoluto(min(MLs_Processado), max(MLs_Processado))

        max_absoluto_AP *=1.25
        max_absoluto_ML *=1.25

        print('max_absoluto_AP:', max_absoluto_AP, 'max_absoluto_ML:', max_absoluto_ML)
        self.axis2.clear()

        self.axis2.set_xlim(-max_absoluto_ML, max_absoluto_ML)
        self.axis2.set_ylim(-max_absoluto_AP, max_absoluto_AP)

        self.axis2.plot(MLs_Processado, APs_Processado,'.-',color='g')
        self.axis2.set_ylabel('AP')
        self.axis2.set_xlabel('ML')
        self.canvas2.draw()
        self.weight.set_text(str(midWeight))
        self.weight.set_max_length(6)
        self.imc.set_text(str(imc))
        self.imc.set_max_length(5)
        self.save_exam_button.set_sensitive(True)

    def on_save_exam_button_clicked(self, widget):
        global pacient, APs, MLs, cur, conn, user_ID
        cur.execute("INSERT INTO exams (APs, MLs, pac_id, usr_id) VALUES (%s, %s, %s, %s)", (APs, MLs, pacient['ID'], user_ID))
        conn.commit()
        #path = 'Pacients/' + str(pacient['ID']) + ' - ' + pacient['Nome']
        #self.fig.canvas.print_png(str(path + '/grafico original'))
        #self.fig2.canvas.print_png(str(path + '/grafico processado'))
        #manArq.saveExam(pacient, APs, MLs, path)
        self.combo_box_set_exam.set_active_id("0")
        self.combo_box_set_exam.set_sensitive(True)
        self.load_exam_button.set_sensitive(True)
        print("Exame Salvo")
        self.save_exam_button.set_sensitive(False)

    def __init__(self):
        global modifying, is_connected, is_pacient

        modifying = False
        is_connected = False
        is_pacient = False

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
        self.instructions_on_saved_box = go("instructions_on_saved_box")

        #Windows
        self.login_window = go("login_window")
        self.register_window = go("register_window")
        self.window = go("window1")
        self.newdevicewindow1 = go("newdevicewindow1")
        self.messagedialog1 = go("messagedialog1")
        self.standupwindow1 = go("standupwindow1")
        self.searchdevicewindow1 = go("searchdevicewindow1")
        self.saveddeviceswindow1 = go("saveddeviceswindow1")
        self.advancedgraphswindow = go("advancedgraphswindow")
        self.load_pacient_window = go("load_pacient_window")

        #Delete-events
        self.register_window.connect("delete-event", self.close_register_window)
        self.searchdevicewindow1.connect("delete-event", self.close_searchdevicewindow1)
        self.newdevicewindow1.connect("delete-event", self.close_newdevicewindow1)
        self.standupwindow1.connect("delete-event", self.close_standupwindow1)
        self.saveddeviceswindow1.connect("delete-event", self.close_saveddeviceswindow1)
        self.advancedgraphswindow.connect("delete-event", self.close_advancedgraphswindow)
        self.load_pacient_window.connect("delete-event", self.close_load_pacient_window)

        #Images
        self.image_statusbar1 = go("image_statusbar1")
        self.image_in_saved = go("image_in_saved")

        #Grids
        self.grid_graphs = go("grid_graphs")

        #Separators
        self.separator_in_saved_devices = go("separator_in_saved_devices")

        #Buttons
        self.login_button = go("login_button")
        self.capture_button = go("capture_button")
        self.savepacient_button = go("savepacient_button")
        self.changepacientbutton = go("changepacientbutton")
        self.start_capture_button = go("start_capture_button")
        self.save_device_in_search = go("save_device_in_search")
        self.connect_button_in_search = go("connect_button_in_search")
        self.connect_in_saved_button = go("connect_in_saved_button")
        self.save_exam_button = go("save_exam_button")
        self.load_exam_button = go("load_exam_button")
        self.add_as_default_button_in_add_device = go("add_as_default_button_in_add_device")

        #Spinners
        self.spinner_in_search = go("spinner_in_search")

        #Labels
        self.label_statusbar1 = go("label_statusbar1")
        self.batterylabel = go("batterylabel")
        self.instructionslabel_in_saved = go("instructionslabel_in_saved")
        self.pacient_label_in_load = go("pacient_label_in_load")

        #Entrys
        self.username_entry_in_login = go("username_entry_in_login")
        self.password_entry_in_login = go("password_entry_in_login")
        self.full_name_entry_in_register = go("full_name_entry_in_register")
        self.username_entry_in_register = go("username_entry_in_register")
        self.password_entry_in_register = go("password_entry_in_register")
        self.password_check_entry_in_register = go("password_check_entry_in_register")
        self.email_entry_in_register = go("email_entry_in_register")
        self.adm_password_entry_in_register = go("adm_password_entry_in_register")
        self.name_entry = go("name_entry")
        self.age_entry = go("age_entry")
        self.height_entry = go("height_entry")
        self.ID_entry = go("ID_entry")
        self.weight = go("weight")
        self.imc = go("imc")
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
        self.combo_box_text_in_search = go("combo_box_text_in_search")
        self.sex_combobox = go("sex_combobox")
        self.combobox_in_load_pacient = go("combobox_in_load_pacient")
        self.combo_box_set_exam = go("combo_box_set_exam")

        #Bars
        self.progressbar1 = go("progressbar1")

        #Plots
        '''Original Graph'''
        self.fig = plt.figure(dpi=50)
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

        self.login_window.show()


if __name__ == "__main__":
    global conn, cur

    '''Connecting to DB'''
    conn = psycopg2.connect("dbname=iem_wbb host=localhost user=postgres password=postgres")
    '''Opening DB cursor'''
    cur = conn.cursor()
    '''Creating tables'''
    #try:
    #    cur.execute("CREATE TABLE pacients(id serial PRIMARY KEY, name text, sex char(5), age smallint, height numeric(3,2), weight numeric(5,2), imc numeric(3,1));")
    #    cur.execute("CREATE TABLE exams(id SERIAL PRIMARY KEY, APs NUMERIC(16,15)[], MLs NUMERIC(16,15)[], date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(), pac_id INT REFERENCES pacients(id));")
    #    cur.execute("CREATE TABLE devices(id SERIAL PRIMARY KEY,name VARCHAR(50),mac VARCHAR(17));")
    #    conn.commit()
    #except:
    #       print("Can't create table. Maybe it already exists.")
    
    #while(Gtk.events_pending()):
    #        Gtk.main_iteration()
    
    main = Iem_wbb()
    Gtk.main()
