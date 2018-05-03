# -*- coding: utf-8 -*-


import cwiid
import bluetooth

def verifyConnection():
    pass

def searchWBB():

    print ("Start discovering....")
    nearby_devices = bluetooth.discover_devices(duration=1, lookup_names = True)

    return nearby_devices


def connectToWBB(MAC):
    wiimote = cwiid.Wiimote(MAC)
    wiimote.rpt_mode = cwiid.RPT_BALANCE | cwiid.RPT_BTN
    wiimote.request_status()

    i=1;
    while (wiimote.state['ext_type'] != cwiid.EXT_BALANCE):
        try:
            wiimote = cwiid.Wiimote(MAC)
            wiimote.rpt_mode = cwiid.RPT_BALANCE | cwiid.RPT_BTN
            wiimote.request_status()
        except RuntimeError:
            if (i>10):
                return None, None
            print ("Error opening wiimote connection")
            print ("attempt " + str(i))
            i +=1

    battery = wiimote.state['battery']/cwiid.BATTERY_MAX

    return wiimote, battery

def closeConnection(wiimote):
    wiimote.close()
