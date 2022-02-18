#!/usr/bin/env python3

# Programm     : test_threads.py
# Version      : 1.01
# SW-Stand     : 17.02.2022
# Autor        : Kanopus1958
# Beschreibung : Test Threads Beispiel in Python

from random import randint
from time import sleep
import readchar as rc
import queue
import threading
from rwm_mod01 import show_header, clean_console

G_OS = ('Raspbian', 'Debian', 'Windows')
G_HEADER_1 = '# Test Threads (Python-Beispie'
G_HEADER_2 = 'l)                           #'


def steuerbefehl(key):
    if (key == rc.key.UP) or (key == "w"):
        befehl = "VOR"
    elif (key == rc.key.DOWN) or (key == "s"):
        befehl = "ZURUECK"
    elif (key == rc.key.LEFT) or (key == "a"):
        befehl = "LINKS"
    elif (key == rc.key.RIGHT) or (key == "d"):
        befehl = "RECHTS"
    elif (key == " ") or (key == "q"):
        befehl = "STOP"
    elif (key == rc.key.CTRL_C) or (key == "x"):
        befehl = "ENDE"
    else:
        befehl = "??? Unbekannter Befehl"
    return befehl

# Primzahlen ermitteln


def primzahl(n, m, ev, nr):
    i = 0
    if (n <= 2):
        n = 2
    for a in range(n, m+1):
        if ev.is_set():
            break
        prim = True
        for b in range(2, a-1):
            if ev.is_set():
                break
            c = a % b
            if (c == 0):
                prim = False
                break
        if prim:
            i += 1
            pz[nr] = a
    pz[nr] = -1


# Thread-Funktion Drucken der Egebnisse
def show(ev):
    lk = threading.Lock()
    while not ev.is_set():
        clean_console()
        lk.acquire()
        for j in range(anz_threads):
            print("Primzahl Thread {0:2d}: {1:10d}   (Start = {2:10d}   "
                  "Ende = {3:10d})\r".
                  format(j+1, pz[j], pz_start[j], pz_ende[j]))
        lk.release()
        sleep(3.0)


# Thread-Funktion Primzahlenberechnung
def tue_was(ev, nr):
    id = threading.get_ident()
    print("Start Thread {0:2d}:  {1:12d}\r".format(nr+1, id))
    n = randint(1000000, 1010000)
    m = n + 100
    pz_start[nr] = n
    pz_ende[nr] = m
    primzahl(n, m, ev, nr)
    print("Ende Thread {0:2d}:  {1:12d}\r".format(nr+1, id))
    pz_start[nr] = -1
    pz_ende[nr] = -1
    return


def getch(ev, qu):
    while not ev.is_set():
        ch = rc.readkey()
        befehl = steuerbefehl(ch)
        qu.put("Taste: "+befehl)
        if ch == 'x':
            ev.set()
        ch == ""
        sleep(0.1)


def _main():
    global anz_threads
    global pz
    global pz_start
    global pz_ende
    try:
        show_header(G_HEADER_1, G_HEADER_2, __file__, G_OS)
        anz_threads = 10
        th = []
        pz = []
        pz_start = []
        pz_ende = []
        for j in range(anz_threads):
            pz.append(0)
            pz_start.append(0)
            pz_ende.append(0)
        id = threading.get_ident()
        print("Start Hauptprogramm", id)
        ev = threading.Event()
        ev.clear()
        qu = queue.Queue()
        for j in range(anz_threads):
            t1 = threading.Thread(target=tue_was, args=(ev, j,))
            th.append(t1)
            t1.start()
            sleep(0.1)
        t2 = threading.Thread(target=show, args=(ev,))
        t2.start()
        t3 = threading.Thread(target=getch, args=(ev, qu,))
        t3.start()
        einer_laeuft_noch = True
        while not ev.is_set() and einer_laeuft_noch:
            if not qu.empty():
                print(qu.get(), "\r")
            sleep(0.01)
            einer_laeuft_noch = False
            for j in range(anz_threads):
                if th[j].is_alive():
                    einer_laeuft_noch = True
                    # print("Thread läuft noch", j+1, "\n\r")
                    break
        ev.set()
        for j in range(anz_threads):
            th[j].join()
        t2.join()
        if t3.is_alive():
            print("\nBitte beliebige Taste drücken "
                  "zum Stoppen des Programms !!!\n\r")
        t3.join()
        show_header(G_HEADER_1, G_HEADER_2, __file__, G_OS)
        print("Ende Hauptprogramm", id, "\n")
    except (KeyboardInterrupt):
        ev.set()
        sleep(1.0)
        print("Abbruch Hauptprogramm", id, "\n")


if __name__ == "__main__":
    _main()
