#!/usr/bin/env python3

# Programm     : code_template.py
# Version      : 1.00
# SW-Stand     : 20.02.2022
# Autor        : Kanopus1958
# Beschreibung : Test mit mehreren Prozessen

import sys
import signal
import os
from time import sleep
from multiprocessing import Process, Pipe, Lock, \
    active_children, current_process
from multiprocessing.connection import wait
from rwm_mod01 import show_header, aktuelle_uhrzeit, getkey
from rwm_steuerung import color as c, key_stroke as k, position as pos

G_OS = ('Raspbian', 'Debian', 'Windows')
G_HEADER_1 = '# Test mit mehreren Prozessen '
G_HEADER_2 = '                             #'


def sigint_handler(signal, frame):
    sleep(2.0)
    procs = active_children()
    if procs:
        # print(f'Noch verbliebene Prozesse\n{procs}')
        for p in procs:
            p.terminate()
            print(f'{c.lightred}CTRL-C empfangen{c.reset}')
    print(f'{aktuelle_uhrzeit()} Hauptprogramm beendet')
    sys.exit(True)


signal.signal(signal.SIGINT, sigint_handler)


def modus_aus_taste(key):
    tasten_valid = {'q': 'STOP',
                    'x': 'STOP',
                    k.LEFT: 'LEFT',
                    k.RIGHT: 'RIGHT',
                    k.UP: 'UP',
                    k.DOWN: 'DOWN'
                    }
    try:
        return tasten_valid[key]
    except KeyError:
        return 'INVALID_KEY'


def proc_00(conn, lock):
    print(f'{c.yellow}Sub-Prozess gestartet: '
          f'{sys._getframe().f_code.co_name}'
          f' ({os.getpid()}){c.reset}')
    while True:
        modus = modus_aus_taste(getkey())
        if modus != 'INVALID_KEY':
            msg = (current_process().name, modus)
            # print(f'{c.yellow}{msg}{c.reset}')
            conn.send(msg)
            if modus == 'STOP':
                break
    sleep(0.2)
    print(f'{c.yellow}Sub-Prozess beendet: '
          f'{sys._getframe().f_code.co_name}'
          f' ({os.getpid()}){c.reset}')


def proc_01(conn, lock):
    print(f'{c.lightgreen}Sub-Prozess gestartet: '
          f'{sys._getframe().f_code.co_name}'
          f' ({os.getpid()}){c.reset}')
    while True:
        if conn.poll():
            try:
                msg = conn.recv()
                if msg[0] == 'MAIN':
                    if msg[1] == 'STOP':
                        break
            except (EOFError):
                continue
    sleep(0.2)
    print(f'{c.lightgreen}Sub-Prozess beendet: '
          f'{sys._getframe().f_code.co_name}'
          f' ({os.getpid()}){c.reset}')


def proc_02(conn, lock):
    print(f'{c.lightblue}Sub-Prozess gestartet: '
          f'{sys._getframe().f_code.co_name}'
          f' ({os.getpid()}){c.reset}')
    while True:
        if conn.poll():
            try:
                msg = conn.recv()
                if msg[0] == 'MAIN':
                    if msg[1] == 'STOP':
                        break
            except (EOFError):
                continue
    sleep(0.2)
    print(f'{c.lightblue}Sub-Prozess beendet: '
          f'{sys._getframe().f_code.co_name}'
          f' ({os.getpid()}){c.reset}')


def _main():
    show_header(G_HEADER_1, G_HEADER_2, __file__, G_OS)
    print(f'{aktuelle_uhrzeit()} Hauptprogramm gestartet')
    # Der erste Prozess MUSS ZWINGEND das
    # Programm zur Tastaturbehandlung sein
    prozesse = (('P00', 'Tasten einlesen'),
                ('P01', 'Informationen anzeigen'),
                ('P02', 'Allgemeiner Prozess', 'target_proc_02')
                )
    pl = {}
    n = 0
    lock = Lock()
    for proz in prozesse:
        r, w = Pipe()
        if n == 0:
            p = Process(target=proc_00, name=proz[0], args=(w, lock))
        elif n == 1:
            p = Process(target=proc_01, name=proz[0], args=(w, lock))
        elif n == 2:
            p = Process(target=proc_02, name=proz[0], args=(w, lock))
        else:
            print(f'\n{c.lightred}Programmabbruch : Fehler bei '
                  f'den Prozess-Definitionen{c.reset}\n')
        pl[proz[0]] = {'Bez': proz[1], 'PID': p, 'Conn': r}
        p.start()
        w.close()
        sleep(0.5)
        n += 1
    # print(pl)
    # sleep(10.0)
    readers = [details['Conn'] for proc, details in pl.items()]
    # print(readers)
    while True:
        for r in wait(readers):
            try:
                msg = r.recv()
            except EOFError:
                readers.remove(r)
            else:
                print(msg)
        if msg[0] == prozesse[0][0]:
            if msg[1] == 'STOP':
                msg = ['MAIN', 'STOP']
                for proc, details in pl.items():
                    details['Conn'].send(msg)
                break
        sleep(0.1)
    sleep(1.0)
    for proc, details in pl.items():
        # details['PID'].terminate()
        details['PID'].join()

    sleep(1.0)
    procs = active_children()
    if procs:
        print(f'Noch verbliebene Prozesse\n{procs}')
        for p in procs:
            print(p.name)
            p.terminate()
        procs = active_children()
        print(procs)
    print(f'{aktuelle_uhrzeit()} Hauptprogramm beendet\n')


if __name__ == "__main__":
    _main()
