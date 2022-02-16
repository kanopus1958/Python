#!/usr/bin/env python3

# Programm     : reiskorn.py
# Version      : 1.01
# SW-Stand     : 12.02.2022
# Autor        : Rolf Weiss
# Beschreibung : Reiskorn Beispiel in Python
G_OS = ('Raspbian','Debian','Windows') 
G_HEADER_1 = '# Reiskorn   (Python-Beispiel)'
G_HEADER_2 = '                             #'

from rwm_mod01 import show_header

def _main():
    show_header(G_HEADER_1, G_HEADER_2, __file__, G_OS)
    summe = 0
    for feld in range(64):
        reiskorn = 2**feld
        summe += reiskorn
        print(f"{feld+1:>2d}. Feld enthält {reiskorn:>25,d} Reiskörner.   Insgesamt nun {summe:>26,d} Reiskörner")
    print()

if __name__ == "__main__":
    _main()