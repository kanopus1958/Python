#!/usr/bin/env python3

# Programm     : synchronisation.py
# Version      : 1.02
# SW-Stand     : 17.02.2022
# Autor        : Kanopus1958
# Beschreibung : rsync von ausgewählten Verzeichnissen auf mehrere Ziel-Rechner
G_OS = ('Raspbian','Debian') 
G_HEADER_1 = '# RSYNC wichtiger Dateien auf '
G_HEADER_2 = 'Linux-Rechner in Andromeda   #'

# ----------------------------------------------------------------------------
# Globale Konstanten GC_<name> für alle Funktionen und Theads
GC_dryrun = False
# ----------------------------------------------------------------------------

import sys
import os
import platform
from rwm_steuerung import color as c, position as p
from rwm_mod01 import show_header, aktuelle_uhrzeit, aktuelles_datum
import subprocess
from socket import gethostname
import datetime
import time
from time import sleep


def synchronisation():
    log_ping = "/home/pi/Python/logs/ping.log"
    log_rsync = "/home/pi/Python/logs/rsync.log"
    cmd_ping = "ping -c1"
    if GC_dryrun:
        cmd_rsync = "rsync -auvn"
    else:
        cmd_rsync = "rsync -auv"
    ziel_rechner = []
    rsync_param = []
    fobj = open(input_rsync, "r")
    for line in fobj:
        zeile = line.rstrip()
        if zeile.find("@@@RS@@@") >= 0:
            zeile = zeile.replace("@@@RS@@@,", "")
            ziel_rechner.append(zeile[zeile.find("@")+1:zeile.rfind(":")])
            rsync_param.append(zeile.replace(",", " "))
    fobj.close()
    print("Datentransfer gestartet :", aktuelles_datum(), aktuelle_uhrzeit())
    print("\r", c.yellow, 60*"*", "\r", sep="")
    fobj1 = open(log_ping, "w")
    fobj2 = open(log_rsync, "w")
    i = 0
    knotenname = gethostname()
    dead_ziel = ""
    for z in ziel_rechner:
        if z != dead_ziel:
            cmd = cmd_ping+" "+z
            x = subprocess.run(cmd, shell=True, stdout=fobj1, stderr=subprocess.STDOUT)
            if x.returncode == 0:
                print(f"*  Datei-Transfer startet    : {knotenname:11s}--> {z:11s}", " *\r")
                print(f"*  {rsync_param[i][:rsync_param[i].find(' ')]:50s}", 4*" ", "*\r")
                cmd = cmd_rsync+" "+rsync_param[i]
                x = subprocess.run(cmd, shell=True, stdout=fobj2, stderr=subprocess.STDOUT)
                if x.returncode == 0:
                    print(f"*  Datei-Transfer erfolgreich", 28*" ", "*\r")
                else:
                    print("*", c.lightred, f"Datei - Transfer fehlgeschlagen !", c.yellow, 20*" ", "*\r")
            elif x.returncode == 1:
                dead_ziel = z
                print("*", c.lightcyan, f"Zielrechner ausgeschaltet : {z:12s}", c.yellow, 13*" ", "*\r")
                print("*", c.lightcyan, f"Datei - Transfer fehlgeschlagen !", c.yellow, 20*" ", "*\r")
            else:
                print("*", c.lightred, f"Unbekannter Zielrechner   : {z:12s}", c.yellow, 13*" ", "*\r")
                print("*", c.lightred, f"Datei - Transfer fehlgeschlagen !", c.yellow, 20*" ", "*\r")
                dead_ziel = z
            print(60*"*", "\r")
        i += 1
    fobj1.close()
    fobj2.close()
    print(c.reset, p.up)
    print("Datentransfer beendet  :", aktuelles_datum(), aktuelle_uhrzeit(),"\n")
    return()
    
def _main():
    global input_rsync
    try:
        show_header(G_HEADER_1, G_HEADER_2, __file__, G_OS)
        input_rsync = os.path.realpath(__file__).replace(".py", ".input")
        if not os.path.isfile(input_rsync):
            print(c.lightred, "\r\nError --> Input-Datei exitiert nicht :", input_rsync, c.reset, "\n")
        else:
            knotenname = gethostname()
            if knotenname != "Merkur":
                print(c.lightred, "\r\nError --> Programmausführung auf diesem Knoten nicht gestattet !", c.reset, "\n")
            else:
                synchronisation()
    except(KeyboardInterrupt, SystemExit):
        print(c.lightred, p.up)
        print(3*" ", "\n!!! Programm abgebrochen !!!\n", c.reset)
        sys.exit(False)
 
if __name__ == "__main__":
    _main() 