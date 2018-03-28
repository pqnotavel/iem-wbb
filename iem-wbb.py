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
import conexao as connect
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



global battery, child, relative, nt, conn, cur

class Iem_wbb:
    
    def on_continue_button_clicked(self, widget):
        self.calibration_equipment_window.hide()
        self.calibration_window.show_all()

    def on_start_calibration_button_clicked(self, widget):
        if(not self.is_connected):
            self.message_dialog_window.set_transient_for(self.calibration_window)
            self.message_dialog_window.format_secondary_text("É preciso conectar a um dispositivo para realizar o processo de captura.")
            self.message_dialog_window.show()
        else:
            self.calibration_image.set_sensitive(True)
            self.scale_button.set_sensitive(True)
            self.start_calibration_button.set_sensitive(False)
            self.calibration_image.set_from_file(self.calibration_images[self.current_image])
            text = "Ajuste o peso de %dkg no ponto %d" % (self.calibration_weights[self.current_weight], self.current_image+1)
            self.calibration_label.set_text(text)
            self.progressbar.set_visible(True)
            self.calibration_results_weights = []
            self.calibration_results_coordenates = []

    def on_scale_button_clicked(self, widget):
        self.scale_button.set_sensitive(False)
        balance, weights, pontos = calc.calcPontos(self, self.wiimote, 0)
        midWeight = calc.calcPesoMedio(weights)
        self.progressbar.set_fraction(0)

        Xs = 0.0
        Ys = 0.0

        for (x,y) in balance:
            Xs+=x
            Ys+=y

        Xs /= pontos
        Ys /= pontos
        Xs = round(Xs, 3)
        Ys = round(Ys, 3)
        midWeight = round(midWeight, 2)

        self.calibration_results_weights.append(midWeight)
        self.calibration_results_coordenates.append((Xs, Ys))

        #self.axis4.plot(Xs, Ys, 'ro')
        self.axis4.plot(Xs, -Ys, 'ro')
        self.canvas4.draw()
    
        self.scale_button.set_sensitive(True)

        label_teste = Gtk.Label.new("\t\t\t%dkg\n\n|Peso \t|\t\tX \t|\t\tY\t|\n|%.2f\t|\t%.3f\t|\t%.3f\t|" % (self.calibration_weights[self.current_weight], midWeight, Xs, Ys))
        self.grid_resultados.attach(label_teste, self.current_image, self.current_weight+1, 1, 1)
        label_teste.set_visible(True)

        if(self.current_image == (len(self.calibration_images) - 1)):
            if(self.current_weight == (len(self.calibration_weights) - 1)):
                self.scale_button.set_sensitive(False)
                self.calibration_image.set_sensitive(False)
                self.calibration_image.set_from_file("test_cal_2.png")
            else:
                self.current_weight = (self.current_weight + 1) % len(self.calibration_weights)

        if(self.scale_button.get_sensitive()):
            self.current_image = (self.current_image + 1) % len(self.calibration_images)
            self.calibration_image.set_from_file(self.calibration_images[self.current_image])
            text = "Ajuste o peso de %dkg no ponto %d" % (self.calibration_weights[self.current_weight], self.current_image+1)
            self.calibration_label.set_text(text)
        else:
            self.calibration_label.set_text("Fim da calibração")


    def on_save_as_activate(self, menuitem, data=None):
        global APs, MLs
        #, cur, conn, user_ID
        
        path = str('./Pacients/' + self.pacient['ID']) + ' - ' + self.pacient['Nome']
        
        if(self.is_pacient and self.is_exam):
            '''manArq.importXlS(pacient, APs, MLs, path)
                                                print("Salvo")'''
            dialog = Gtk.FileChooserDialog("Salvar como", self.main_window,
                Gtk.FileChooserAction.SAVE,
                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_SAVE, Gtk.ResponseType.OK))

            dialog.set_do_overwrite_confirmation(True)

            self.add_filters(dialog)
            dialog.set_current_folder(path)
            dialog.set_current_name(self.pacient['Nome']+'.xls')

            response = dialog.run()
            dialog.set_filename('.xls')
            if response == Gtk.ResponseType.OK:
                #manArq.makeDir(path)
                print(dialog.get_filename())
                manArq.importXlS(pacient, APs, MLs, dialog.get_filename())
                print("Salvo")
                self.main_window.get_focus()
            elif response == Gtk.ResponseType.CANCEL:
                print("Cancelado")
                self.main_window.get_focus()

            dialog.destroy()
        else:
            self.message_dialog_window.set_transient_for(self.main_window)
            self.message_dialog_window.format_secondary_text("Não há usuário ou exame carregado.")
            self.message_dialog_window.show()

        self.main_window.get_focus()

    def add_filters(self, dialog):
        filter_text = Gtk.FileFilter()
        filter_text.set_name(".xls")
        filter_text.add_mime_type("application/x-msexcel")
        dialog.add_filter(filter_text)

        #filter_py = Gtk.FileFilter()
        #filter_py.set_name("Python files")
        #filter_py.add_mime_type("text/x-python")
        #dialog.add_filter(filter_py)

        filter_any = Gtk.FileFilter()
        filter_any.set_name("Todos os arquivos")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)

    def on_calibration_window_destroy(self, object, data=None):
        print("Quit in calibration_window from menu")
        cur.close()
        conn.close()
        Gtk.main_quit()

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

    def clear_all(self):
        self.pacient = {}
        self.is_pacient = False

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
        self.progressbar.set_visible(False)

    def on_login_button_clicked(self, widget):
        global cur, user_ID

        self.message_dialog_window.set_transient_for(self.login_window)
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
            self.message_dialog_window.format_secondary_text("Nome de usuário inválido, tente novamente.")
            self.message_dialog_window.show()
            self.username_entry_in_login.grab_focus()
        elif(password == "" or len(password) < 8 or not (row[0][0])):
            self.message_dialog_window.format_secondary_text("Senha inválida, tente novamente.")
            self.message_dialog_window.show()
            self.password_entry_in_login.grab_focus()
        else:
            user_ID = str(i)
            print("Login as " + username)
            self.login_window.hide()
            self.main_window.set_title("IEM_WBB" + " - " + username)
            self.main_window.show_all()
            self.progressbar.set_visible(False)
            self.username_entry_in_login.set_text("")
            self.password_entry_in_login.set_text("")

    def on_register_new_user_button_clicked(self, widget):
        print("Register Window")

        #Window
        self.register_window = self.builder.get_object("register_window")

        #Entrys
        self.full_name_entry_in_register = self.builder.get_object("full_name_entry_in_register")
        self.username_entry_in_register = self.builder.get_object("username_entry_in_register")
        self.password_entry_in_register = self.builder.get_object("password_entry_in_register")
        self.password_check_entry_in_register = self.builder.get_object("password_check_entry_in_register")
        self.email_entry_in_register = self.builder.get_object("email_entry_in_register")
        self.adm_password_entry_in_register = self.builder.get_object("adm_password_entry_in_register")
        
        #Button
        self.is_adm_button_in_register = self.builder.get_object("is_adm_button_in_register")

        self.full_name_entry_in_register.set_text("")
        self.username_entry_in_register.set_text("")
        self.password_entry_in_register.set_text("")
        self.password_check_entry_in_register.set_text("")
        self.email_entry_in_register.set_text("")
        self.adm_password_entry_in_register.set_text("")
        
        self.full_name_entry_in_register.grab_focus()
        self.register_window.show()

    def on_register_user_button_clicked(self, widget):
        global cur

        self.message_dialog_window.set_transient_for(self.register_window)
        name = self.full_name_entry_in_register.get_text()
        username = self.username_entry_in_register.get_text()
        password = self.password_entry_in_register.get_text()
        password_check = self.password_check_entry_in_register.get_text()
        email = self.email_entry_in_register.get_text()
        adm_password = self.adm_password_entry_in_register.get_text()
        is_adm = self.is_adm_button_in_register.get_active()

        cur.execute("SELECT username FROM users;")
        rows = cur.fetchall()
        user_exists = False
        i = 0
        while (not (user_exists)) and (i<len(rows)):
            if(rows[i][0] == username):
                user_exists = True
            i+=1

        if(name == ""):
            self.message_dialog_window.format_secondary_text("Nome inválido, tente novamente.")
            self.message_dialog_window.show()
            self.full_name_entry_in_register.grab_focus()
        elif(username == "" or user_exists):
            self.message_dialog_window.format_secondary_text("Nome de usuário inválido, tente novamente.")
            self.message_dialog_window.show()
            self.username_entry_in_register.grab_focus()
        elif(password == "" or len(password) < 8):
            self.message_dialog_window.format_secondary_text("Senha inválida, tente novamente.")
            self.message_dialog_window.show()
            self.password_entry_in_register.grab_focus()
        elif(password != password_check):
            self.message_dialog_window.format_secondary_text("Senhas não correspondem, tente novamente.")
            self.message_dialog_window.show()
            self.password_check_entry_in_register.grab_focus()
        elif(email == ""):
            self.message_dialog_window.format_secondary_text("E-mail inválido, tente novamente.")
            self.message_dialog_window.show()
            self.email_entry_in_register.grab_focus()
        elif(adm_password == "" or adm_password != "adm123"):
            self.message_dialog_window.format_secondary_text("Senha do administrador inválida, tente novamente.")
            self.message_dialog_window.show()
            self.email_entry_in_register.grab_focus()
        else:
            cur.execute("INSERT INTO users (name, username, password, email, is_adm) VALUES (%s, %s, crypt(%s, gen_salt('md5')), %s, %s);", (name, username, password, email, is_adm))
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

    def on_main_window_destroy(self, object, data=None):
        print("Quit with cancel")
        cur.close()
        conn.close()
        Gtk.main_quit()

    def on_gtk_quit_activate(self, menuitem, data=None):
        print("Quit from menu")
        self.main_window.hide()
        #self.calibration_window.hide()
        self.clear_all()
        self.username_entry_in_login.grab_focus()
        self.login_window.show()

    def on_new_activate(self, menuitem, data=None):
        self.clear_all()

    def on_open_activate(self, menuitem, data=None):
        global cur

        self.is_pacient = False

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
        global cur

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

            self.pacient = {'Nome': name, 'ID': ID, 'Sexo': sex, 'Idade': age, 'Altura': height, 'Peso' : weight, 'IMC': imc}

    def on_load_pacient_button_clicked(self, widget):
        global cur

        self.is_pacient = True

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
        self.ID_entry.set_text(self.pacient['ID'])
        self.name_entry.set_text(self.pacient['Nome'])
        self.age_entry.set_text(self.pacient['Idade'])
        self.height_entry.set_text(self.pacient['Altura'])
        if(self.pacient['Sexo'] == 'M'):
            self.sex_combobox.set_active_id('0')
        elif(self.pacient['Sexo'] == 'F'):
            self.sex_combobox.set_active_id('1')
        else:
            self.sex_combobox.set_active_id('2')

        self.weight.set_text(self.pacient['Peso'])
        self.imc.set_text(self.pacient['IMC'])
        self.sex_combobox.set_sensitive(False)
        self.name_entry.set_sensitive(False)
        self.age_entry.set_sensitive(False)
        self.height_entry.set_sensitive(False)
        self.savepacient_button.set_sensitive(False)
        self.changepacientbutton.set_sensitive(True)
        self.load_pacient_window.hide()
        self.capture_button.set_sensitive(True)

        #Fills the exams_combobox with the dates of current pacient exams
        cur.execute("SELECT * FROM exams WHERE pac_id = (%s)", (self.pacient['ID']))
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
        global cur, APs, MLs

        self.is_exam = False

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

        self.is_exam = True

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

    #Show new_device_window
    def on_new_device_activate(self, menuitem, data=None):
        print("Adicionando novo dispositivo")
        self.add_as_default_button_in_add_device.set_active(False)
        self.new_device_window.show()

    def on_add_button_in_add_device_clicked(self, widget):

        self.message_dialog_window.set_transient_for(self.new_device_window)
        name = self.device_name_in_new.get_text()
        mac = self.device_mac_in_new.get_text()
        is_default = self.add_as_default_button_in_add_device.get_active()

        if (name == ""):
            self.message_dialog_window.format_secondary_text("Nome inválido, tente novamente.")
            self.message_dialog_window.show()
        elif((mac == "") or not (iva(mac))):
            self.message_dialog_window.format_secondary_text("MAC inválido, tente novamente.")
            self.message_dialog_window.show()
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
            self.new_device_window.hide()
            self.main_window.get_focus()

    #Disconnet self.wiimote
    def on_disconnect_activate(self, menuitem, data=None):
        connect.closeConnection(self.wiimote)
        self.is_connected = False
        self.battery_label.set_text("Bateria:")
        self.battery_label.set_visible(False)
        self.status_image.set_from_file("bt_red.png")
        self.status_label.set_text("Não conectado")

    def close_load_pacient_window(self, arg1, arg2):
        self.load_pacient_window.hide()
        self.main_window.get_focus()
        return True

    def close_stand_up_window(self, arg1, arg2):
        self.stand_up_window.hide()
        self.main_window.get_focus()
        return True

    def close_search_device_window(self, arg1, arg2):
        self.search_device_window.hide()
        self.main_window.get_focus()
        return True

    def close_new_device_window(self, arg1, arg2):
        self.new_device_window.hide()
        return True

    def close_saved_devices_window(self, arg1, arg2):
        self.saved_devices_window.hide()
        return True

    def close_advanced_graphs_window(self, arg1, arg2):
        global child, relative, nt
        self.boxAdvanced.remove(child)
        self.boxAdvanced.remove(nt)
        relative.pack_start(child, expand=True, fill=True, padding=0)
        self.advanced_graphs_window.hide()
        return True

    def on_cancel_in_saved_button_clicked(self, widget):
        print("Seleção de dispositivo cancelada")
        self.saved_devices_window.hide()

        #Show search_device_window
    
    def on_search_device_activate(self, menuitem, data=None):
        self.combo_box_text_in_search.remove_all()
        self.spinner_in_search.start()
        self.search_device_window.show()

    def on_start_search_button_clicked(self, widget):
        self.battery_label.set_text("Bateria:")
        self.is_connected = False

        self.status_image.set_from_file("bt_red.png")
        self.status_label.set_text("Não conectado")

        print("Buscando novo dispositivo")

        self.devices = connect.searchWBB()

        self.combo_box_text_in_search.remove_all()
        device_ID = 0
        for addr, name in self.devices:
            self.combo_box_text_in_search.append(str(device_ID), 'Nome: ' + name + '\nMAC: ' + addr)
            device_ID += 1

        self.connect_button_in_search.set_sensitive(True)
        self.save_device_in_search.set_sensitive(True)
        self.spinner_in_search.stop()

    def on_connect_button_in_search_clicked(self, widget):
        device_ID = int(self.combo_box_text_in_search.get_active_id())

        self.wiimote, self.battery = connect.connectToWBB(self.devices[device_ID][0])

        if(self.wiimote):
            self.is_connected = True
            self.battery_label.set_text("Bateria: " + str(int(100*self.battery))+"%")
            self.battery_label.set_visible(True)
            self.status_image.set_from_file("bt_green.png")
            self.status_label.set_text("Conectado")
            self.capture_button.set_sensitive(True)
            self.search_device_window.hide()

    def on_save_device_in_search_clicked(self, widget):
        device_ID = int(self.combo_box_text_in_search.get_active_id())

        self.device_name_in_new.set_text(self.devices[device_ID][1])
        self.device_mac_in_new.set_text(self.devices[device_ID][0])
        self.device_mac_in_new.set_sensitive(False)
        self.new_device_window.show()

    def on_cancel_in_search_clicked(self, widget):
        self.connect_button_in_search.set_sensitive(False)
        self.save_device_in_search.set_sensitive(False)
        self.spinner_in_search.stop()
        self.search_device_window.hide()
        self.main_window.get_focus()

    #Show saved devices window
    def on_connect_to_saved_device_activate(self, menuitem, data=None):
        global cur

        self.is_connected = False

        #Fills the combobox with devices names
        self.combo_box_in_saved.remove_all()
        cur.execute("SELECT id, name, is_default FROM devices;")
        rows = cur.fetchall()
        for row in rows:
            self.combo_box_in_saved.append(str(row[0]), row[1])
            if(row[2]):
                self.combo_box_in_saved.set_active_id(str(row[0]))
        self.saved_devices_window.show()

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
        self.battery_label.set_text("Bateria:")
        self.status_image.set_from_file("bt_red.png")
        self.status_label.set_text("Não conectado")

        MAC = self.mac_entry_in_saved.get_text()
        print (MAC)

        self.wiimote, self.battery = connect.connectToWBB(MAC)

        if(self.wiimote):
            self.is_connected = True

            self.battery_label.set_text("Bateria: " + str(int(100*self.battery))+"%")
            self.battery_label.set_visible(True)
            #self.status_bar.push(1, "Conectado")
            self.status_image.set_from_file("bt_green.png")
            self.status_label.set_text("Conectado")
            self.instructions_on_saved_box.set_visible(False)
            self.connect_in_saved_button.set_sensitive(False)
            self.saved_devices_window.hide()
            self.main_window.get_focus()
            self.capture_button.set_sensitive(True)

    def on_cancel_button_in_add_device_clicked(self, widget):
        print("Adição de dispositivo cancelada")
        self.new_device_window.hide()

    def on_device_mac_activate(self, widget):
        print("Dispositivo adicionado")
        self.new_device_window.hide()

    def on_boxOriginal_button_press_event(self, widget, event):
        global child, relative, nt
        if event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS and event.button == 1:
            print("Janela Avançada")

            self.boxOriginal.set_focus_child(self.canvas)
            relative = self.boxOriginal
            child = relative.get_focus_child()
            relative.remove(child)
            self.boxAdvanced.pack_start(child, expand=True, fill=True, padding=0)
            nt = NavigationToolbar(child, self.advanced_graphs_window)
            self.boxAdvanced.pack_start(nt, expand=False, fill=True, padding=0)
            self.advanced_graphs_window.show()

    def on_boxProcessado_button_press_event(self, widget, event):
        global child, relative, nt
        if event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS and event.button == 1:
            print("Janela Avançada")

            self.boxProcessado.set_focus_child(self.canvas2)
            relative = self.boxProcessado
            child = relative.get_focus_child()
            relative.remove(child)
            self.boxAdvanced.pack_start(child, expand=True, fill=True, padding=0)
            nt = NavigationToolbar(child, self.advanced_graphs_window)
            self.boxAdvanced.pack_start(nt, expand=False, fill=True, padding=0)
            self.advanced_graphs_window.show()

    def on_boxFourier_button_press_event(self, widget, event):
        global child, relative, nt
        if event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS and event.button == 1:
            print("Janela Avançada")

            self.boxFourier.set_focus_child(self.canvas3)
            relative = self.boxFourier
            child = relative.get_focus_child()
            relative.remove(child)
            self.boxAdvanced.pack_start(child, expand=True, fill=True, padding=0)
            nt = NavigationToolbar(child, self.advanced_graphs_window)
            self.boxAdvanced.pack_start(nt, expand=False, fill=True, padding=0)
            self.advanced_graphs_window.show()

    def on_cancel_in_standup_clicked(self, widget):
        self.stand_up_window.hide()

    def on_messagedialog1_close_clicked(self, widget):
        self.message_dialog_window.hide()

    def on_savepacient_button_clicked(self, widget):
        global cur, conn

        self.is_pacient = False

        name = self.name_entry.get_text()
        sex = self.sex_combobox.get_active_text()
        age = self.age_entry.get_text()
        height = self.height_entry.get_text()

        if (name == ""):
            self.message_dialog_window.format_secondary_text("Nome inválido, tente novamente.")
            self.message_dialog_window.show()
            self.name_entry.grab_focus()
        elif(sex == ""):
            self.message_dialog_window.format_secondary_text("Sexo inválido, tente novamente.")
            self.message_dialog_window.show()
            self.sex_combobox.grab_focus()
        elif(age == ""):
            self.message_dialog_window.format_secondary_text("Idade inválida, tente novamente.")
            self.message_dialog_window.show()
            self.age_entry.grab_focus()
        elif(height == ""):
            self.message_dialog_window.format_secondary_text("Altura inválida, tente novamente.")
            self.message_dialog_window.show()
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
            if not self.modifying:
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
                self.pacient = {'Nome': name, 'ID': ID, 'Sexo': sex, 'Idade': age, 'Altura': height}
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
                self.pacient['Nome'] = name
                self.pacient['Sexo'] = sex
                self.pacient['Idade'] = age
                self.pacient['Altura'] = height
                #manArq.savePacient(pacient, str(pacient['ID']) + ' - ' + name)
            print("Paciente salvo")
            self.changepacientbutton.set_sensitive(True)
            self.is_pacient = True

    def on_changepacientbutton_clicked(self, widget):
        self.modifying = True
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
        if(not self.is_pacient):
            self.message_dialog_window.format_secondary_text("É preciso cadastrar ou carregar um paciente para realizar o processo de captura.")
            self.message_dialog_window.show()
        elif(not self.is_connected):
            self.message_dialog_window.format_secondary_text("É preciso connectar a um dispositivo para realizar o processo de captura..")
            self.message_dialog_window.show()
        else:
            self.progressbar.set_fraction(0)
            self.stand_up_window.show()

    def on_start_capture_button_clicked(self, widget):
        self.stand_up_window.hide()
        self.axis.clear()
        self.axis.set_ylabel('AP')
        self.axis.set_xlabel('ML')
        self.axis2.clear()
        self.axis2.set_ylabel('AP')
        self.axis2.set_xlabel('ML')
        self.axis3.clear()
        self.axis.set_ylabel('AP')
        self.axis.set_xlabel('ML')

        self.progressbar.set_visible(True)

        global APs, MLs, cur, conn

        balance, weights, pontos = calc.calcPontos(self, self.wiimote, 1)
        midWeight = calc.calcPesoMedio(weights)
        imc = calc.calcIMC(midWeight, float(self.pacient['Altura']))

        self.points_entry.set_text(str(pontos))

        self.pacient['Peso'] = round(midWeight, 2)
        self.pacient['IMC'] = round(imc,1)

        cur.execute("UPDATE pacients SET weight = (%s), imc = (%s) WHERE name = (%s);", (self.pacient['Peso'], self.pacient['IMC'], self.pacient['Nome']))
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
        global APs, MLs, cur, conn, user_ID
        cur.execute("INSERT INTO exams (APs, MLs, pac_id, usr_id) VALUES (%s, %s, %s, %s)", (APs, MLs, self.pacient['ID'], user_ID))
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
        self.wiimote = None
        self.is_pacient = False
        self.is_exam = False
        self.is_connected = False
        self.modifying = False

        self.pacient = {}

        self.calibration_images = ["test_cal_21.png", "test_cal_22.png", "test_cal_23.png", "test_cal_24.png", "test_cal_25.png"]
        self.current_image = 0
        self.calibration_weights = [5, 10]
        #self.calibration_weights = [5, 10, 15, 20]
        self.current_weight = 0

        self.calibration_results_weights = []
        self.calibration_results_coordenates = []

        self.gladeFile = "iem-wbb.glade"
        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.gladeFile)
        self.builder.connect_signals(self)

        #Windows
        self.login_window = self.builder.get_object("login_window")
        self.message_dialog_window = self.builder.get_object("message_dialog_window")
        self.main_window = None
        self.main_window = self.builder.get_object("main_window")
        self.main_window.maximize()
        self.advanced_graphs_window = self.builder.get_object("advanced_graphs_window")

        #Boxes
        self.boxOriginal = self.builder.get_object("boxOriginal")
        self.boxProcessado = self.builder.get_object("boxProcessado")
        self.boxFourier = self.builder.get_object("boxFourier")
        self.boxAdvanced = self.builder.get_object("boxAdvanced")
        
        #Images
        self.status_image = self.builder.get_object("status_image")
        self.image_in_saved = self.builder.get_object("image_in_saved")
        self.calibration_image = self.builder.get_object("calibration_image")

        #Buttons
        self.capture_button = self.builder.get_object("capture_button")
        self.savepacient_button = self.builder.get_object("savepacient_button")
        self.changepacientbutton = self.builder.get_object("changepacientbutton")
        self.save_exam_button = self.builder.get_object("save_exam_button")
        self.load_exam_button = self.builder.get_object("load_exam_button")
        self.start_calibration_button = self.builder.get_object("start_calibration_button")
        self.scale_button = self.builder.get_object("scale_button")
        
        #Entrys
        self.name_entry = self.builder.get_object("name_entry")
        self.age_entry = self.builder.get_object("age_entry")
        self.height_entry = self.builder.get_object("height_entry")
        self.ID_entry = self.builder.get_object("ID_entry")
        self.weight = self.builder.get_object("weight")
        self.imc = self.builder.get_object("imc")
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

        #Combo-Boxes
        self.sex_combobox = self.builder.get_object("sex_combobox")
        self.combo_box_set_exam = self.builder.get_object("combo_box_set_exam")

        #StatusBar
        #self.status_bar = self.builder.get_object("status_bar")

        #Plots
        #Original Graph
        self.fig = plt.figure(dpi=50)
        self.fig.suptitle('Original', fontsize=20)
        self.axis = self.fig.add_subplot(111)
        self.axis.set_ylabel('AP', fontsize = 16)
        self.axis.set_xlabel('ML', fontsize = 16)
        self.canvas = FigureCanvas(self.fig)
        self.boxOriginal.pack_start(self.canvas, expand=True, fill=True, padding=0)

        #Processed Graph
        self.fig2 = Figure(dpi=50)
        self.fig2.suptitle('Processado', fontsize=20)

        self.axis2 = self.fig2.add_subplot(111)
        self.axis2.set_ylabel('AP', fontsize = 16)
        self.axis2.set_xlabel('ML', fontsize = 16)
        self.canvas2 = FigureCanvas(self.fig2)
        self.boxProcessado.pack_start(self.canvas2, expand=True, fill=True, padding=0)

        #Fourier Graph
        self.fig3 = Figure(dpi=50)
        self.fig3.suptitle('Transformada de Fourier', fontsize=20)
        self.axis3 = self.fig3.add_subplot(111)
        self.axis3.set_ylabel('AP', fontsize = 16)
        self.axis3.set_xlabel('ML', fontsize = 16)
        self.canvas3 = FigureCanvas(self.fig3)
        self.boxFourier.pack_start(self.canvas3, expand=True, fill=True, padding=0)
        
        self.advanced_graphs_window.connect("delete-event", self.close_advanced_graphs_window)

        #Boxes
                                
        self.instructions_on_saved_box = self.builder.get_object("instructions_on_saved_box")
        self.graphs_calibration_box = self.builder.get_object("graphs_calibration_box")
        self.calibration_box = self.builder.get_object("calibration_box")
        self.vbox1 = self.builder.get_object("vbox1")


        #Windows
        self.new_device_window = self.builder.get_object("new_device_window")
        self.stand_up_window = self.builder.get_object("stand_up_window")
        self.search_device_window = self.builder.get_object("search_device_window")
        self.saved_devices_window = self.builder.get_object("saved_devices_window")
        
        self.load_pacient_window = self.builder.get_object("load_pacient_window")
        self.calibration_window = self.builder.get_object("calibration_window")
        self.calibration_equipment_window = self.builder.get_object("calibration_equipment_window")

        #Delete-events
        #self.register_window.connect("delete-event", self.close_register_window)
        self.search_device_window.connect("delete-event", self.close_search_device_window)
        self.new_device_window.connect("delete-event", self.close_new_device_window)
        self.stand_up_window.connect("delete-event", self.close_stand_up_window)
        self.saved_devices_window.connect("delete-event", self.close_saved_devices_window)
        self.load_pacient_window.connect("delete-event", self.close_load_pacient_window)

        #Buttons
        self.start_capture_button = self.builder.get_object("start_capture_button")
        self.save_device_in_search = self.builder.get_object("save_device_in_search")
        self.connect_button_in_search = self.builder.get_object("connect_button_in_search")
        self.connect_in_saved_button = self.builder.get_object("connect_in_saved_button")
        self.add_as_default_button_in_add_device = self.builder.get_object("add_as_default_button_in_add_device")
                                
        self.start_calibration_button = self.builder.get_object("start_calibration_button")

        #Spinners
        self.spinner_in_search = self.builder.get_object("spinner_in_search")

        #Labels
        self.pacient_label_in_load = self.builder.get_object("pacient_label_in_load")
        self.calibration_label = self.builder.get_object("calibration_label")

        #Grids
        self.grid_resultados = self.builder.get_object("grid_resultados")
        
        #Entrys
        self.username_entry_in_login = self.builder.get_object("username_entry_in_login")
        self.password_entry_in_login = self.builder.get_object("password_entry_in_login")
        self.password_entry_in_login.set_activates_default(True)
                                
        self.device_name_in_new = self.builder.get_object("device_name_in_new")
        self.device_mac_in_new = self.builder.get_object("device_mac_in_new")
        self.mac_entry_in_saved = self.builder.get_object("mac_entry_in_saved")

        #Combo-boxes
        self.combo_box_in_saved = self.builder.get_object("combo_box_in_saved")
        self.combo_box_text_in_search = self.builder.get_object("combo_box_text_in_search")
        self.combobox_in_load_pacient = self.builder.get_object("combobox_in_load_pacient")

        #Separators
        self.separator_results = self.builder.get_object("separator_results")


        #Calibration Graph
        self.fig4 = Figure(dpi=50)
        self.fig4.suptitle('Calibração', fontsize=20)
        self.axis4 = self.fig4.add_subplot(111)
        self.axis4.set_ylabel('Y', fontsize = 16)
        self.axis4.set_xlabel('X', fontsize = 16)
        self.axis4.set_xlim(-2.25, 2.25)
        self.axis4.set_ylim(-2.65, 2.65)
        self.axis4.axhline(0, color='grey')
        self.axis4.axvline(0, color='grey')
        self.canvas4 = FigureCanvas(self.fig4)
        self.graphs_calibration_box.pack_start(self.canvas4, expand=True, fill=True, padding=0)

        #StatusBar
        self.status_bar = Gtk.Box(spacing=10)
        self.status_image_box = Gtk.Box(spacing=5)
        self.status_image = Gtk.Image.new_from_file("bt_red.png")
        self.status_label = Gtk.Label.new("Não conectado")
        self.battery_label = Gtk.Label.new("Bateria: ")
        self.progressbar = Gtk.ProgressBar.new()
        self.progressbar.set_show_text(True)

        self.status_image_box.pack_start(self.status_image, expand=False, fill=True, padding=0)
        self.status_image_box.pack_start(self.status_label, expand=False, fill=True, padding=0)
        self.status_bar.pack_start(self.status_image_box, expand=True, fill=True, padding=0)
        self.status_bar.pack_start(self.battery_label, expand=True, fill=True, padding=0)
        self.status_bar.pack_start(self.progressbar, expand=True, fill=True, padding=0)
        self.calibration_box.pack_end(self.status_bar, expand=True, fill=True, padding=0)
        #self.vbox1.pack_end(self.status_bar, expand=True, fill=True, padding=0)


        #self.login_window.show_all()
        #self.main_window.show_all()
        self.calibration_window.show_all()
        self.battery_label.set_visible(False)
        self.progressbar.set_visible(False)
        #self.calibration_equipment_window.show_all()

if __name__ == "__main__":
    global conn, cur

    #Connecting to DB
    conn = psycopg2.connect("dbname=iem_wbb host=localhost user=postgres password=postgres")
    #Opening DB cursor
    cur = conn.cursor()

    main = Iem_wbb()
    Gtk.main()
