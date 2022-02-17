#!/usr/bin/env python3

# Programm     : besonderezahl.py
# Version      : 1.01
# SW-Stand     : 17.02.2022
# Autor        : Kanopus1958
# Beschreibung : Zahl mit Persistence 11 ist 277777788888899
G_OS = ('Raspbian','Debian','Windows') 
G_HEADER_1 = '# Berechnung Persistence      '
G_HEADER_2 = ' (277777788888899 hat 11)    #'

# ----------------------------------------------------------------------------
# Globale Konstanten GC_<name> für alle Funktionen und Theads
GC_anz_interval = 100000
GC_max_zahl = 1000000000000000 # 16-stellig
# GC_max_zahl = 1500000
# ----------------------------------------------------------------------------

import sys
import os
import platform
from pathlib import Path
from rwm_mod01 import show_header, aktuelle_uhrzeit, getch
from rwm_steuerung import color as c, position as p, key_stroke as k
from time import time
import datetime
import time
from time import sleep
import threading
from multiprocessing import Process, Pipe, active_children
import logging

def tasten_thread(ev):
    try:
        logging.info(f"Thread gestartet : {sys._getframe().f_code.co_name} {threading.get_ident()}")
        #print("Thread gestartet : ", f"{sys._getframe(  ).f_code.co_name}", \
        #       threading.get_ident(), "\n")
        while not ev.is_set():
            # char = getch()
            char = input()
            if char == 'q' or char == k.CTRL_C or char == k.CTRL_Z:
                ev.set()
                sleep(0.1)
                break
            else:
                print(p.up, f"\r", 70*" ", f"\r", p.up, sep="")
            char = ""
            sleep(0.1)
        #print("\r\nThread wird beendet : ", f"{sys._getframe(  ).f_code.co_name}", \
        #       threading.get_ident(), "\r")
        logging.info(f"Thread gestoppt : {sys._getframe().f_code.co_name} {threading.get_ident()}")
        return
    except(KeyboardInterrupt, SystemExit):
        sys.exit(False)

def zeit_diff(t_start):
    dt = time.time() - t_start
    stunde = int(dt / 3600)
    minute = int((dt - 3600 * stunde) / 60)
    sekunde = int(dt - 60 * minute - 3600 * stunde)
    return "{0:02d}:{1:02d}:{2:02d}".format(stunde, minute, sekunde)

def persistence(n, inner_pers):
    inner_pers += 1
    if len(str(n)) == 1:
        return inner_pers
    digits = [int(i) for i in str(n)]
    result = 1
    for j in digits:
        result *= j
    # print(f"     {result:20d}")
    return persistence(result, inner_pers)

def besonderezahl_proc(conn, startzeit, max_zahl):
    logging.info(f"Thread gestartet : {sys._getframe().f_code.co_name} {threading.get_ident()}")
    pers_liste = []
    #print("Thread gestartet : ", f"{sys._getframe(  ).f_code.co_name}", \
    #       threading.get_ident(), "\n")
    for i in range(1, max_zahl+1):
        if i % GC_anz_interval == 0:
            conn.send(['CNTR', i, zeit_diff(startzeit),aktuelle_uhrzeit()])
        pers = persistence(i, -1)
        if len(pers_liste) <= pers:
            pers_liste.append(-1)
        if pers_liste[pers] < 0:
            pers_liste[pers] = i
            #print(c.yellow, "\r", aktuelle_uhrzeit(), \
            #      " (", zeit_diff(startzeit),") | ", \
            #      f"Persistence {pers:3d} | kleinste Zahl {i:18d}\n", \
            #            c.reset, sep='', end="")
            conn.send(['PERS', i, zeit_diff(startzeit), aktuelle_uhrzeit()])
    conn.send(['STOP', 0, zeit_diff(startzeit), aktuelle_uhrzeit()])
    #print("\r\nThread wird beendet : ", f"{sys._getframe(  ).f_code.co_name}", \
    #       threading.get_ident(), "\r")
    conn.close()
    logging.info(f"Thread gestoppt : {sys._getframe().f_code.co_name} {threading.get_ident()}")
    return

def anzeige_werte(tab, index, startzeit):
    show_header(G_HEADER_1, G_HEADER_2, __file__, G_OS)
    print(f"Persistence-Berechnungen gestartet      (Stop = 'q'+<Enter>)", sep="")
    print(60*"*", sep="")
    if len(tab) > 0:
        z = 0
        for wert in tab:
            print(c.yellow, f"{wert[2]:8s} ({wert[1]:8s})", \
                  f" | Pers {z:3d} | min-Zahl {wert[0]:18d}\n", \
                  c.reset, sep='', end="")
            z += 1
    index = "{:,}".format(index).replace(",",".")
    max_zahl = "{:,}".format(GC_max_zahl).replace(",",".")
    print(c.lightcyan, f"{aktuelle_uhrzeit()} ({zeit_diff(startzeit):8s})", \
          f"{index:>17s} / {max_zahl:>18s}", \
          c.reset, sep="")
    print(60*"*", sep="")
    return

def _main():
    format = "%(asctime)s: %(levelname)s - %(message)s"
    log = os.path.basename(__file__).replace(".py", ".log")
    log_file = homedir = os.path.expanduser('~')+'/Python/logs/'+log
    if platform.system() == 'Windows':
        log_file = str(Path(os.getcwd()).parent)+'\\logs\\'+log
    logging.basicConfig(format=format, level=logging.WARNING, datefmt="%d-%m-%Y %H:%M:%S", \
            filename=log_file, filemode='a')
    logging.getLogger().setLevel(logging.DEBUG) # Logger einschalten   
    logging.info(f"Thread gestartet : {sys._getframe().f_code.co_name} {threading.get_ident()}")
    sleep(1.0)
    pers_tab = []
    bearbeitet = 0
    t0 = time.time()
    proc_parent_conn, proc_child_conn = Pipe()
    proc = Process(target=besonderezahl_proc, args=(proc_child_conn, t0, GC_max_zahl,))
    proc.start()
    ev_t = threading.Event()
    ev_t.clear()
    th_tasten = threading.Thread(target=tasten_thread, \
                                 args=(ev_t,))
    th_tasten.daemon = True
    th_tasten.start()
    sleep(0.5)
    anzeige_werte(pers_tab, bearbeitet, t0)
    try:
        logging.info(f"Berechnung gestartet : {sys._getframe().f_code.co_name}")
        while not ev_t.is_set():
            sleep(0.5)
            # print("\rschlafe")
            if proc_parent_conn.poll():
                try:
                    ausgabe = proc_parent_conn.recv()
                    # print("\rausgabe : ", ausgabe)
                    if ausgabe[0] == 'STOP':
                            break
                    elif ausgabe[0] == 'CNTR':
                        bearbeitet = ausgabe[1]
                        anzeige_werte(pers_tab, bearbeitet, t0)
                        #print(c.yellow, f"\r{zeit_diff(t0):8s}: {bearbeitet:18d} von {GC_max_zahl:18d}", \
                        #      c.reset, sep="")
                    elif ausgabe[0] == 'PERS':
                        pers_tab.append(ausgabe[1:])
                        z = len(pers_tab) - 1
                        ergebnis_liste = []
                        ergebnis_liste.append(z)
                        ergebnis_liste = ergebnis_liste+pers_tab[z]
                        logging.info(f"Zwischenergebnis: {ergebnis_liste}")
                        #print(c.yellow, f"{pers_tab[z][2]:8s} ({pers_tab[z][1]:8s})", \
                        #      f" | Pers {z:3d} | min-Zahl {pers_tab[z][0]:18d}\n", \
                        #      c.reset, sep='', end="")
                    else:
                        print("\rSchnittstellenfehler !!!")
                except EOFError:
                    continue
            ausgabe = ""
        procs = active_children()
        for proc in procs:
            proc.terminate()
        #print(f"\r\nLetzte bearbeitete Zahl : {bearbeitet:18d} von {GC_max_zahl:18d}")
        #print("\n",pers_tab, sep='')
        #print("\nEnde   ", aktuelle_uhrzeit(), " (", \
        #      zeit_diff(t0), ")", "\n", sep='')
        logging.info(f"Berechnung beendet : {sys._getframe().f_code.co_name}")
        if not ev_t.is_set():
            print(f"Alle Berechnungen abgeschlossen", c.reset, sep="")
            print(c.lightred, f"Programm beenden mit 'q' <Enter> ", c.reset, sep="")
        th_tasten.join()
        print(p.up, f"\r     ", sep="")
        anzeige_werte(pers_tab, bearbeitet, t0)
        if not ev_t.is_set():
            print(f"Persistence-Berechnungen fehlerfrei abgeschlossen", sep="")
        else:
            print(c.lightred, f"Persistence-Berechnungen interaktiv abgebrochen", c.reset, sep="")
        print()
        logging.info(f"Thread gestoppt : {sys._getframe().f_code.co_name} {threading.get_ident()}")
    except(KeyboardInterrupt, SystemExit):
        procs = active_children()
        for proc in procs:
            proc.terminate()
        print(2*p.up)
        print("\r***\r", sep="", end="")
        print(c.lightred, "\nAbbruch mit CTRL-C um ", aktuelle_uhrzeit(), " (Laufzeit = ", \
              zeit_diff(t0), ")", "\n", c.reset, sep='')
        sys.exit(0)

if __name__ == "__main__":
    _main() 