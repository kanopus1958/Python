#!/usr/bin/env python3

# Programm     : test_tastatur.py
# Version      : 1.01
# SW-Stand     : 17.02.2022
# Autor        : Kanopus1958
# Beschreibung : Tastur Beispiel in Python
G_OS = ('Raspbian','Debian') 
G_HEADER_1 = '# Test Tastatur (Python-Beispi'
G_HEADER_2 = 'el)                          #'

import sys
import platform
from rwm_mod01 import show_header
from rwm_steuerung import color as c
if platform.system() == 'Linux':
    import tty, termios

def inkey():
    fd = sys.stdin.fileno()
    while True:
        remember_attributes = termios.tcgetattr(fd)
        tty.setraw(fd)
        character = sys.stdin.read(1) # wir lesen nur einzelne zeichen
        termios.tcsetattr(fd, termios.TCSADRAIN, remember_attributes)
        if character == 'q':
            break
        if character != '\x1b' and character != '[': # x1b is ESC
            sys.stdout.write(character)
            sys.stdout.flush()
            # print(character)
            
def _main():
    show_header(G_HEADER_1, G_HEADER_2, __file__, G_OS)
    print("\nTasteninput gestartet (Beenden mit 'q')\n")
    inkey()
    print()
    print("\nTasteninput gestoppt\n")

if __name__ == "__main__":
    _main()