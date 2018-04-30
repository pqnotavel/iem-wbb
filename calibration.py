#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('src')
sys.path.append('media')

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Pango, GLib

from matplotlib.figure import Figure
from matplotlib import pyplot as plt
from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas

from bluetooth.btcommon import is_valid_address as iva

import psycopg2
import wbb_calitera as wbb

class Calibration:
    
    #Evento de seleção do método de calibração por pontos
    def on_bypoints_calibration_button_clicked(self, widget):
        #Esconde a janela do assistente
        self.calibration_assistant.hide()
        #Seta a imagem das instruções
        self.equipment_image.set_from_file('./media/calibracao_ponto.png')
        #Mostra a janela de instruções
        self.calibration_equipment_window.show()

    #Evento de seleção do método de calibração por sensores
    def on_bysensor_calibration_button_clicked(self, widget):
        #Esconde a janela do assistente
        self.calibration_assistant.hide()
        #Seta a imagem das instruções
        self.equipment_image.set_from_file('./media/calibracao_sensor.png')
        #Mostra a janela de instruções
        self.calibration_equipment_window.show()
        #Muda a variável de valor
        self.calibration_by_points = False

    #Evento de seleção de novo teste de calibração por pontos
    def on_new_calibration_activate(self, menuitem, data=None):
        #Redefine a imagem de calibração
        self.calibration_by_points_image.set_from_file('./media/test_pontos.png')
        #Limpa a label de instruções
        self.calibration_label.set_text("")
        #Redefine a variável de teste
        self.calibration_test = 0
        #Zera a barra de progresso
        self.progressbar.set_fraction(0)

        self.calibration_button = Gtk.Button("Iniciar")
        self.calibration_button.connect('clicked', self.on_calibration_button_clicked)
        #Muda a sensibilidade do bot~ao de inicio
        self.calibration_button.set_sensitive(True)

    def on_save_calibration_activate(self, menuitem, data=None):
        calibrations = ('\'{' + str(self.calibrations['right_top']) + 
                ',' + str(self.calibrations['right_bottom']) + 
                ',' + str(self.calibrations['left_top']) + 
                ',' + str(self.calibrations['left_bottom'])+ '}\'')

        calibrations = calibrations.replace('[', '{', 4).replace(']', '}', 4)
        mac = '\'' + str(self.WBB['MAC']) + '\''

        self.cur.execute("UPDATE devices SET calibrations = %s WHERE mac = %s" % (calibrations, mac))
        self.conn.commit()

    #Evento de continuar para a calibração
    def on_continue_button_clicked(self, widget):
        self.calibration_equipment_window.hide()
        if(self.calibration_by_points):
            calibration_menu_bar = Gtk.MenuBar()
            arquivo = Gtk.MenuItem("_Arquivo", True)
            conexao = Gtk.MenuItem("_Conexão", True)
            
            arquivo_menu = Gtk.Menu()
            conexao_menu = Gtk.Menu()

            nova_cal = Gtk.MenuItem("Novo", True)
            nova_cal.connect('activate', self.on_new_calibration_activate)
            self.salvar_cal = Gtk.MenuItem("Salvar")
            self.salvar_cal.connect('activate', self.on_save_calibration_activate)
            self.salvar_cal.set_sensitive(False)
            sair = Gtk.MenuItem("Sair")
            sair.connect('activate', Gtk.main_quit)
            sep = Gtk.SeparatorMenuItem()

            novo_wbb = Gtk.MenuItem("Adicionar novo dispositivo")
            novo_wbb.connect('activate', self.on_new_device_activate)
            busca = Gtk.MenuItem("Buscar dispositivo bluetooth")
            busca.connect('activate', self.on_search_device_activate)
            salvo = Gtk.MenuItem("Conectar a um dispositivo salvo")
            salvo.connect('activate', self.on_connect_to_saved_device_activate)
            desconectar = Gtk.MenuItem("Desconectar")
            desconectar.connect('activate', self.on_disconnect_activate)
            sep1 = Gtk.SeparatorMenuItem()

            arquivo_menu.append(nova_cal)
            arquivo_menu.append(self.salvar_cal)
            arquivo_menu.append(sep)
            arquivo_menu.append(sair)

            conexao_menu.append(novo_wbb)
            conexao_menu.append(busca)
            conexao_menu.append(salvo)
            conexao_menu.append(sep1)
            conexao_menu.append(desconectar)
            
            arquivo.set_submenu(arquivo_menu)
            conexao.set_submenu(conexao_menu)

            calibration_menu_bar.append(arquivo)
            calibration_menu_bar.append(conexao)
            
            separator = Gtk.HSeparator()
            separator1 = Gtk.HSeparator()
            
            self.calibration_button = Gtk.Button("Iniciar")
            self.calibration_button.connect('clicked', self.on_calibration_button_clicked)
            
            button_box = Gtk.ButtonBox()
            button_box.set_layout(Gtk.ButtonBoxStyle.EXPAND)
            button_box.pack_start(self.calibration_button, True, True, 0)
            
            self.box_assistant_images.remove(self.calibration_by_points_image)
            self.calibration_label = Gtk.Label("Calibração")
            self.box_calibration_by_points = Gtk.VBox()
            self.box_calibration_by_points.set_spacing(10)
            
            for x in [calibration_menu_bar, self.calibration_by_points_image, separator, 
                        self.calibration_label, separator1, button_box, self.status_bar]:
            
                self.box_calibration_by_points.pack_start(x, False, False, 0)

            self.calibration_by_points_window = Gtk.Window()
            self.calibration_by_points_window.set_title("Calibração por Pontos")
            self.calibration_by_points_window.add(self.box_calibration_by_points)
            self.calibration_by_points_window.connect('destroy', Gtk.main_quit)
            self.calibration_by_points_window.set_gravity(Gdk.Gravity.STATIC)
            self.calibration_by_points_window.set_position(Gtk.WindowPosition.CENTER)
            self.calibration_by_points_window.set_resizable(False)
            self.calibration_by_points_window.show_all()
        else:
            Gtk.main_quit()

    def on_calibration_button_clicked(self, widget):
        if(not self.is_connected):
            self.message_dialog_window.set_transient_for(self.calibration_by_points_window)
            self.message_dialog_window.format_secondary_text("É preciso conectar a um dispositivo para realizar o processo de captura.")
            self.message_dialog_window.show()
        else:
            self.calibration_test = 0
            self.calibration_by_points_image.set_sensitive(True)
            self.calibration_button.set_label("Medir")
            self.calibration_button.connect('clicked', self.on_start_calibration_clicked)
            text = "Posicione a plataforma sem nenhum peso"
            self.calibration_label.set_text(text)
            self.progressbar.set_visible(True)
            self.salvar_cal.set_sensitive(False)

    def destroy_event(self, widget):
        widget.hide()
        return True

    def on_start_calibration_clicked(self, widget):
        if(self.calibration_test == 0):
            self.calibration_button.set_sensitive(False)
            self.calibrations = wbb.calibra_minimos(self.wiimote, self.progressbar, wbb.escala_eu)
            self.calibration_button.set_sensitive(True)
            text = "Posicione o peso de 10kg no ponto RT"
            self.calibration_label.set_text(text)
            self.calibration_by_points_image.set_from_file('./media/'+self.calibration_by_points_images[self.current_image])
            self.calibration_test = (self.calibration_test + 1) % 3
        elif(self.calibration_test == 1):
            if(self.current_image == 0):
                self.calibration_button.set_sensitive(False)
                self.sinal_RT = wbb.captura(self.wiimote, self.progressbar)
                self.calibration_button.set_sensitive(True)
                text = "Posicione o peso de 10kg no ponto RB"
                self.calibration_label.set_text(text)
            elif(self.current_image == 1):
                self.calibration_button.set_sensitive(False)
                self.sinal_RB = wbb.captura(self.wiimote, self.progressbar)
                self.calibration_button.set_sensitive(True)
                text = "Posicione o peso de 10kg no ponto LT"
                self.calibration_label.set_text(text)
            elif(self.current_image == 2):
                self.calibration_button.set_sensitive(False)
                self.sinal_LT = wbb.captura(self.wiimote, self.progressbar)
                self.calibration_button.set_sensitive(True)
                text = "Posicione o peso de 10kg no ponto LB"
                self.calibration_label.set_text(text)
            else:
                self.calibration_button.set_sensitive(False)
                self.sinal_LB = wbb.captura(self.wiimote, self.progressbar)
                self.calibrations = wbb.calibra_medios(self.wiimote, self.calibrations, self.sinal_RT, self.sinal_RB, self.sinal_LT, self.sinal_LB, wbb.escala_eu)
                self.calibration_button.set_sensitive(True)
                text = "Posicione o peso de 30kg no ponto RT"
                self.calibration_label.set_text(text)
                self.calibration_test = (self.calibration_test + 1) % 3

            self.current_image = (self.current_image + 1) % len(self.calibration_by_points_images)
            self.calibration_by_points_image.set_from_file('./media/'+self.calibration_by_points_images[self.current_image])
        else:
            if(self.current_image == 0):
                self.calibration_button.set_sensitive(False)
                self.sinal_RT = wbb.captura(self.wiimote, self.progressbar)
                self.calibration_button.set_sensitive(True)
                text = "Posicione o peso de 30kg no ponto RB"
                self.calibration_label.set_text(text)
            elif(self.current_image == 1):
                self.calibration_button.set_sensitive(False)
                self.sinal_RB = wbb.captura(self.wiimote, self.progressbar)
                self.calibration_button.set_sensitive(True)
                text = "Posicione o peso de 30kg no ponto LT"
                self.calibration_label.set_text(text)
            elif(self.current_image == 2):
                self.calibration_button.set_sensitive(False)
                self.sinal_LT = wbb.captura(self.wiimote, self.progressbar)
                self.calibration_button.set_sensitive(True)
                text = "Posicione o peso de 30kg no ponto LB"
                self.calibration_label.set_text(text)
            else:
                self.calibration_button.set_sensitive(False)
                self.sinal_LB = wbb.captura(self.wiimote, self.progressbar)
                self.calibrations = wbb.calibra_maximos(self.wiimote, self.calibrations, self.sinal_RT, self.sinal_RB, self.sinal_LT, self.sinal_LB, wbb.escala_eu)
                self.calibration_label.set_text('Fim da Calibração')
                self.calibration_by_points_image.set_from_file('./media/test_pontos.png')
                self.calibration_by_points_image.set_sensitive(False)
                self.salvar_cal.set_sensitive(True)
                return

            self.current_image = (self.current_image + 1) % len(self.calibration_by_points_images)
            self.calibration_by_points_image.set_from_file('./media/'+self.calibration_by_points_images[self.current_image])
    
        return

    def on_calibration_by_points_window_destroy(self, object, data=None):
        print("Quit in calibration_by_points_window from menu")
        self.cur.close()
        self.conn.close()
        Gtk.main_quit()

    def on_calibration_by_sensors_window_destroy(self, object, data=None):
        print("Quit in calibration_by_sensors_window from menu")
        self.cur.close()
        self.conn.close()
        Gtk.main_quit()

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
            self.WBB = {'Nome':name, 'MAC':mac, 'Padrao' : is_default}
            if(is_default):
                self.cur.execute("SELECT * FROM devices_id_seq;")
                row = self.cur.fetchall()
                ID = row[0][1]
                self.cur.execute("UPDATE devices SET is_default = FALSE;")
            self.cur.execute("INSERT INTO devices (name, mac, is_default) VALUES (%s, %s, %s);", (name, mac, is_default))
            self.conn.commit()
            self.device_name_in_new.set_text("")
            self.device_mac_in_new.set_text("")
            self.new_device_window.hide()

    #Disconnet self.wiimote
    def on_disconnect_activate(self, menuitem, data=None):
        if(self.wiimote):
            connect.closeConnection(self.wiimote)
            self.is_connected = False
            self.battery_label.set_text("Bateria:")
            #self.battery_label.set_visible(False)
            self.status_image.set_from_file("./media/bt_red.png")
            self.status_label.set_text("Não conectado")

    def on_cancel_in_saved_button_clicked(self, widget):
        print("Seleção de dispositivo cancelada")
        self.saved_devices_window.hide()
    
    def on_search_device_activate(self, menuitem, data=None):
        self.combo_box_in_search.remove_all()
        self.spinner_in_search.start()
        self.search_device_window.show()

    def on_start_search_button_clicked(self, widget):
        self.status_image.set_from_file("./media/bt_red.png")
        self.status_label.set_text("Não conectado")

        print("Buscando novo dispositivo")

        self.devices = wbb.search()

        self.combo_box_in_search.remove_all()
        device_ID = 0
        for addr, name in self.devices:
            self.combo_box_in_search.append(str(device_ID), 'Nome: ' + name + '\nMAC: ' + addr)
            device_ID += 1

        self.connect_button_in_search.set_sensitive(True)
        self.save_device_in_search.set_sensitive(True)
        self.spinner_in_search.stop()

    def on_connect_button_in_search_clicked(self, widget):
        self.battery_label.set_text("Bateria:")
        self.is_connected = False

        device_ID = int(self.combo_box_in_search.get_active_id())

        self.wiimote, self.battery = wbb.conecta(self.devices[device_ID][0])

        if(self.wiimote):
            self.is_connected = True
            self.battery_label.set_text("Bateria: " + str(int(100*self.battery))+"%")
            self.battery_label.set_visible(True)
            self.status_image.set_from_file("./media/bt_green.png")
            self.status_label.set_text("Conectado")
            self.capture_button.set_sensitive(True)
            self.search_device_window.hide()

            #Gdk.threads_add_timeout(GLib.PRIORITY_HIGH_IDLE, 1, self.verify_bt)
            GLib.timeout_add_seconds(1, self.verify_bt)

        else:
            self.message_dialog_window.set_transient_for(self.search_device_window)
            self.message_dialog_window.format_secondary_text("Não foi possível conectar-se à plataforma, tente novamente.")
            self.message_dialog_window.show()

    def on_save_device_in_search_clicked(self, widget):
        device_ID = int(self.combo_box_in_search.get_active_id())

        self.device_name_in_new.set_text(self.devices[device_ID][1])
        self.device_mac_in_new.set_text(self.devices[device_ID][0])
        self.device_mac_in_new.set_sensitive(False)
        self.new_device_window.show()

    def on_cancel_in_search_clicked(self, widget):
        self.connect_button_in_search.set_sensitive(False)
        self.save_device_in_search.set_sensitive(False)
        self.spinner_in_search.stop()
        self.search_device_window.hide()

    #Show saved devices window
    def on_connect_to_saved_device_activate(self, menuitem, data=None):

        self.is_connected = False

        #Fills the combobox with devices names
        self.combo_box_in_saved.remove_all()
        self.cur.execute("SELECT id, name, is_default FROM devices;")
        rows = self.cur.fetchall()
        for row in rows:
            self.combo_box_in_saved.append(str(row[0]), row[1])
            if(row[2]):
                self.combo_box_in_saved.set_active_id(str(row[0]))
        self.saved_devices_window.show()

    #Saved devices selection
    def on_combo_box_in_saved_changed(self, widget):

        #Gets the active row ID at pacients_combobox
        ID = self.combo_box_in_saved.get_active_id()
        ID = str(ID)

        if(ID != "None"):
            #Selects the active row from table devices
            self.cur.execute("SELECT mac FROM devices WHERE id = (%s);", (ID))
            row = self.cur.fetchall()

            self.mac_entry_in_saved.set_text(row[0][0])
            self.connect_in_saved_button.set_sensitive(True)
            self.instructions_on_saved_box.set_visible(True)

    def on_connect_in_saved_button_clicked(self, widget):
        self.battery_label.set_text("Bateria:")
        self.status_image.set_from_file("./media/bt_red.png")
        self.status_label.set_text("Não conectado")

        MAC = self.mac_entry_in_saved.get_text()

        self.wiimote, self.battery = wbb.conecta(MAC)

        if(self.wiimote):

            self.cur.execute("SELECT name, calibrations, is_default FROM devices WHERE mac = \'%s\';" % (str(MAC)))
            rows = self.cur.fetchall()
            row_calibration = rows[0][1]

            calibration = { 'right_top':    row_calibration[0],
                            'right_bottom': row_calibration[1],
                            'left_top':     row_calibration[2],
                            'left_bottom':  row_calibration[3] }

            self.WBB = {'Nome': rows[0][0], 'MAC': MAC, 'Calibração': calibration, 'Padrão': rows[0][2]}

            self.is_connected = True
            self.battery_label.set_text("Bateria: " + str(int(100*self.battery))+"%")
            self.battery_label.set_visible(True)
            self.status_image.set_from_file("./media/bt_green.png")
            self.status_label.set_text("Conectado")
            self.instructions_on_saved_box.set_visible(False)
            self.connect_in_saved_button.set_sensitive(False)
            self.saved_devices_window.hide()
            self.capture_button.set_sensitive(True)

            GLib.timeout_add_seconds(1, self.verify_bt)
            #Gdk.threads_add_timeout(GLib.PRIORITY_HIGH_IDLE, 1, self.verify_bt)

        else:
            self.message_dialog_window.set_transient_for(self.saved_devices_window)
            self.message_dialog_window.format_secondary_text("Não foi possível conectar-se à plataforma, tente novamente.")
            self.message_dialog_window.show()

    def on_cancel_button_in_add_device_clicked(self, widget):
        print("Adição de dispositivo cancelada")
        self.new_device_window.hide()

    def on_device_mac_activate(self, widget):
        print("Dispositivo adicionado")
        self.new_device_window.hide()

    def on_messagedialog_button_cancel_clicked(self, widget):
        self.message_dialog_window.hide()

    def verify_bt(self):
        if(self.wiimote):
            try:
                self.wiimote.request_status()
            except RuntimeError:
                self.is_connected = False
                self.battery_label.set_text("Bateria:")
                self.status_image.set_from_file("./media/bt_red.png")
                self.status_label.set_text("Não conectado")
                self.message_dialog_window.set_transient_for(self.main_window)
                self.message_dialog_window.format_secondary_text("Perda de conexão, tente novamente.")
                self.message_dialog_window.show()
                return False
        else:
            return False

        return True

    def main_window_delete_event(self, widget, arg2):
        widget.hide()
        return True

    def __init__(self):

        #Connecting to DB
        self.conn = psycopg2.connect("dbname=iem_wbb host=localhost user=postgres password=postgres")
        #Opening DB cursor
        self.cur = self.conn.cursor()

        self.APs = []
        self.MLs = []
        self.WBB = {}

        self.battery = None
        self.wiimote = None
        self.is_connected = False
        self.calibration_by_points = True

        self.calibrations = {}
        self.calibration_test = 0
        self.sensores = ['RT', 'RB', 'LT', 'LB']
        self.current_sensor = 0
        self.calibration_by_points_images = ["test_pontos_rt.png", "test_pontos_rb.png", "test_pontos_lt.png", "test_pontos_lb.png"]
        self.current_image = 0
        self.calibration_weights = [10, 30]
        self.current_weight = 0

        #Builders
        self.calibrationGladeFile = "./src/calibration.glade"
        self.builder_calibration = Gtk.Builder()
        self.builder_calibration.add_from_file(self.calibrationGladeFile)
        self.builder_calibration.connect_signals(self)
        
        self.commonGladeFile = "./src/common.glade"
        self.commonBuilder = Gtk.Builder()
        self.commonBuilder.add_from_file(self.commonGladeFile)
        self.commonBuilder.connect_signals(self)

        #Windows
        self.message_dialog_window = self.commonBuilder.get_object("message_dialog_window")
        self.new_device_window = self.commonBuilder.get_object("new_device_window")
        self.search_device_window = self.commonBuilder.get_object("search_device_window")
        self.saved_devices_window = self.commonBuilder.get_object("saved_devices_window")
        self.calibration_by_sensors_window = self.builder_calibration.get_object("calibration_by_sensors_window")
        self.calibration_equipment_window = self.builder_calibration.get_object("calibration_equipment_window")
        self.calibration_assistant = self.builder_calibration.get_object("calibration_assistant")

        #Boxes
        self.boxAdvanced = self.commonBuilder.get_object("boxAdvanced")
        self.instructions_on_saved_box = self.commonBuilder.get_object("instructions_on_saved_box")
        self.graphs_calibration_by_points_box = self.builder_calibration.get_object("graphs_calibration_by_points_box")
        self.box_assistant_images = self.builder_calibration.get_object("box_assistant_images")
        
        #Images
        self.image_in_saved = self.commonBuilder.get_object("image_in_saved")
        self.image_in_saved.set_from_file('./media/syncButton.png')
        self.search_image = self.commonBuilder.get_object("search_image")
        self.search_image.set_from_file('./media/syncButton.png')
        self.calibration_by_points_image = self.builder_calibration.get_object("calibration_by_points_image")
        self.calibration_by_points_image.set_from_file('./media/test_pontos.png')
        self.calibration_by_sensors_image = self.builder_calibration.get_object("calibration_by_sensors_image")
        self.calibration_by_sensors_image.set_from_file('./media/test_sensores.png')
        self.equipment_image = self.builder_calibration.get_object("equipment_image")

        #Buttons
        self.save_device_in_search = self.commonBuilder.get_object("save_device_in_search")
        self.connect_button_in_search = self.commonBuilder.get_object("connect_button_in_search")
        self.connect_in_saved_button = self.commonBuilder.get_object("connect_in_saved_button")
        self.add_as_default_button_in_add_device = self.commonBuilder.get_object("add_as_default_button_in_add_device")                   
        
        #Combo-Boxes
        self.combo_box_in_saved = self.commonBuilder.get_object("combo_box_in_saved")
        self.combo_box_in_search = self.commonBuilder.get_object("combo_box_in_search")

        #Delete-events
        self.search_device_window.connect("delete-event", self.main_window_delete_event)
        self.new_device_window.connect("delete-event", self.main_window_delete_event)
        self.calibration_assistant.connect('delete-event', Gtk.main_quit)
        self.calibration_equipment_window.connect('delete-event', Gtk.main_quit)
        
        #Entrys
        self.device_name_in_new = self.commonBuilder.get_object("device_name_in_new")
        self.device_mac_in_new = self.commonBuilder.get_object("device_mac_in_new")
        self.mac_entry_in_saved = self.commonBuilder.get_object("mac_entry_in_saved")

        #Plots
        #Calibration Graph
        self.fig4 = Figure(dpi=50)
        self.fig4.suptitle('Calibração', fontsize=20)
        self.axis4 = self.fig4.add_subplot(111)
        self.axis4.set_ylabel('Y', fontsize = 16)
        self.axis4.set_xlabel('X', fontsize = 16)
        self.axis4.set_xlim(-433/2, 433/2)
        self.axis4.set_ylim(-238/2, 238/2)
        self.axis4.axhline(0, color='grey')
        self.axis4.axvline(0, color='grey')
        self.canvas4 = FigureCanvas(self.fig4)
        #self.graphs_calibration_by_points_box.pack_start(self.canvas4, expand=True, fill=True, padding=0)

        #StatusBar
        self.status_bar = Gtk.Box(spacing=20)
        status_sep1 = Gtk.VSeparator()
        status_sep2 = Gtk.VSeparator()
        self.status_image_box = Gtk.Box(spacing=5)
        self.status_image = Gtk.Image()
        self.status_image.set_from_file('./media/bt_red.png')
        self.status_label = Gtk.Label.new("Não conectado")
        self.battery_label = Gtk.Label.new("Bateria: ")
        self.progressbar = Gtk.ProgressBar.new()
        self.progressbar.set_show_text(True)

        self.status_image_box.pack_start(self.status_image, expand=False, fill=True, padding=0)
        self.status_image_box.pack_start(self.status_label, expand=False, fill=True, padding=0)
        self.status_bar.pack_start(self.status_image_box, expand=True, fill=True, padding=0)
        self.status_bar.pack_start(status_sep1, expand=True, fill=True, padding=0)
        self.status_bar.pack_start(self.battery_label, expand=True, fill=True, padding=0)
        self.status_bar.pack_start(status_sep2, expand=True, fill=True, padding=0)
        self.status_bar.pack_start(self.progressbar, expand=True, fill=True, padding=0)
        
        #Spinners
        self.spinner_in_search = self.commonBuilder.get_object("spinner_in_search")

        ''' Calibração '''
        self.calibration_assistant.show_all()

if __name__ == "__main__":

    main = Calibration()
    Gtk.main()
