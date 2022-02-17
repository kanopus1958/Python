#!/usr/bin/env python3

# Programm     : pystress.py
# Version      : 1.00
# SW-Stand     : 17.02.2022
# Autor        : Kanopus1958
# Beschreibung : Stresstest für alle CPUs (Source von GitHub)
G_OS = ('Raspbian','Debian','Windows') 
G_HEADER_1 = '# Stresstest Rechner CPUs     '
G_HEADER_2 = '        (Abbruch mit CTRL-C) #'

# ----------------------------------------------------------------------------
# Globale Konstanten GC_<name> für alle Funktionen und Theads
GC_fib_n = 100
GC_default_time = 60
# ----------------------------------------------------------------------------

import os
import sys
from rwm_steuerung import color as c, position as p
from rwm_mod01 import show_header, aktuelle_uhrzeit, aktuelles_datum
from multiprocessing import Process, active_children, cpu_count, Pipe
from time import sleep

try:
    DEFAULT_CPU = cpu_count()
    # print("CPU-Anzahl = ", DEFAULT_CPU)
except NotImplementedError:
    DEFAULT_CPU = 1
    print("cpu_count not implemented")

def loop(conn):
    proc_info = os.getpid()
    conn.send(proc_info)
    conn.close()
    while True:
        fib(GC_fib_n)
    return

def fib(n):
    if n < 2:
        return 1
    else:
        return fib(n - 1) + fib(n - 2)

def get_args():
    exec_time = GC_default_time
    proc_num = DEFAULT_CPU
    if len(sys.argv) > 3:
        raise
    if len(sys.argv) == 2:
        exec_time = int(sys.argv[1])
    if len(sys.argv) == 3:
        exec_time = int(sys.argv[1])
        proc_num = int(sys.argv[2])
    if proc_num > 10:
        proc_num = 10
    if proc_num <  1:
        proc_num =  1
    return exec_time, proc_num

def _main():
    try:
        try:
            show_header(G_HEADER_1, G_HEADER_2, __file__, G_OS)
            exec_time, proc_num = get_args()
        except:
            msg = "Usage: pystress [exec_time] [proc_num]\n"
            sys.stderr.write(msg)
            sys.exit(1)
        procs = []
        conns = []
        pids  = []
        for i in range(proc_num):
            parent_conn, child_conn = Pipe()
            proc = Process(target=loop, args=(child_conn,))
            proc.start()
            procs.append(proc)
            conns.append(parent_conn)
        for conn in conns:
            try:
                pids.append(conn.recv())
            except EOFError:
                continue
        print("Stresstest gestartet  : ", aktuelles_datum(), \
              " ", aktuelle_uhrzeit(), sep="", end="\n\r")
        print(60*"*", sep="")
        print(f"* Anzahl Prozesse :{proc_num:6d}", 34*" ", "*",sep="")
        print(f"*            PIDs :", sep="", end="")
        for n in range(len(pids)):
            if n < 5:
                print(f"{pids[n]:6d}  ", sep="", end="")
        print((4-n)*"        ", "*", sep="")
        if len(pids) > 5:
            print(f"*                 :", sep="", end="")
            for n in range(len(pids)):
                if n >= 5:
                    print(f"{pids[n]:6d}  ", sep="", end="")
            print((4-n+5)*"        ", "*", sep="")
        print(f"* Dauer (Sek.)    :{exec_time:6d}", 34*" ", "*",sep="")
        print("*", 58*" ", "*", sep="")
        print("*", 58*" ", "*", sep="")
        print("*", 58*" ", "*", sep="")
        print(60*"*", sep="")

        print(3*p.up, sep="", end="")
        for n in range(1, 41):
            print(10*p.right, sep="", end="")
            print(c.yellow, f'>\r', n*p.right, c.reset, sep="", end="")
            sleep(exec_time/40)

        for proc in procs:
            proc.terminate()
        print(3*p.down, sep="", end="")
        print("Stresstest gestoppt   : ", aktuelles_datum(), \
              " ", aktuelle_uhrzeit(), sep="", end="\n\r")
    except(KeyboardInterrupt, SystemExit):
        procs = active_children()
        for proc in procs:
            proc.terminate()
        print("\r  \r", sep="", end="")
        print(c.lightred, 2*p.down)
        print(3*" ", "\n!!! Programm abgebrochen !!!\n", c.reset)
        sys.exit(False)

if __name__ == "__main__":
    _main()