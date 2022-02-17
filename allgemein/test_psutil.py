#!/usr/bin/env python3

# Programm     : test_psutil.py
# Version      : 1.02
# SW-Stand     : 17.02.2022
# Autor        : Kanopus1958
# Beschreibung : Test von psutil Funktionalitäten
G_OS = ('Raspbian','Debian','Windows') 
G_HEADER_1 = '# Test psutil Funktionen      '
G_HEADER_2 = '      (Stop q/CTRL_C/CTRL_Z) #'

# ----------------------------------------------------------------------------
# Globale Konstanten GC_<name> für alle Funktionen und Theads
GC_messzyklus = 1.0
# ----------------------------------------------------------------------------

import platform
from rwm_steuerung import color as c, position as p, key_stroke as k
from rwm_mod01 import show_header, aktuelle_uhrzeit, aktuelles_datum, getch
import threading
import psutil
from time import sleep

def anzeige_thread():
    N_Druck = 12 # Maximale Anzahl von druckbaren Ausgabezeilen
    sleep(0.1)
    print("Messung gestartet  : ", aktuelles_datum(), \
          " ", aktuelle_uhrzeit(), sep="", end="\n\r")
    zyklus = 0
    anzeige_komplett = False
    while not stop or not anzeige_komplett:
        anz_z = N_Druck
        zyklus += 1
        cpu_count = psutil.cpu_count()
        cpu_load = psutil.cpu_percent(GC_messzyklus)
        mem = psutil.virtual_memory()
        freq = psutil.cpu_freq()
        tcpu_exist = False
        tgpu_exist = False
        if platform.system() == 'Linux':
            temp = psutil.sensors_temperatures()
            for name, entries in temp.items():
                if name == "k10temp" or name == "cpu_thermal":
                    tcpu_exist = True
                    for entry in entries:
                        tcpu = entry.current
                elif name == "amdgpu":
                    tgpu_exist = True
                    for entry in entries:
                        tgpu = entry.current
        print(60*"*", "\r")
        print(c.yellow, end="")
        print(f"* Messzeit         : {aktuelle_uhrzeit():8s}", \
              28*" ", "*\r")
        print(f"* Testzyklus       : {zyklus:8d}", \
              28*" ", "*\r")
        print(f"* CPU Anzahl       : {cpu_count:8d} Stk", \
              24*" ", "*\r")
        print(f"* CPU Last         : {cpu_load:8.1f} %", \
              26*" ", "*\r")
        if tcpu_exist:
            print(f"* CPU Temperatur   : {tcpu:8.1f} 'C", \
                  25*" ", "*\r")
        else:
            anz_z -= 1
        if tgpu_exist:
            print(f"* GPU Temperatur   : {tgpu:8.1f} 'C", \
                  25*" ", "*\r")
        else:
            anz_z -= 1
        print(f"* Taktrate aktuell : {freq.current:8.1f} MHz", \
              24*" ", "*\r")
        print(f"* Taktrate min.    : {freq.min:8.1f} MHz", \
              24*" ", "*\r")
        print(f"* Taktrate max.    : {freq.max:8.1f} MHz", \
              24*" ", "*\r")
        print(f"* RAM Auslastung   : {mem.percent:8.1f} %", \
              26*" ", "*\r")
        print(f"* RAM Belegung     : {mem.used/1024/1024:8.1f} MB", \
              25*" ", "*\r")
        print(f"* RAM total        : {mem.total/1024/1024:8.1f} MB", \
              25*" ", "*\r")
        print(c.reset, end="")
        print(60*"*", "\r")
        print((anz_z+2)*p.up, end="")
        sleep(0.1)
        anzeige_komplett = True
    print((anz_z+2)*p.down, end="")
    print("Messung beendet    : ", aktuelles_datum(), \
          " ", aktuelle_uhrzeit(), sep="", end="\n\r")
    print()
    return
    
def _main():
    global stop
    try:
        show_header(G_HEADER_1, G_HEADER_2, __file__, G_OS)
        stop = False
        th_anzeige = threading.Thread(target=anzeige_thread)
        th_anzeige.start()
        while True:
            sleep(0.1)
            char = getch()
            if char == 'q' or char == k.CTRL_C or char == k.CTRL_Z:
                sleep(1.0)
                break
            char = ""
        stop = True
        th_anzeige.join()
    except(KeyboardInterrupt, SystemExit):
        sleep(1.0)
        stop = True
        print(c.lightred, p.up)
        print(3*" ", "\n!!! Programm abgebrochen !!!\n", c.reset)

if __name__ == "__main__":
    _main()