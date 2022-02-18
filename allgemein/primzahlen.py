#!/usr/bin/env python3

# Programm     : primzahlen.py
# Version      : 1.01
# SW-Stand     : 17.02.2022
# Autor        : Kanopus1958
# Beschreibung : Berechnung von Primzahlen

from time import time
from rwm_steuerung import color as c, position as p
from rwm_mod01 import show_header
import sys

G_OS = ('Raspbian', 'Debian', 'Windows')
G_HEADER_1 = '# Primzahlenberechnung (mit St'
G_HEADER_2 = 'art- und Endewert)           #'


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
        for a in range(n, m+1):
            prim = True
            for b in range(2, a-1):
                c_wert = a % b
                if (c_wert == 0):
                    prim = False
                    break
            if prim:
                t2 = time()
                dt = (t2 - t0)
                stunde = int(dt / 3600)
                minute = int((dt - 3600 * stunde) / 60)
                sekunde = int(dt - 60 * minute - 3600 * stunde)
                i += 1
                r = a - a1
                if (a1 == 0):
                    r = 0
                prozent = (100 * i) / (a + 1 - n)
                print(f"{i:6d}. PZ={a:10d}  Delta={r:5d}  \
                      {prozent:7.3f}%  Zeit ",
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
