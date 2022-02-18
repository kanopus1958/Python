#!/usr/bin/env python3

# Programm     : pythagoras.py
# Version      : 1.01
# SW-Stand     : 17.02.2022
# Autor        : Kanopus1958
# Beschreibung : Berechnung von Tripeln die a^2 + b^2 = c^2 erfüllen
G_OS = ('Raspbian','Debian','Windows')
G_HEADER_1 = '# Pythagoras (Tripel die a^2 +'
G_HEADER_2 = ' b^2 = c^2 erfüllen          #'

import sys
from rwm_mod01 import show_header
from rwm_steuerung import color as c, position as p
from math import sqrt

def _main():
    show_header(G_HEADER_1, G_HEADER_2, __file__, G_OS)
    print()
    try:
        n = int(input("Erste Zahl? "))
        m = int(input("Maximale Zahl? "))
        print()
        if m <= n:
            print ("Maximale Zahl muss größer sein als erste Zahl !")
        for a_wert in range(n,m+1):
            for b_wert in range(a_wert,m):
                c_square = a_wert**2 + b_wert**2
                c_wert = int(sqrt(c_square))
                if (c_square - c_wert**2) == 0:
                    print(f"{a_wert:8d} {b_wert:8d} {c_wert:8d}", sep="")
        print()
    except(KeyboardInterrupt, SystemExit):
        print("\r \r", sep="", end="")
        print(c.lightred, p.up)
        print(3*" ", "\n!!! Programm abgebrochen !!!\n", c.reset)
        sys.exit(False)

if __name__ == "__main__":
    _main()
