#!/usr/bin/env python3

# Programm     : turmhanoi.py
# Version      : 1.00
# SW-Stand     : 17.02.2022
# Autor        : Kanopus1958
# Beschreibung : Turm Hanoi Beispiel in Python
from rwm_mod01 import show_header
G_OS = ('Raspbian', 'Debian', 'Windows')
G_HEADER_1 = '# Turm Hanoi (Python-Beispiel)'
G_HEADER_2 = '                             #'


def hanoi(n, source, helper, target):
    if n > 0:
        # move tower of size n - 1 to helper:
        hanoi(n - 1, source, target, helper)
        # move disk from source peg to target peg
        if source:
            target.append(source.pop())
        # move tower of size n-1 from helper to target
        hanoi(n - 1, helper, source, target)


def _main():
    show_header(G_HEADER_1, G_HEADER_2, __file__, G_OS)
    source = [4, 3, 2, 1]
    target = []
    helper = []
    print(source, helper, target)
    hanoi(len(source), source, helper, target)
    print(source, helper, target)
    print()


if __name__ == "__main__":
    _main()
