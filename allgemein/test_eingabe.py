#!/usr/bin/env python3

# Programm     : test_eingabe.py
# Version      : 1.00
# SW-Stand     : 17.02.2022
# Autor        : Kanopus1958
# Beschreibung : Test von Eingabe- und Tastenüberwachung

from rwm_mod01 import show_header, getkey
from rwm_steuerung import color as c, key_stroke as k, position as p
from time import sleep
import signal

G_OS = ('Raspbian', 'Debian')
G_HEADER_1 = '# Test Eingabe-/Tasten-Funktio'
G_HEADER_2 = 'nen        (Stop q/x/CTRL_Z) #'


def sigint_handler(signal, frame):
    print(f'{c.yellow}CTRL-C führt nicht zum Abbruch{c.reset}')


signal.signal(signal.SIGINT, sigint_handler)


def _main():
    try:
        show_header(G_HEADER_1, G_HEADER_2, __file__, G_OS)
        abbruch_tasten = ('q', 'x', k.CTRL_Z)
        print('Start des Tests')
        while True:
            try:
                key = getkey()
                print(f'{c.yellow}{len(key)}{c.reset} : ', end='')
                k_str = list(n for n in key)
                k_hex = list(n.encode('utf-8').hex() for n in k_str)
                k_esc = ""
                for n in k_hex:
                    k_esc += '\\x'+n
                print(f'{k_str} --> ', end='')
                # print(k_hex)
                print(f"'{k_esc}'")
                # print(f'Eingabe-/Tastendruck empfangen : <{key}>')
                if key in abbruch_tasten:
                    print(f'Stop-Kriterium empfangen : {k_esc}')
                    break
                # key = ""
            except (TypeError):
                print(f'{c.lightred}Invalid key mit {type(key)}{c.reset}')
                continue
        print('Ende des Tests\n')
    except(KeyboardInterrupt):
        sleep(1.0)
        print(c.lightred, p.up)
        print(3*" ", "\n!!! Programm abgebrochen mit CTRL-C !!!\n", c.reset)


if __name__ == "__main__":
    _main()
