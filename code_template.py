#!/usr/bin/env python3

# Programm     : code_template.py
# Version      : 1.00
# SW-Stand     : 16.02.2022
# Autor        : Kanopus1958
# Beschreibung : Code Template Datei für Python-Profamme RW

from rwm_mod01 import show_header

G_OS = ('Raspbian', 'Debian', 'Windows')
G_HEADER_1 = '# Code Template für Python-Pro'
G_HEADER_2 = 'gramme                       #'


def _main():
    show_header(G_HEADER_1, G_HEADER_2, __file__, G_OS)


if __name__ == "__main__":
    _main()
