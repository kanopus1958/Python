#!/usr/bin/env python3

# Programm     : test_eingabe.py
# Version      : 1.00
# SW-Stand     : 14.02.2022
# Autor        : Rolf Weiss
# Beschreibung : Test von Eingabe- und Tastenüberwachung
G_OS = ('Raspbian','Debian','Windows') 
G_HEADER_1 = '# Test Eingabe-/Tasten-Funktio'
G_HEADER_2 = 'nen   (Stop q/CTRL_C/CTRL_Z) #'

import platform
from rwm_steuerung import color as c, key_stroke as k
from rwm_mod01 import show_header, getch
from time import sleep

def _main():
    try:
        show_header(G_HEADER_1, G_HEADER_2, __file__, G_OS)
        print('Start des Tests')
        while True:
            sleep(0.1)
            char = getch()
            print('Eingabe-/Tastendruck empfangen : <', char, '>', sep='')
            if char == 'q' or char == k.CTRL_C or char == k.CTRL_Z:
                print('Stop-Kriterium empfangen : ', char)
                sleep(1.0)
                break
            eingabe = ""
        print('Ende des Tests\n')
    except(KeyboardInterrupt, SystemExit):
        sleep(1.0)
        print(c.lightred, p.up)
        print(3*" ", "\n!!! Programm abgebrochen !!!\n", c.reset)

if __name__ == "__main__":
    _main()