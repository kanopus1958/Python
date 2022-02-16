#!/usr/bin/env python3

# Programm     : primzahlen.py
# Version      : 1.01
# SW-Stand     : 12.06.2022
# Autor        : Rolf Weiss
# Beschreibung : Berechnung von Primzahlen
G_OS = ('Raspbian','Debian','Windows') 
G_HEADER_1 = '# Primzahlenberechnung (mit St'
G_HEADER_2 = 'art- und Endewert)           #'

import sys
from rwm_mod01 import show_header
from rwm_steuerung import color as c, position as p
from time import time

def _main():
    try:
        show_header(G_HEADER_1, G_HEADER_2, __file__, G_OS)
        n = int(input("Erste Primzahl? "))
        m = int(input("Maximale Primzahl? "))
        i = 0
        a1 = 0
        if (n <= 2):
            n = 2
        t0 = time()
        for a in range(n,m+1):
            prim = True
            for b in range(2,a-1):
                c_wert = a % b 
                if (c_wert == 0):
                    prim = False
                    break
            if (prim == True):
                t2 = time()
                dt = (t2 - t0)
                stunde = int(dt / 3600)
                minute = int((dt - 3600 * stunde) / 60)
                sekunde = int(dt - 60 * minute - 3600 * stunde)
                i += 1
                l = a - a1
                if (a1 == 0):
                    l = 0
                prozent = (100 * i) / (a + 1 - n)
                #print ("%6d"%i,". PZ= ","%10d"%a,"  Delta= ","%5d"%l,"  ", \
                #       "%3.3f"%prozent,"%","  Zeit ","%02d"%stunde,":","%02d"%minute,":","%02d"%sekunde,sep="")
                print (f"{i:6d}. PZ={a:10d}  Delta={l:5d}  {prozent:7.3f}%  Zeit ", \
                       f"{stunde:02d}:{minute:02d}:{sekunde:02d}", sep="")
                a1 = a
        print("\nPrimzahlenberechnung beendet\n")
    except(KeyboardInterrupt, SystemExit):
        print("\r \r", sep="", end="")
        print(c.lightred, p.up)
        print(3*" ", "\n!!! Programm abgebrochen !!!\n", c.reset)
        sys.exit(False)

if __name__ == "__main__":
    _main() 