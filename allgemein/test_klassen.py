#!/usr/bin/env python3

# Programm     : test_klassen.py
# Version      : 1.01
# SW-Stand     : 17.02.2022
# Autor        : Kanopus1958
# Beschreibung : Klassen Beispiel in Python
G_OS = ('Raspbian','Debian','Windows') 
G_HEADER_1 = '# Test Klassen (Python-Beispie'
G_HEADER_2 = 'l)                           #'

from rwm_mod01 import show_header

class konto:
    def __init__(self ,Kontoinhaber, Kontostand=0.0):
        self.Kontoinhaber = Kontoinhaber
        self.Kontostand = Kontostand
        
    def kontostand_anzeigen(self):
        print(self.Kontostand)
        
    def einzahlen(self, betrag):
        self.Kontostand += betrag
        
def _main():
    show_header(G_HEADER_1, G_HEADER_2, __file__, G_OS)
    k1 = konto("Rolf")
    k1.kontostand_anzeigen()
    betrag = float(input("Was wollen Sie einzahlen ? : "))
    k1.einzahlen(betrag)
    k1.kontostand_anzeigen()
    print()

if __name__ == "__main__":
    _main()