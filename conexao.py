import cwiid
import os
import time as ptime
import calculos as calc

'''def openConection(MAC):
    print("Please press the red 'connect' button on the balance board, inside the battery compartment.")
    print("Do not step on the balance board.")

    global wiimote

    wiimote = cwiid.Wiimote(MAC)

    wiimote.rpt_mode = cwiid.RPT_BALANCE | cwiid.RPT_BTN
    wiimote.request_status()

    while (wiimote.state['ext_type'] != cwiid.EXT_BALANCE):
        # if wiimote.state['ext_type'] != cwiid.EXT_BALANCE:
        print('This program only supports the Wii Balance Board')
        print("Please press the red 'connect' button on the balance board, inside the battery compartment.")
        print("Do not step on the balance board.")
        wiimote.close()
        wiimote = cwiid.Wiimote("00:27:09:AC:29:22")
        wiimote.rpt_mode = cwiid.RPT_BALANCE | cwiid.RPT_BTN
        wiimote.request_status()

    balance_calibration = wiimote.get_balance_cal()
    named_calibration = {'right_top': balance_calibration[0],
                         'right_bottom': balance_calibration[1],
                         'left_top': balance_calibration[2],
                         'left_bottom': balance_calibration[3],
                         }

'''

def readWBB():
    print("Please press the red 'connect' button on the balance board, inside the battery compartment.")
    print("Do not step on the balance board.")

    global wiimote

    wiimote = cwiid.Wiimote("00:27:09:AC:29:22")

    wiimote.rpt_mode = cwiid.RPT_BALANCE | cwiid.RPT_BTN
    wiimote.request_status()

    while (wiimote.state['ext_type'] != cwiid.EXT_BALANCE):
        # if wiimote.state['ext_type'] != cwiid.EXT_BALANCE:
        print('This program only supports the Wii Balance Board')
        print("Please press the red 'connect' button on the balance board, inside the battery compartment.")
        print("Do not step on the balance board.")
        wiimote.close()
        wiimote = cwiid.Wiimote("00:27:09:AC:29:22")
        wiimote.rpt_mode = cwiid.RPT_BALANCE | cwiid.RPT_BTN
        wiimote.request_status()

    balance_calibration = wiimote.get_balance_cal()
    named_calibration = { 'right_top': balance_calibration[0],
                             'right_bottom': balance_calibration[1],
                             'left_top': balance_calibration[2],
                             'left_bottom': balance_calibration[3],
                             }
    # balance_lst = []
    balance_dif = []
    balanca = []
    x_ref = 0.0
    y_ref = 0.0


    duration = 1  # second
    freq = 440  # Hz
    os.system('play --no-show-progress --null --channels 1 synth %s sine %f' % (duration, freq))
    print("Preperados!!!!!")
    ptime.sleep(10)
    print("Já!!!!!!!!!!")
    os.system('play --no-show-progress --null --channels 1 synth %s sine %f' % (duration, freq))
    start = ptime.time()
    # dt = 0.03125
    dt = 0.040
    # dt = 0.032
    i = 0
    amostra = 768
    t1 = ptime.time() + dt
    while (i < amostra):
        wiimote.request_status()
        readings = wiimote.state['balance']
        try:
            r_rt = calc.gsc(readings ,'right_top', named_calibration)
            r_rb = calc.gsc(readings ,'right_bottom', named_calibration)
            r_lt = calc.gsc(readings ,'left_top', named_calibration)
            r_lb = calc.gsc(readings ,'left_bottom', named_calibration)
        except:
            x_balance = 1.
            y_balance = 1.

        x_balance = (float(r_rt + r_rb)) / (float(r_lt + r_lb))
        if x_balance > 1:
            x_balance = (((float(r_lt + r_lb)) / (float(r_rt + r_rb)) ) *-1.) +1.
        else:
            x_balance = x_balance -1.

        y_balance = (float(r_lb + r_rb)) / (float(r_lt + r_rt))
        if y_balance > 1:
            y_balance = (((float(r_lt + r_rt)) / (float(r_lb + r_rb))) * -1.) + 1.
        else:
            y_balance = y_balance - 1

        # balance_lst.append((x_balance,y_balance))
        i += 1
        if (i == amostra-1):
            weight = calc.calcweight(readings, named_calibration)

        if (x_ref != x_balance or y_ref != y_balance):
            balance_dif.append((x_balance, y_balance))
            x_ref = x_balance
            y_ref = y_balance

        # ptime.sleep(0.005)
        while (ptime.time() < t1):
            pass
        # t1 = ptime.time() + .02
        t1 += dt

    stop = ptime.time()
    os.system('play --no-show-progress --null --channels 1 synth %s sine %f' % (duration, freq))
    print("dt = ", stop - start)
    print("Balance")
    print(len(balanca))

    print(weight,' Kg')
    # print(len(balance_lst))
    #wiimote.close()
    #print(wiimote.__getattribute__())
    print(wiimote.request_status())

    return balance_dif

def closeConection():
    wiimote.close()