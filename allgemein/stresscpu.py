#!/usr/bin/env python3

# Programm     : stresscpu.py
# Version      : 1.03
# SW-Stand     : 17.02.2022
# Autor        : Kanopus1958
# Beschreibung : Anzeige von System Informationen

import psutil
import subprocess
import threading
from multiprocessing import Process, active_children, cpu_count, Pipe
from time import sleep
from rwm_mod01 import show_header, aktuelle_uhrzeit, aktuelles_datum, getch
from rwm_steuerung import color as c, position as p, key_stroke as k
import platform
import os

G_OS = ('Raspbian', 'Debian', 'Windows')
G_HEADER_1 = '# Stresstest Rechner CPUs     '
G_HEADER_2 = '                (Stop mit q) #'

# ----------------------------------------------------------------------------
# Globale Konstanten GC_<name> für alle Funktionen und Theads
GC_fib = 50
GC_max_proc = 10
# ----------------------------------------------------------------------------


def show_systemumgebung():
    devicetype = "unknown"
    ver_distribution = "unknown"
    ver_kernel = "unknown"
    cpu_anz = -1
    cmd = "cat /sys/firmware/devicetree/base/model"
    x = subprocess.run(cmd, shell=True,
                       capture_output=True, text=True)
    if x.returncode == 0:
        devicetype = x.stdout[:-1].replace("\n", "").strip()
    else:
        cmd = "grep -m 1 'model name' /proc/cpuinfo"
        x = subprocess.run(cmd, shell=True,
                           capture_output=True, text=True)
        if x.returncode == 0:
            devicetype = x.stdout[x.stdout.find(
                ":")+2:x.stdout.find(",")].replace("\n", "").strip()
    cmd = "lsb_release -d"
    x = subprocess.run(cmd, shell=True,
                       capture_output=True, text=True)
    if x.returncode == 0:
        ver_distribution = x.stdout.replace(
            "Description:", "").replace("\n", "").strip()
    cmd = "uname -r"
    x = subprocess.run(cmd, shell=True,
                       capture_output=True, text=True)
    if x.returncode == 0:
        ver_kernel = x.stdout.replace("\n", "").strip()
    cpu_anz = cpu_count()
    print(c.white, end="")
    print(f"# Rechnertyp   : {devicetype:38s}",
          2*" ", "#\r")
    print(f"# Distribution : {ver_distribution:38s}",
          2*" ", "#\r")
    print(f"# Kernel       : {ver_kernel:38s}",
          2*" ", "#\r")
    print(f"# CPU-Anzahl   : {cpu_anz:1d}",
          39*" ", "#\r")
    print(60*"#", "\r")
    print(c.reset, end="")
    return


def tasten_thread(conn):
    conn.send(threading.get_ident())
    sleep(0.5)
    while not stop:
        char = getch()
        if char == 'q' or char == 'x' or char == '+' or char == '-':
            conn.send(char)
            sleep(0.2)
        if char == 'q':
            break
        char = ""
    conn.close()
    return


def anzeige_thread(conn):
    conn.send(threading.get_ident())
    conn.close()
    N_Messzyklus = 1.0
    N_Druck = 12  # Maximale Anzahl von druckbaren Ausgabezeilen
    N_Leer = 12
    sleep(0.1)
    print("Stresstest gestartet  : ", aktuelles_datum(),
          " ", aktuelle_uhrzeit(), sep="", end="\n\r")
    print("(\'+\' = Add Proc , "
          "\'-\' = Del Proc , \'x\' = Stop all Proc)",
          sep="", end="\n\r")
    zyklus = 0
    anzeige_komplett = False
    while not stop or not anzeige_komplett:
        anz_z = N_Druck
        zyklus += 1
        cpu_load = psutil.cpu_percent(N_Messzyklus)
        freq = psutil.cpu_freq()
        tcpu_exist = False
        tgpu_exist = False
        if platform.system() == 'Linux':
            temp = psutil.sensors_temperatures()
            for name, entries in temp.items():
                if name == "k10temp" or name == "cpu_thermal":
                    tcpu_exist = True
                    for entry in entries:
                        tcpu = entry.current
                elif name == "amdgpu":
                    tgpu_exist = True
                    for entry in entries:
                        tgpu = entry.current
        print(60*"*", "\r")
        print(c.yellow, end="")
        print(f"* PID Main", 4*" ", f"ID Tasten-Th", 4*" ",
              f"ID Anzeige-Th", 16*" ", "*\r", sep="")
        print(f"* {pids[0]:8s}", 6*" ", f"{pids[1][len(pids[1])-10:]:10s}",
              7*" ", f"{pids[2][len(pids[2])-10:]:10s}", 16*" ", "*\r", sep="")
        print(f"*", 58*" ", "*\r", sep="")
        print(f"* Messzeit", 4*" ", f"Testzyklus", 6*" ",
              f"Prozesse", 21*" ", "*\r", sep="")
        print(f"* {aktuelle_uhrzeit():8s}", 6*" ", f"{zyklus:8d}",
              10*" ", c.pink, f"{anz_procs:4d}",
              c.yellow, 21*" ", "*\r", sep="")
        print(f"*", 58*" ", "*\r", sep="")
        print(f"* CPU-Last", 4*" ", c.lightcyan, f"{cpu_load:8.1f} %",
              c.yellow, 35*" ", "*\r", sep="")
        if tcpu_exist:
            print(f"* CPU-Temp", 4*" ", c.lightcyan, f"{tcpu:8.1f}'C",
                  c.yellow, 35*" ", "*\r", sep="")
        else:
            anz_z -= 1
        if tgpu_exist:
            print(f"* GPU-Temp", 4*" ", c.lightcyan, f"{tgpu:8.1f}'C",
                  c.yellow, 35*" ", "*\r", sep="")
        else:
            anz_z -= 1
        print(f"* CPU-Freq", 4*" ", c.lightcyan, f"{freq.current:8.1f} MHz",
              c.yellow, 33*" ", "*\r", sep="")
        if len(p_loop) > 0:
            print(f"*", 58*" ", "*\r", sep="")
            print(f"* Proc-Nr", 7*" ", f"Proc-PID", 8*" ",
                  f"Status", 21*" ", "*\r", sep="")
        else:
            anz_z -= 2
        for n in range(len(p_loop)):
            anz_z += 1
            if p_loop[n].is_alive():
                status = "alive"
                print(f"*      {n+1:02d}", 7*" ", f"{p_loop[n].ident:8d}",
                      9*" ", c.green, status, c.yellow, 21*" ", "*\r", sep="")
            else:
                status = " dead"
                print(f"*      {n+1:02d}", 7*" ", f"{p_loop[n].ident:8d}",
                      9*" ", c.lightred, status, c.yellow, 21*" ", "*\r",
                      sep="")
        print(c.reset, end="")
        print(60*"*", "\r")
        for n in range(N_Leer):
            print(f" ", 58*" ", " \r", sep="")
            # print("\n", sep="")
            anz_z += 1
        print((anz_z+2)*p.up, end="")
        sleep(0.01)
        anzeige_komplett = True
    print((anz_z+2-N_Leer)*p.down, end="")
    print("Stresstest beendet    : ", aktuelles_datum(),
          " ", aktuelle_uhrzeit(), sep="", end="\n\r")
    print()
    return


def proc_change(modifier):
    global anz_procs
    if modifier == "+":
        if len(p_loop) < GC_max_proc:
            proc = Process(target=loop)
            p_loop.append(proc)
            proc.start()
            anz_procs += 1
    elif modifier == "-":
        if len(p_loop) > 0:
            proc = p_loop.pop()
            proc.terminate()
        anz_procs -= 1
    if anz_procs < 0:
        anz_procs = 0
    return


def fib(n):
    if n < 2:
        return 1
    else:
        return fib(n - 1) + fib(n - 2)


def loop():
    # print("Prozess gestartet : ", os.getpid())
    while True:
        fib(GC_fib)
    return


def _main():
    global stop
    global pids
    global anz_procs
    global p_loop
    try:
        show_header(G_HEADER_1, G_HEADER_2, __file__, G_OS)
        psutil.cpu_percent(1.0)
        show_systemumgebung()
        stop = False
        anz_procs = 0
        pids = []  # [0]=Mainprogramm, [1]=Tasten-Thread, [2]=Anzeige-Thread
        p_loop = []
        tasten_parent_conn, tasten_child_conn = Pipe()
        anzeige_parent_conn, anzeige_child_conn = Pipe()
        th_tasten = threading.Thread(target=tasten_thread,
                                     args=(tasten_child_conn,))
        th_anzeige = threading.Thread(target=anzeige_thread,
                                      args=(anzeige_child_conn,))
        th_tasten.start()
        th_anzeige.start()
        pids.append(str(os.getpid()))
        pids.append(str(tasten_parent_conn.recv()))
        pids.append(str(anzeige_parent_conn.recv()))
        for n in range(cpu_count()):
            proc_change('+')
        while True:
            sleep(0.5)
            try:
                char = tasten_parent_conn.recv()
            except EOFError:
                continue
            if char == 'q':
                sleep(0.5)
                break
            if char == '+' or char == '-':
                proc_change(char)
                sleep(0.5)
            if char == 'x':
                sleep(0.1)
                procs = active_children()
                for procs in procs:
                    proc_change('-')
            char = ""
        stop = True
        procs = active_children()
        for proc in procs:
            proc.terminate()
        sleep(0.1)
        th_anzeige.join()
        th_tasten.join()
    except(KeyboardInterrupt, SystemExit):
        sleep(1.0)
        stop = True
        print(c.lightred, p.up)
        print(3*" ", "\n!!! Programm abgebrochen !!!\n", c.reset)


if __name__ == "__main__":
    _main()
