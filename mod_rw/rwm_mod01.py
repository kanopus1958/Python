#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Modul        : rwm_mod01.py
# Version      : 1.03
# SW-Stand     : 14.02.2022
# Autor        : Kanopus1958
# Beschreibung : Definition von allgemeinen Funktionen Teil 01
#                getkey()
#                getch()
#                aktuelle_uhrzeit()
#                aktuelles_datum()
#                show_header()
#                clean_console()

import os
import platform
import subprocess
import readchar
import datetime
from socket import gethostname
from rwm_steuerung import color as c, key_stroke as k


def getkey():
    key = readchar.readkey()
    return key


def getch():
    char = readchar.readchar()
    ch = str(char)
    if platform.system() == 'Windows':
        ch = str(char, encoding='utf-8', errors="ignore")
    return ch


def aktuelle_uhrzeit():
    now = datetime.datetime.now()
    uhrzeit = now.strftime('%H:%M:%S')
    return uhrzeit


def aktuelles_datum():
    now = datetime.datetime.now()
    datum = now.strftime('%A %d.%m.%Y')
    return datum


def show_header(h1, h2, f1, runable=('Raspbian')):
    script_n = os.path.basename(f1)
    script_v = datetime.datetime.fromtimestamp(os.path.getmtime(
        os.path.realpath(f1))).strftime('%d.%m.%Y %H:%M:%S')
    knotenname = gethostname()
    os_info = os_system = os_distribution = "###"
    os_system = platform.system()
    os_info = os_system
    if os_system == 'Linux':
        cmd = "lsb_release -is"
        x = subprocess.run(cmd, shell=True,
                           capture_output=True, text=True)
        if x.returncode == 0:
            os_distribution = x.stdout.replace("\n", "").strip()
            os_info = os_info+' -- '+os_distribution
    clean_console()
    print(c.white, end="")
    print(60*"#", sep="")
    print(h1, h2, sep="")
    print("#", 58*" ", "#", sep="")
    print(f"# Python-Script: {script_n:22s}", 20*" ", "#", sep="")
    print(f"# Versionsstand: {script_v:22s}", 20*" ", "#", sep="")
    print(f"# Knotenname   : {knotenname:40s}", 2*" ", "#", sep="")
    print(f"# OS-Info      : {os_info:40s}", 2*" ", "#", sep="")
    print(60*"#", sep="")
    print(c.reset, end="")
    if os_system in runable or os_distribution in runable:
        pass
    else:
        print(c.lightred, "\n!!! Programm ist nur lauffähig unter !!!")
        print("   ", runable)
        print("!!! Programm wird abgebrochen        !!!\n", c.reset)
        exit(False)
    return


def clean_console():
    command = 'clear'  # Konsole löschen in Linux
    if platform.system() in ('Windows'):  # Konsole löschen in Windows
        command = 'cls'
    os.system(command)
    return
