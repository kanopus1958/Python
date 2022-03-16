#!/usr/bin/env python3

# Programm     : schildkrote.py
# Version      : 1.00
# SW-Stand     : 18.02.2022
# Autor        : Kanopus1958
# Beschreibung : Tests mit Modul turtle

import turtle as tu
from rwm_mod01 import show_header

G_OS = ('Windows')
G_HEADER_1 = '# Tests mit Modul "turtle"    '
G_HEADER_2 = '                             #'


def _main():
    show_header(G_HEADER_1, G_HEADER_2, __file__, G_OS)

    laenge = 500
    winkel = 170
    n = 0
    tu.color('red', 'yellow')
    tu.begin_fill()
    tu.setposition(-laenge/2, 0.0)
    while True:
        n += 1
        print(n, n*winkel)
        tu.forward(laenge)
        tu.left(winkel)
        if n*winkel % 360 == 0:
            break
    tu.end_fill()
    tu.done()


if __name__ == "__main__":
    _main()
