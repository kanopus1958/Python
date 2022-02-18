#!/usr/bin/env python3

# Programm     : systeminfo.py
# Version      : 1.04
# SW-Stand     : 17.02.2022
# Autor        : Kanopus1958
# Beschreibung : Anzeige von System Informationen

import psutil
import subprocess
import threading
from time import sleep
from rwm_mod01 import show_header, aktuelle_uhrzeit, aktuelles_datum, getch
from rwm_steuerung import color as c, position as p, key_stroke as k
import platform

G_OS = ('Raspbian', 'Debian', 'Windows')
G_HEADER_1 = '# Monitor System Informationen'
G_HEADER_2 = '                (Stop mit q) #'

# ----------------------------------------------------------------------------
# Globale Konstanten GC_<name> für alle Funktionen und Theads
GC_messzyklus = 1.0
# ----------------------------------------------------------------------------


def show_systemumgebung():
    cmd = "sudo iwgetid -r"
    x = subprocess.run(cmd, shell=True,
                       capture_output=True, text=True)
    if x.returncode == 0:
        ssid = x.stdout.replace("\n", "").strip()
    else:
        ssid = ""
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
    cmd = "df -h -t ext4 --output='size','used','avail','pcent'"
    x = subprocess.run(cmd, shell=True,
                       capture_output=True, text=True)
    if x.returncode == 0:
        tmp = x.stdout.split("\n")
        discspace = tmp[1].replace("\n", "").rstrip()
    print(c.white, end="")
    print(f"# WLAN-SSID    : {ssid:38s}",
          2*" ", "#\r")
    print(f"# Rechnertyp   : {devicetype:38s}",
          2*" ", "#\r")
    print(f"# Distribution : {ver_distribution:38s}",
          2*" ", "#\r")
    print(f"# Kernel       : {ver_kernel:38s}",
          2*" ", "#\r")
    print("# System-Disc  : size    used  free     %",
          16*" ", "#\r")
    print(f"#               {discspace:38s}",
          3*" ", "#\r")
    print(60*"#", "\r")
    print(c.reset, end="")
    return


def anzeige_thread():
    N_Max = 100.0
    N_Min = 0.0
    N_Druck = 12  # Maximale Anzahl von druckbaren Ausgabezeilen
    sleep(0.1)
    print("Messung gestartet  : ", aktuelles_datum(),
          " ", aktuelle_uhrzeit(), sep="", end="\n\r")
    cpu_load_min = N_Max
    cpu_load_max = N_Min
    tcpu_min = N_Max
    tcpu_max = N_Min
    tgpu_min = N_Max
    tgpu_max = N_Min
    zyklus = 0
    anzeige_komplett = False
    while not stop or not anzeige_komplett:
        anz_z = N_Druck
        zyklus += 1
        spannung_exist = False
        cmd = "vcgencmd measure_volts"
        voltage = subprocess.run(cmd, shell=True,
                                 capture_output=True, text=True)
        if voltage.returncode == 0:
            spannung = float(voltage.stdout.replace(
                "volt=", "").replace("V\n", ""))
            spannung_exist = True
        cpu_count = psutil.cpu_count()
        cpu_load = psutil.cpu_percent(GC_messzyklus)
        mem = psutil.virtual_memory()
        freq = psutil.cpu_freq()
        tcpu = 0.0
        tgpu = 0.0
        tcpu_exist = False
        tgpu_exist = False
        if platform.system() == 'Linux':
            temp = psutil.sensors_temperatures()
            for name, entries in temp.items():
                if name == "k10temp" or name == "cpu_thermal":
                    tcpu_exist = True
                    for entry in entries:
                        tcpu = entry.current
                        if tcpu >= tcpu_max:
                            tcpu_max = tcpu
                        if tcpu <= tcpu_min:
                            tcpu_min = tcpu
                elif name == "amdgpu":
                    tgpu_exist = True
                    for entry in entries:
                        tgpu = entry.current
                        if tgpu >= tgpu_max:
                            tgpu_max = tgpu
                        if tgpu <= tgpu_min:
                            tgpu_min = tgpu
        if cpu_load >= cpu_load_max:
            cpu_load_max = cpu_load
        if cpu_load <= cpu_load_min:
            cpu_load_min = cpu_load
        print(60*"*", "\r")
        print(c.yellow, end="")
        if spannung_exist:
            print(f"* Messzeit", 4*" ", f"Testzyklus", 4*" ",
                  f"CPU-Anzahl", 6*" ", f"Spannung", 7*" ", "*\r", sep="")
            print(f"* {aktuelle_uhrzeit():8s}", 6*" ", f"{zyklus:8d}",
                  6*" ", f"{cpu_count:8d}", 6*" ",
                  f"{spannung:8.4f}", 7*" ", "*\r", sep="")
        else:
            print(f"* Messzeit", 4*" ", f"Testzyklus", 4*" ",
                  f"CPU-Anzahl", 21*" ", "*\r", sep="")
            print(f"* {aktuelle_uhrzeit():8s}", 6*" ", f"{zyklus:8d}",
                  6*" ", f"{cpu_count:8d}", 21*" ", "*\r", sep="")
        print(f"*", 58*" ", "*\r", sep="")
        print(f"* CPU-Last", 9*" ", f"L-akt", 9*" ",
              f"L-min", 9 * " ", f"L-max", 7*" ", "*\r", sep="")
        print(c.yellow, f"*", 13*" ",
              c.green, f"{cpu_load:8.1f} %", 4*" ",
              c.lightcyan, f"{cpu_load_min:8.1f} %", 4*" ",
              c.lightred, f"{cpu_load_max:8.1f} %", 7*" ",
              c.yellow, "*\r", sep="")
        # print(f"*", 58*" ", "*\r", sep="")
        if tcpu_exist or tgpu_exist:
            print(f"* Temperatur", 7*" ", f"T-akt", 9*" ",
                  f"T-min", 9 * " ", f"T-max", 7*" ", "*\r", sep="")
        else:
            anz_z -= 1
        if tcpu_exist:
            print(c.yellow, f"*  - CPU", 6*" ",
                  c.green, f"{tcpu:8.1f}'C", 4*" ",
                  c.lightcyan, f"{tcpu_min:8.1f}'C", 4*" ",
                  c.lightred, f"{tcpu_max:8.1f}'C", 7*" ",
                  c.yellow, "*\r", sep="")
        else:
            anz_z -= 1
        if tgpu_exist:
            print(c.yellow, f"*  - GPU", 6*" ",
                  c.green, f"{tgpu:8.1f}'C", 4*" ",
                  c.lightcyan, f"{tgpu_min:8.1f}'C", 4*" ",
                  c.lightred, f"{tgpu_max:8.1f}'C", 7*" ",
                  c.yellow, "*\r", sep="")
        else:
            anz_z -= 1
        # print(f"*", 58*" ", "*\r", sep="")
        print(f"* Frequenz", 9*" ", f"F-akt", 9*" ",
              f"F-min", 9 * " ", f"F-max", 7*" ", "*\r", sep="")
        print(c.yellow, f"*", 11*" ",
              c.green, f"{freq.current:8.1f} MHz", 2*" ",
              c.lightcyan, f"{freq.min:8.1f} MHz", 2*" ",
              c.lightred, f"{freq.max:8.1f} MHz", 7*" ",
              c.yellow, "*\r", sep="")
        # print(f"*", 58*" ", "*\r", sep="")
        print(f"* Memory", 12*" ", f"Proz", 10*" ",
              f"used", 9 * " ", f"total", 7*" ", "*\r", sep="")
        print(c.yellow, f"*", 13*" ",
              c.green, f"{mem.percent:8.1f} %", 3*" ",
              c.lightcyan, f"{mem.used/1024/1024:8.1f} MB", 3*" ",
              c.lightred, f"{mem.total/1024/1024:8.1f} MB", 7*" ",
              c.yellow, "*\r", sep="")
        print(c.reset, end="")
        print(60*"*", "\r")
        print((anz_z+2)*p.up, end="")
        sleep(0.01)
        anzeige_komplett = True
    print((anz_z+2)*p.down, end="")
    print("Messung beendet    : ", aktuelles_datum(),
          " ", aktuelle_uhrzeit(), sep="", end="\n\r")
    print()
    return


def _main():
    global stop
    try:
        show_header(G_HEADER_1, G_HEADER_2, __file__, G_OS)
        psutil.cpu_percent(GC_messzyklus)
        if platform.system() == 'Linux':
            show_systemumgebung()
        stop = False
        th_anzeige = threading.Thread(target=anzeige_thread)
        th_anzeige.start()
        while True:
            sleep(0.1)
            char = getch()
            if char == 'q':
                sleep(1.0)
                break
            char = ""
        stop = True
        th_anzeige.join()
    except(KeyboardInterrupt, SystemExit):
        sleep(1.0)
        stop = True
        print(c.lightred, p.up)
        print(3*" ", "\n!!! Programm abgebrochen !!!\n", c.reset)


if __name__ == "__main__":
    _main()
