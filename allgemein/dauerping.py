#!/usr/bin/env python3

# Programm     : dauerping.py
# Version      : 1.01
# SW-Stand     : 17.02.2022
# Autor        : Kanopus1958
# Beschreibung : Dauer ping auf ausgewählte Ziel-Rechner im Netzwerk Andromeda
from time import sleep
import datetime
import threading
import socket
import subprocess
from rwm_mod01 import show_header, aktuelle_uhrzeit, aktuelles_datum, getch
from rwm_steuerung import color as c, position as p, key_stroke as k
import os
G_OS = ('Raspbian', 'Debian')
G_HEADER_1 = '# Monitor Status aller Rechner'
G_HEADER_2 = ' im Netz Andromeda (ping)    #'


def ping_thread():
    cmd_ping = "ping -c 1"
    ziel_rechner = []
    fobj = open(input_ping, "r")
    for line in fobj:
        zeile = line.rstrip()
        if zeile.find("@@@PING@@@") >= 0:
            zeile = zeile.replace("@@@PING@@@,", "")
            ziel_rechner.append(zeile)
    fobj.close()
    print("Monitoring gestartet: ", aktuelles_datum(),
          " ", aktuelle_uhrzeit(), "\r", sep="")
    print(60*"*", "\r")
    anzeige_komplett = False
    N_Druck = len(ziel_rechner)
    while not stop or not anzeige_komplett:
        anz_z = 0
        for z in ziel_rechner:
            if stop and anzeige_komplett:
                break
            cmd = cmd_ping+" "+z
            x = subprocess.run(
                               cmd, shell=True, stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
            if x.returncode == 0:
                sleep(0.1)
                print("*", c.yellow,
                      f"{aktuelle_uhrzeit():8s}   {z:20s} : Zielrechner ON",
                      c.reset, 5*" ", "*\r")
            elif x.returncode == 1:
                print("*", c.lightcyan,
                      f"{aktuelle_uhrzeit():8s}   {z:20s} : Zielrechner OFF",
                      c.reset, 4*" ", "*\r")
            else:
                sleep(3.0)
                print("*", c.lightred,
                      f"{aktuelle_uhrzeit():8s}   {z:20s} : "
                      "Zielrechner UNKNOWN",
                      c.reset, 0*" ", "*\r")
            anz_z += 1
        if not stop or not anzeige_komplett:
            print(60*"*", "\r")
        if stop:
            print((N_Druck-anz_z-1)*p.down)
            if not anzeige_komplett:
                print(2*p.up, end="")
        else:
            print((N_Druck+2)*p.up)
        anzeige_komplett = True
    print(c.reset)
    print("Monitoring beendet  :",
          aktuelles_datum(), aktuelle_uhrzeit(), "\n")
    return


def _main():
    global stop
    global input_ping
    try:
        show_header(G_HEADER_1, G_HEADER_2, __file__, G_OS)
        input_ping = os.path.realpath(__file__).replace(".py", ".input")
        if not os.path.isfile(input_ping):
            print(c.lightred, "\r\nError --> Input-Datei exitiert nicht :",
                  input_ping, c.reset, "\n")
        else:
            stop = False
            th_ping = threading.Thread(target=ping_thread)
            th_ping.start()
            while True:
                sleep(0.1)
                char = getch()
                if char == 'q' or char == k.ESC:  # Escape-Sequenz ESC = \xlb
                    stop = True
                    sleep(1.0)
                    break
                char = ""
            th_ping.join
    except(KeyboardInterrupt, SystemExit):
        sleep(1.0)
        stop = True
        print(c.lightred, p.up)
        print(3*" ", "\n!!! Programm abgebrochen !!!\n", c.reset)


if __name__ == "__main__":
    _main()
