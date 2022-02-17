#!/usr/bin/env python3

# Programm     : sensoren.py
# Version      : 1.02
# SW-Stand     : 17.02.2022
# Autor        : Kanopus1958
# Beschreibung : Periodische Anzeige der Temperatur, Spannung und Taktfrequenz
G_OS = ('Raspbian','Debian','Windows') 
G_HEADER_1 = '# Temperatur, Spannung und Tak'
G_HEADER_2 = 't               (Stop mit q) #'

import os
from rwm_steuerung import color as c, key_stroke as k
from rwm_mod01 import show_header, aktuelle_uhrzeit, getch
import socket
import threading
import subprocess
import datetime
from time import sleep

def sensoren():
    messzyklus = 1.0 # Messwiederholungszyklus in Sekunden
    temp_min = 100.0
    temp_max = 0.0
    print("Messung gestartet: ", aktuelle_uhrzeit(), " auf System '", socket.gethostname(), "'", sep="")
    print("   Uhrzeit    T-akt   T-min   T-max  Spannung     Takt")
    while not stop:
        messergebnis = os.popen("vcgencmd measure_temp").readline()
        temperatur = float((messergebnis.replace("temp=","").replace("'C\n","")))
        if temperatur >= temp_max:
            temp_max = temperatur
        if temperatur <= temp_min:
            temp_min = temperatur
        messergebnis = os.popen("vcgencmd measure_volts").readline()
        spannung = float((messergebnis.replace("volt=","").replace("V\n","")))
        messergebnis = os.popen("vcgencmd measure_clock arm").readline()
        freq = (messergebnis.replace("frequency(48)=","").replace("\n",""))
        frequenz = int(int(freq) / 1000000)
        ausgabe = "   {0:8s}  "+c.yellow+"{1:4.1f}'C"+c.reset+"  " +c.lightblue+ \
                  "{2:4.1f}'C"+c.reset+"  "+c.red+"{3:4.1f}'C"+c.reset+"   " + \
                  "{4:6.4f}V  {5:4d}MHz\r"
        print(ausgabe.format(aktuelle_uhrzeit(),temperatur,temp_min, \
              temp_max,spannung,frequenz),sep="",end="")
        sleep(messzyklus) #Sekundenintervall der Sensorenabfrage
    print("\nMessung beendet:", aktuelle_uhrzeit(),"\n")
    return()
    
def _main():
    global stop
    try:
        show_header(G_HEADER_1, G_HEADER_2, __file__, G_OS)
        cmd = "vcgencmd"
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if p.returncode == 0:
            stop = False
            sensoren_thread = threading.Thread(target=sensoren)
            sensoren_thread.start()
            while True:
                sleep(0.1)
                char = getch()
                if char == 'q':
                    stop = True
                    sleep(0.5)
                    break
                char = ""
        else:
            print("\n", c.lightred, "Error: Funktion \'vcgencmd\' ", \
                  "im Betriebssystem nicht vorhanden", c.reset, "\n", sep="")
    except(KeyboardInterrupt, SystemExit):
        stop = True

if __name__ == "__main__":
    _main()