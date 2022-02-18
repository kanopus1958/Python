#!/usr/bin/env python3

# Programm     : robot-control.py
# Version      : 1.00
# SW-Stand     : 17.02.2022
# Autor        : Kanopus1958
# Beschreibung : Steuerung eines Roboter-Autos mit Tastatureingaben

import os
import sys
import platform
from pathlib import Path
from rwm_steuerung import color as c, key_stroke as k
from rwm_mod01 import clean_console, show_header, aktuelle_uhrzeit, getkey
import logging
import threading
import subprocess
import queue
import datetime
from time import sleep
from random import randint

G_OS = ('Raspbian', 'Debian')
G_HEADER_1 = '# Steuerung Roboter-Auto mit T'
G_HEADER_2 = 'astatureingaben              #'

# ----------------------------------------------------------------------------
# Globale Konstanten GC_<name> für alle Funktionen und Theads
GC_log_ein = True               # Schalter für Logging Ein=True / Aus=False
GC_log_detail = False           # Schalter Detail-Logging Ein=True/Aus=False
GC_speed_min = -1.0             # Minimale Speed der Motoren (rückwärts)
GC_speed_max = +1.0             # Maximale Speed der Motoren (vorwärts)
GC_speed_zero = 0.0             # Geschwindigkeit für Motoren AUS
GC_mod_man = 'manuell'          # Modus manuelles Fahren
GC_mod_auto = 'autonom'         # Modus autonomes Fahren
# Globale Variablen GV_<name> für alle Funktionen und Theads
GV_th_list = list()             # Identifier für die gestarteten Threads
GV_speedleft = 0.0              # Geschwindigkeit Linke Motoren
GV_speedright = 0.0             # Geschwindigkeit Rechte Motoren
GV_modus = GC_mod_man           # Aktueller Fahrmodus
GV_entfernung = 0               # Aktuelle Entfernung zum Hindernis vorne
GV_anz_funk = 'START'           # Anzeige der aktuellen Funktion der Motoren
# ----------------------------------------------------------------------------


# Testmode einschalten mit Aufrufparameter 'test'
# Im Testmodus wird der Motortreiber L298NHBridgePCA9685 nicht geladen
testmode = False
if len(sys.argv) == 2:
    if sys.argv[1] == 'test':
        testmode = True
# Solange im Testmode, bis HW angeschlossen ist
testmode = True

# Das Programm L298NHBridgePCA9685 wird als Modul geladen. Es stellt
# die Funktionen fuer die Steuerung der H-Bruecke ueber einen PCA9685
# Servo Kontroller zur Verfuegung.
if not testmode:
    import L298NHBridgePCA9685 as HBridge
else:
    pass


def motoren_autonom(funktion):
    global GV_speedleft, GV_speedright
    if(funktion == "VOR"):
        if GV_speedleft > GC_speed_max:
            GV_speedleft = GC_speed_max
        if GV_speedright > GC_speed_max:
            GV_speedright = GC_speed_max
        if not testmode:
            HBridge.setMotorLeft(GV_speedleft)
            HBridge.setMotorRight(GV_speedright)
        else:
            pass
    if(funktion == "ZURUECK"):
        if GV_speedleft < GC_speed_min:
            GV_speedleft = GC_speed_min
        if GV_speedright < GC_speed_min:
            GV_speedright = GC_speed_min
        if not testmode:
            HBridge.setMotorLeft(GV_speedleft)
            HBridge.setMotorRight(GV_speedright)
        else:
            pass
    if(funktion == "STOP"):
        GV_speedleft = GC_speed_zero
        GV_speedright = GC_speed_zero
        if not testmode:
            HBridge.setMotorLeft(GV_speedleft)
            HBridge.setMotorRight(GV_speedright)
        else:
            pass
    if(funktion == "RECHTS"):
        if GV_speedright < GC_speed_min:
            GV_speedright = GC_speed_min
        if GV_speedleft > GC_speed_max:
            GV_speedleft = GC_speed_max
        if not testmode:
            HBridge.setMotorLeft(GV_speedleft)
            HBridge.setMotorRight(GV_speedright)
        else:
            pass
    if(funktion == "LINKS"):
        if GV_speedleft < GC_speed_min:
            GV_speedleft = GC_speed_min
        if GV_speedright > GC_speed_max:
            GV_speedright = GC_speed_max
        if not testmode:
            HBridge.setMotorLeft(GV_speedleft)
            HBridge.setMotorRight(GV_speedright)
        else:
            pass
    if(funktion == "ENDE"):
        func = sys._getframe().f_code.co_name
        txt = f"HW ordnungsgemäß heruntergefahren"
        logging.info(f"{func:>15s} : {txt:s}")
        if not testmode:
            GV_speedleft = GC_speed_zero
            GV_speedright = GC_speed_zero
            HBridge.setMotorLeft(GV_speedleft)
            HBridge.setMotorRight(GV_speedright)
            HBridge.exit()
        else:
            pass


def motoren_manuell(funktion):
    global GV_speedleft, GV_speedright
    speed_incr = 0.1
    # Das Roboter-Auto faehrt vorwaerts, wenn der Anwender die
    # Tastenkombination für "VOR" drückt.
    if(funktion == "VOR"):
        # Das Roboter-Auto beschleunigt in Schritten von 10 %
        # bei jedem Tastendruck für "VOR" bis maximal
        # 100 %. Dann faehrt es maximal schnell vorwaerts.
        GV_speedleft = round((GV_speedleft + speed_incr), 1)
        GV_speedright = round((GV_speedright + speed_incr), 1)
        if GV_speedleft > GC_speed_max:
            GV_speedleft = GC_speed_max
        if GV_speedright > GC_speed_max:
            GV_speedright = GC_speed_max
        # Dem Programm L298NHBridge, das zu Beginn
        # importiert wurde, wird die Geschwindigkeit fuer
        # die linken und rechten Motoren uebergeben.
        if not testmode:
            HBridge.setMotorLeft(GV_speedleft)
            HBridge.setMotorRight(GV_speedright)
        else:
            pass
    # Das Roboter-Auto faehrt rueckwaerts, wenn die Tastenkombination
    # für "ZURUECK" gedrueckt wird.
    if(funktion == "ZURUECK"):
        # Das Roboter-Auto bremst in Schritten von 10 %
        # bei jedem Tastendruck für "ZURUECK" bis maximal
        # -100 %. Dann faehrt es maximal schnell rueckwaerts.
        GV_speedleft = round((GV_speedleft - speed_incr), 1)
        GV_speedright = round((GV_speedright - speed_incr), 1)
        if GV_speedleft < GC_speed_min:
            GV_speedleft = GC_speed_min
        if GV_speedright < GC_speed_min:
            GV_speedright = GC_speed_min
        # Dem Programm L298NHBridge, das zu Beginn
        # importiert wurde, wird die Geschwindigkeit fuer
        # die linken und rechten Motoren uebergeben.
        if not testmode:
            HBridge.setMotorLeft(GV_speedleft)
            HBridge.setMotorRight(GV_speedright)
        else:
            pass
    # Mit dem Druecken der Tastenkombination "STOP" werden
    # die Motoren angehalten.
    if(funktion == "STOP"):
        GV_speedleft = GC_speed_zero
        GV_speedright = GC_speed_zero
        if not testmode:
            HBridge.setMotorLeft(GV_speedleft)
            HBridge.setMotorRight(GV_speedright)
        else:
            pass
    # Mit der Tastenkombination für "RECHTS" lenkt das Auto nach rechts,
    # bis die max/min. Geschwindigkeit der linken und
    # rechten Motoren erreicht ist.
    if(funktion == "RECHTS"):
        GV_speedright = round((GV_speedright - speed_incr), 1)
        GV_speedleft = round((GV_speedleft + speed_incr), 1)
        if GV_speedright < GC_speed_min:
            GV_speedright = GC_speed_min
        if GV_speedleft > GC_speed_max:
            GV_speedleft = GC_speed_max
        if not testmode:
            HBridge.setMotorLeft(GV_speedleft)
            HBridge.setMotorRight(GV_speedright)
        else:
            pass
    # Mit der Tastenkombination für "LINKS" lenkt das Auto nach links,
    # bis die max/min. Geschwindigkeit der linken und
    # rechten Motoren erreicht ist.
    if(funktion == "LINKS"):
        GV_speedleft = round((GV_speedleft - speed_incr), 1)
        GV_speedright = round((GV_speedright + speed_incr), 1)
        if GV_speedleft < GC_speed_min:
            GV_speedleft = GC_speed_min
        if GV_speedright > GC_speed_max:
            GV_speedright = GC_speed_max
        if not testmode:
            HBridge.setMotorLeft(GV_speedleft)
            HBridge.setMotorRight(GV_speedright)
        else:
            pass
    # Mit der Tastenkombination "ENDE" wird die Endlosschleife beendet
    # und das Programm ebenfalls beendet. Zum Schluss wird
    # noch die Funktion exit() aufgerufen, die die Motoren stoppt.
    if(funktion == "ENDE"):
        func = sys._getframe().f_code.co_name
        txt = f"HW ordnungsgemäß heruntergefahren"
        logging.info(f"{func:>15s} : {txt:s}")
        if not testmode:
            GV_speedleft = GC_speed_zero
            GV_speedright = GC_speed_zero
            HBridge.setMotorLeft(GV_speedleft)
            HBridge.setMotorRight(GV_speedright)
            HBridge.exit()
        else:
            pass

# Check, ob die Treads noch laufen


def live_check():
    alive = [[0, 0], [0, 0], [0, 0]]
    thread_up = 'running'
    thread_down = 'stopped'
    for index, thread in enumerate(GV_th_list):
        name = thread.getName()
        if thread.is_alive():
            alive[index][0] = f"{name:25s}"
            alive[index][1] = f"{thread_up:8s}"
        else:
            alive[index][0] = f"{name:25s}"
            alive[index][1] = f"{thread_down:8s}"
    return alive

# Ermittlung Steuerungsbefehl aus Tastendruck


def steuerbefehl(key):
    if (key == "m"):
        befehl = "MODUS"
    elif (key == k.UP) or (key == "w"):
        befehl = "VOR"
    elif (key == k.DOWN) or (key == "s"):
        befehl = "ZURUECK"
    elif (key == k.LEFT) or (key == "a"):
        befehl = "LINKS"
    elif (key == k.RIGHT) or (key == "d"):
        befehl = "RECHTS"
    elif (key == " ") or (key == "q"):
        befehl = "STOP"
    elif (key == k.CTRL_C) or (key == "x"):
        befehl = "ENDE"
    else:
        befehl = ""
    return befehl

# Ausgabe Startbildschirm


def printstart(warten):
    show_header(G_HEADER_1, G_HEADER_2, __file__, G_OS)
    print("*", 58*"=", "*", sep="")
    print("*  ", c.lightcyan, "Robotersteuerung per Tastatur",
          27*" ", c.reset, "*", sep="")
    print("*", 58*" ", "*", sep="")
    print("*  \'m\'                       : "
          "Manuell / Autonom Fahren    *\r")
    print("*  \'w\' / \'Pfeiltaste OBEN\'   : "
          "vorwärts (beschleunigen)    *\r")
    print("*  \'s\' / \'Pfeiltaste UNTEN\'  : "
          "rückwärts (beschleunigen)   *\r")
    print("*  \'a\' / \'Pfeiltaste LINKS\'  : "
          "nach links lenken           *\r")
    print("*  \'d\' / \'Pfeiltaste RECHTS\' : "
          "nach rechts lenken          *\r")
    print("*  \'q\' / \'Leer-Taste\'        : "
          "Motoren stoppen             *\r")
    print("*  \'x\' / \'Ctrl-C\'            : "
          "Steuerung beenden           *\r")
    print("*", 58*" ", "*", sep="")
    print("*", 58*"=", "*", sep="")
    sleep(warten)

# Thread-Funktion Bildschirmanzeige


def anzeige(ev):
    func = sys._getframe().f_code.co_name
    id = threading.get_ident()
    txt = f"Thread started {id:10d}"
    logging.info(f"{func:>15s} : {txt:s}")
    lk = threading.Lock()
    while not ev.is_set():
        sleep(0.5)
        th_alive = live_check()
        clean_console()
        lk.acquire()
        print("\n*", 58*"=", "*\r", sep="")
        print("*             ", c.lightcyan,
              f"System-Informationen ({aktuelle_uhrzeit():8s})",
              c.reset, "              *\r", sep="")
        print("*", 58*" ", "*\r", sep="")
        for thread in th_alive:
            if thread[1] == 'running ':
                f1 = c.lightgreen
            else:
                f1 = c.lightred
            print(f"*  {thread[0]:25s} : {f1}{thread[1]:8s}",
                  c.reset, "                    *\r", sep="")
        print("*", 58*" ", "*\r", sep="")
        print("*", 58*"=", "*\r", sep="")
        print("*                   ", c.lightcyan,
              "Entfernungsmessung", c.reset,
              "                     *\r", sep="")
        print("*", 58*" ", "*\r", sep="")
        print("*           ", c.yellow,
              f"Hindernis vorne : {GV_entfernung:5d} cm", c.reset,
              "                     *\r", sep="")
        print("*", 58*" ", "*\r", sep="")
        print("*", 58*"=", "*\r", sep="")
        print("*           ", c.lightcyan,
              "Geschwindigkeitsanzeige der Motoren",
              c.reset, "            *\r", sep="")
        print("*", 58*" ", "*\r", sep="")
        if GV_modus == GC_mod_auto:
            f1 = c.pink
        else:
            f1 = c.yellow
        print("*                  ", c.yellow,
              "Fahrmodus : ", f1,
              f"{GV_modus:8s}", c.reset,
              "                    *\r", sep="")
        print("*           ", c.yellow,
              f"Steuerungsbefehl : {GV_anz_funk:>7s}", c.reset,
              "                     *\r", sep="")
        print("*", 58*" ", "*\r", sep="")
        print("*  linker Motor --> ", c.yellow,
              f"{int(GV_speedleft*100):4d} %", c.reset, "   |",
              c.yellow, f" {int(GV_speedright*100):4d} %", c.reset,
              "  <-- rechter Motor   *\r", sep="")
        print("*", 58*"=", "*\r", sep="")
        lk.release()
    sleep(1.0)
    txt = f"Thread stopped {id:10d}"
    logging.info(f"{func:>15s} : {txt:s}")

# Thread-Funktion Taste einlesen und Steuerbefehl in Queue schreiben


def taste(ev, ev_stop, qu):
    func = sys._getframe().f_code.co_name
    id = threading.get_ident()
    txt = f"Thread started {id:10d}"
    logging.info(f"{func:>15s} : {txt:s}")
    global GV_modus
    befehl = ""
    while not ev.is_set():
        sleep(0.1)
        key = getkey()
        befehl = steuerbefehl(key)
        if befehl == "MODUS":
            if GV_modus == GC_mod_man:
                GV_modus = GC_mod_auto
            else:
                GV_modus = GC_mod_man
        if befehl != "" and befehl != "MODUS" and \
           befehl != "ENDE" and not ev_stop.is_set():
            qu.put(befehl)
        if befehl == "ENDE":
            ev_stop.set()
            ev.set()
    sleep(2.0)
    txt = f"Thread stopped {id:10d}"
    logging.info(f"{func:>15s} : {txt:s}")

# Thread Entfernungsmessung vorne


def distance(ev):
    func = sys._getframe().f_code.co_name
    id = threading.get_ident()
    txt = f"Thread started {id:10d}"
    logging.info(f"{func:>15s} : {txt:s}")
    global GV_entfernung
    while not ev.is_set():
        GV_entfernung = randint(0, 100)
        sleep(1.0)
    sleep(0.3)
    txt = f"Thread stopped {id:10d}"
    logging.info(f"{func:>15s} : {txt:s}")

# Autonomes Fahren


def autonom_fahren(ev_stop, qu):
    global GV_speedleft, GV_speedright
    global GV_anz_funk
    warn_dist_low = 50
    warn_dist_medium = 30
    warn_dist_high = 10
    func = sys._getframe().f_code.co_name
    txt = f"Autonomes Fahren started"
    logging.info(f"{func:>15s} : {txt:s}")
    fast = GC_speed_max
    medium = GC_speed_max / 2.5
    slow = GC_speed_max / 10
    while not ev_stop.is_set() and GV_modus == GC_mod_auto:
        dist = GV_entfernung
        # Beginne mit vorwäerts fahren
        funktion = GV_anz_funk = "VOR"
        if dist >= warn_dist_low:
            GV_speedleft = round(fast, 1)
            GV_speedright = round(fast, 1)
            txt = f"Entf. {dist:3d}cm , Speed {int(GV_speedleft*100):3d}% , " \
                  f"{GV_anz_funk:6s} , Vollgas"
            if GC_log_detail:
                logging.info(f"{func:>15s} : {txt:s}")
            motoren_autonom(funktion)
        elif dist >= warn_dist_medium:
            GV_speedleft = round(medium, 1)
            GV_speedright = round(medium, 1)
            txt = f"Entf. {dist:3d}cm , Speed {int(GV_speedleft*100):3d}% , " \
                  f"{GV_anz_funk:6s} , gedrosselt"
            if GC_log_detail:
                logging.info(f"{func:>15s} : {txt:s}")
            motoren_autonom(funktion)
        elif dist >= warn_dist_high:
            GV_speedleft = round(slow, 1)
            GV_speedright = round(slow, 1)
            txt = f"Entf. {dist:3d}cm , Speed {int(GV_speedleft*100):3d}% , " \
                  f"{GV_anz_funk:6s} , stark gedrosselt"
            if GC_log_detail:
                logging.info(f"{func:>15s} : {txt:s}")
            motoren_autonom(funktion)
        else:
            # erst mal anhalten und kurz warten
            GV_speedleft = round(GC_speed_zero, 1)
            GV_speedright = round(GC_speed_zero, 1)
            funktion = GV_anz_funk = "STOP"
            txt = f"Entf. {dist:3d}cm , Speed {int(GV_speedleft*100):3d}% , " \
                  f"{GV_anz_funk:6s} , angehalten"
            if GC_log_detail:
                logging.info(f"{func:>15s} : {txt:s}")
            motoren_autonom(funktion)
            sleep(0.5)
            # Drehe auf der Stelle in Abhängigkeit der
            # Zufallszahl (0 = links , 1 = rechts)
            drehrichtung = randint(0, 1)
            if drehrichtung == 0:
                GV_speedleft = round(-slow, 1)
                GV_speedright = round(slow, 1)
                funktion = GV_anz_funk = "LINKS"
                txt = f"Drehung       Speed {int(abs(GV_speedleft)*100):3d}% , " \
                      f"{GV_anz_funk:6s}"
                if GC_log_detail:
                    logging.info(f"{func:>15s} : {txt:s}")
            else:
                GV_speedleft = round(slow, 1)
                GV_speedright = round(-slow, 1)
                funktion = GV_anz_funk = "RECHTS"
                txt = f"Drehung       Speed {int(abs(GV_speedleft)*100):3d}% , " \
                      f"{GV_anz_funk:6s}"
                if GC_log_detail:
                    logging.info(f"{func:>15s} : {txt:s}")
            motoren_autonom(funktion)
            sleep(2.0)
            # Stoppe Drehung
            GV_speedleft = round(GC_speed_zero, 1)
            GV_speedright = round(GC_speed_zero, 1)
            funktion = GV_anz_funk = "STOP"
            txt = f"Drehung       Speed {int(GV_speedleft*100):3d}% , " \
                  f"{GV_anz_funk:6s}"
            if GC_log_detail:
                logging.info(f"{func:>15s} : {txt:s}")
            motoren_autonom(funktion)
            sleep(0.5)
        sleep(0.2)
    funktion = GV_anz_funk = "STOP"
    motoren_autonom(funktion)
    # Queue komplett leeren nach autonomen Fahren
    while not qu.empty():
        dummy = qu.get()
    txt = f"Autonomes Fahren stopped"
    logging.info(f"{func:>15s} : {txt:s}")

# Manuelles Fahren


def manuell_fahren(ev_stop, qu):
    global GV_anz_funk
    func = sys._getframe().f_code.co_name
    txt = f"Manuelles Fahren started"
    logging.info(f"{func:>15s} : {txt:s}")
    while not ev_stop.is_set() and GV_modus == GC_mod_man:
        if not qu.empty():
            funktion = GV_anz_funk = qu.get()
            motoren_manuell(funktion)
        sleep(0.2)
    funktion = GV_anz_funk = "STOP"
    motoren_manuell(funktion)
    txt = f"Manuelles Fahren stopped"
    logging.info(f"{func:>15s} : {txt:s}")

# Zentralschleife


def loop_main(ev_stop, qu):
    func = sys._getframe().f_code.co_name
    txt = f"Zentralschleife started"
    logging.info(f"{func:>15s} : {txt:s}")
    while not ev_stop.is_set():
        # hier kommen weitere Tasks rein, falls erforderlich

        # ##############################
        if GV_modus == GC_mod_auto:
            autonom_fahren(ev_stop, qu)
        elif GV_modus == GC_mod_man:
            manuell_fahren(ev_stop, qu)
        else:
            print("Modus undefiniert")
        sleep(0.1)
    func = sys._getframe().f_code.co_name
    txt = f"HW ordnungsgemäß heruntergefahren"
    logging.info(f"{func:>15s} : {txt:s}")
    if not testmode:
        GV_speedleft = GC_speed_zero
        GV_speedright = GC_speed_zero
        HBridge.setMotorLeft(GV_speedleft)
        HBridge.setMotorRight(GV_speedright)
        HBridge.exit()
    else:
        pass
    sleep(0.1)
    txt = f"Zentralschleife stopped"
    logging.info(f"{func:>15s} : {txt:s}")

# Hauptprogramm


def _main():
    format = "%(asctime)s: %(levelname)s - %(message)s"
    log = os.path.basename(__file__).replace(".py", ".log")
    log_file = homedir = os.path.expanduser('~')+'/Python/logs/'+log
    if platform.system() == 'Windows':
        log_file = str(Path(os.getcwd()).parent)+'\\logs\\'+log
    logging.basicConfig(format=format, level=logging.WARNING,
                        datefmt="%d-%m-%Y %H:%M:%S", filename=log_file,
                        filemode='a')
    if GC_log_ein:
        logging.getLogger().setLevel(logging.DEBUG)
    logging.info(50*">")
    try:
        func = sys._getframe().f_code.co_name
        id = threading.get_ident()
        txt = f"Thread started {id:10d}"
        logging.info(f"{func:>15s} : {txt:s}")
        ev0 = threading.Event()         # Bildschirmanzeige
        ev0.clear()
        ev1 = threading.Event()         # Entfernungsmessung
        ev1.clear()
        ev2 = threading.Event()         # Tastatatureingabe
        ev2.clear()
        ev_stop = threading.Event()
        ev_stop.clear()
        qu = queue.Queue()
        t = threading.Thread(target=anzeige, args=(ev0,),
                             name="Thread Bildschirmanzeige")
        GV_th_list.append(t)
        t = threading.Thread(target=distance, args=(ev1,),
                             name="Thread Entfernungsmessung")
        GV_th_list.append(t)
        t = threading.Thread(target=taste, args=(ev2, ev_stop, qu,),
                             name="Thread Tastaturbetätigung")
        GV_th_list.append(t)
        printstart(0.5)
        getkey()
        for thread in GV_th_list:
            thread.start()
            sleep(1.0)
        loop_main(ev_stop, qu)
        ev2.set()
        sleep(1.0)
        ev1.set()
        sleep(1.0)
        ev0.set()
        for thread in GV_th_list:
            thread.join()
        print("\nEnde Robotersteuerung\r\n")
        func = sys._getframe().f_code.co_name
        id = threading.get_ident()
        txt = f"Thread stopped {id:10d}"
        logging.info(f"{func:>15s} : {txt:s}")
    except (KeyboardInterrupt):
        if not testmode:
            GV_speedleft = GC_speed_zero
            GV_speedright = GC_speed_zero
            HBridge.setMotorLeft(GV_speedleft)
            HBridge.setMotorRight(GV_speedright)
            HBridge.exit()
        else:
            pass
        ev_stop.set()
        sleep(1.0)
        print("\nAbbruch Robotersteuerung\r\n")
        txt = f"Thread interrupted by CTRL-C {id:10d}"
        logging.warning(f"{func:>15s} : {txt:s}")
        txt = f"Exception occurred {id:10d}"
        logging.error(f"{func:>15s} : {txt:s}", exc_info=True)


if __name__ == "__main__":
    _main()
