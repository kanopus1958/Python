#!/usr/bin/env python3

# Programm     : test_test.py
# Version      : 1.01
# SW-Stand     : 17.02.2022
# Autor        : Kanopus1958
# Beschreibung : Allgemeines Testprogramm für Python

from itertools import count
import threading
from multiprocessing import Process
import subprocess
import psutil
from time import sleep
from rwm_mod01 import show_header, aktuelle_uhrzeit
from rwm_steuerung import color as c, position as p
import platform
import os
import sys

G_OS = ('Raspbian', 'Debian', 'Windows')
G_HEADER_1 = '# Test von allerlei Python Fun'
G_HEADER_2 = 'ktionen                      #'


def test_01():
    print(c.yellow, f"Test Funktion : ",
          f"{sys._getframe(  ).f_code.co_name}", c.reset, sep="")
    N_Zyklus = 3
    N_Messzyklus = 1.0
    N_Druck = 11

    for zyklus in range(1, N_Zyklus+1):
        cpu_count = psutil.cpu_count()
        cpu_load = psutil.cpu_percent(N_Messzyklus)
        mem = psutil.virtual_memory()
        temp = psutil.sensors_temperatures()
        freq = psutil.cpu_freq()
        for name, entries in temp.items():
            if name == "k10temp" or name == "cpu_thermal":
                for entry in entries:
                    tcpu = entry.current
        print(f"measure time  : {aktuelle_uhrzeit():8s}")
        print(f"test cycle    : {zyklus:8d} von {N_Zyklus:3d}")
        print(f"cpu count     : {cpu_count:8d} Stk")
        print(f"cpu load      : {cpu_load:8.1f} %")
        print(f"cpu temp      : {tcpu:8.1f} 'C")
        print(f"freq current  : {freq.current:8.1f} MHz")
        print(f"freq min      : {freq.min:8.1f} MHz")
        print(f"freq max      : {freq.max:8.1f} MHz")
        print(f"mem percent   : {mem.percent:8.1f} %")
        print(f"mem used      : {mem.used/1024/1024:8.1f} MB")
        print(f"mem total     : {mem.total/1024/1024:8.1f} MB")
        print((N_Druck+1)*p.up)
        sleep(0.1)
    print((N_Druck-1)*p.down)
    print(c.yellow, 60*"-", c.reset, sep="")
    return


def test_02():
    print(c.yellow, f"Test Funktion : ",
          f"{sys._getframe(  ).f_code.co_name}", c.reset, sep="")
    ##########
    cmd = "vcgencmd measure_volts"
    voltage = subprocess.run(cmd, shell=True,
                             capture_output=True, text=True)
    if voltage.returncode == 0:
        spannung = float(voltage.stdout.replace(
            "volt=", "").replace("V\n", "").strip())
        print(f"Spannung      : {spannung:6.4f} V")
    else:
        print(c.lightred, f"Errorcode {voltage.returncode:3d} : ",
              f"Befehl '{cmd:s}' unbekannt", c.reset, sep="")
    ##########
    cmd = "sudo iwgetid -r"
    x = subprocess.run(cmd, shell=True,
                       capture_output=True, text=True)
    if x.returncode == 0:
        ergebnis = x.stdout.replace("\n", "").strip()
        print(f"WLAN-SSID     : {ergebnis:s}")
    else:
        print(c.lightred, f"Errorcode {x.returncode:3d} : ",
              f"Befehl '{cmd:s}' unbekannt", c.reset, sep="")
    ##########
    cmd = "cat /sys/firmware/devicetree/base/model"
    x = subprocess.run(cmd, shell=True,
                       capture_output=True, text=True)
    if x.returncode == 0:
        ergebnis = x.stdout.replace("\n", "").strip()
        print(f"Rechnertyp    : {ergebnis:s}")
    else:
        cmd = "grep -m 1 'model name' /proc/cpuinfo"
        x = subprocess.run(cmd, shell=True,
                           capture_output=True, text=True)
        if x.returncode == 0:
            ergebnis = x.stdout[x.stdout.find(
                ":")+2:].replace("\n", "").strip()
            print(f"Rechnertyp    : {ergebnis:s}")
        else:
            print(c.lightred, f"Errorcode {x.returncode:3d} : ",
                  f"Befehl '{cmd:s}' unbekannt", c.reset, sep="")
    ##########
    cmd = "lsb_release -d"
    x = subprocess.run(cmd, shell=True,
                       capture_output=True, text=True)
    if x.returncode == 0:
        ergebnis = x.stdout.replace(
            "Description:", "").replace("\n", "").strip()
        print(f"Distribution  : {ergebnis:s}")
    else:
        print(c.lightred, f"Errorcode {x.returncode:3d} : ",
              f"Befehl '{cmd:s}' unbekannt", c.reset, sep="")
    ##########
    cmd = "uname -r"
    x = subprocess.run(cmd, shell=True,
                       capture_output=True, text=True)
    if x.returncode == 0:
        ergebnis = x.stdout.replace("\n", "").strip()
        print(f"Kernel        : {ergebnis:s}")
    else:
        print(c.lightred, f"Errorcode {x.returncode:3d} : ",
              f"Befehl '{cmd:s}' unbekannt", c.reset, sep="")
    ##########
    cmd = "df -h -t ext4 --output='size','used','avail','pcent'"
    x = subprocess.run(cmd, shell=True,
                       capture_output=True, text=True)
    if x.returncode == 0:
        tmp = x.stdout.split("\n")
        ergebnis = tmp[1].replace("\n", "").strip()
        print(f"System-Disc   : {ergebnis:s}")
    else:
        print(c.lightred, f"Errorcode {x.returncode:3d} : ",
              f"Befehl '{cmd:s}' unbekannt", c.reset, sep="")
    ##########
    print(c.yellow, 60*"-", c.reset, sep="")
    return


def test_03():
    print(c.yellow, f"Test Funktion : ",
          f"{sys._getframe(  ).f_code.co_name}", c.reset, sep="")
    hosts = ['Robot-01', 'Merkur', 'Wega']
    for host in hosts:
        cmd = "ping -c1 "+host
        x = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, text=True)
        print(f"{host:15s}: Errorcode={x.returncode:3d}", sep="")
        print(type(x.stdout))
        print(x.stdout)
    print(c.yellow, 60*"-", c.reset, sep="")
    return


def test_04():
    print(c.yellow, f"Test Funktion : ",
          f"{sys._getframe(  ).f_code.co_name}", c.reset, sep="")
    for m in range(6):
        for n in range(1, 11):
            if n == 10:
                n = 0
            print(n, end="")
    print("\r", sep="")
    for m in range(5):
        print('\r', 60*" ", '\r', sep="", end="")
        for n in range(1, 31):
            print(f'*\r', n*p.right, sep="", end="")
            sleep(0.05)
    print("\r\n", sep="", end="")
    print(c.yellow, 60*"-", c.reset, sep="")
    return


def persistence(n, inner_pers):
    inner_pers += 1
    if len(str(n)) == 1:
        return inner_pers
    digits = [int(i) for i in str(n)]
    result = 1
    for j in digits:
        result *= j
    print(f"           {result:20d}")
    return persistence(result, inner_pers)


def test_05():
    print(c.yellow, f"Test Funktion : ",
          f"{sys._getframe(  ).f_code.co_name}", c.reset, sep="")
    zahl = int(input("Ganz-Zahl eingeben : "))
    print(f"         Zahl : {zahl:15d}")
    pers = persistence(zahl, -1)
    print(f"Persistence von {zahl:15d} ={pers:4d}")
    print(c.yellow, 60*"-", c.reset, sep="")
    return


def f1(name1, name2):
    for n in range(10):
        print(f"Hallo {name1} {name2}")


def test_06():
    print(c.yellow, f"Test Funktion : ",
          f"{sys._getframe(  ).f_code.co_name}", c.reset, sep="")
    n1 = 'Kanopus'
    n2 = '1958'
    proc = Process(target=f1, args=(n1, n2, ))
    proc.start()
    proc.join()
    print(c.yellow, 60*"-", c.reset, sep="")
    return


def worker():
    print("worker gestartet")
    for i in count():
        print(i)
        sleep(0.5)
    print("worker gestoppt")
    return


def controller():
    print("controller gestartet")
    th_w = threading.Thread(target=worker, daemon=True)
    th_w.start()
    for n in range(10):
        sleep(1.0)
    print("controller gestoppt")
    return


def test_07():
    print(c.yellow, f"Test Funktion : ",
          f"{sys._getframe(  ).f_code.co_name}", c.reset, sep="")
    print("Hauptprogramm gestartet mit PID ", os.getpid())
    th_c = threading.Thread(target=controller)
    th_c.start()

    th_c.join()
    for n in range(5):
        print(os.getpid(), " schläft")
        sleep(1)
    print("Hauptprogramm gestoppt mit PID ", os.getpid())
    print(c.yellow, 60*"-", c.reset, sep="")
    return


def _main():
    try:
        show_header(G_HEADER_1, G_HEADER_2, __file__, G_OS)
        # test_01()
        # test_02()
        # test_03()
        # test_04()
        # test_05()
        # test_06()
        test_07()
        sleep(0.5)
    except(KeyboardInterrupt, SystemExit):
        print()
        show_header(G_HEADER_1, G_HEADER_2, __file__)
        sleep(1.0)
        print(c.lightred, p.up)
        print(
              3*" ", "\n!!! Abbruch mit Ctrl-C (SIGINT) "
              "oder CTRL-Z (SIGTSTP) !!!\n", c.reset)


if __name__ == "__main__":
    _main()
