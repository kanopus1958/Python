#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Modul        : rwn_steuerung.py
# Version      : 1.01
# SW-Stand     : 12.02.2022
# Autor        : Kanopus1958
# Beschreibung : Definition von Steuerungs-Sequenzen
#                Cursor-Position, Farben und Tastencodes

class position:
    up         = '\r\033[A'
    down       = '\r\033[B'
    right      = '\033[C'
    left       = '\033[D'

class color:
    reset      = '\033[0m'
    black      = '\033[30m'
    red        = '\033[31m'
    green      = '\033[32m'
    orange     = '\033[33m'
    blue       = '\033[34m'
    purple     = '\033[35m'
    pink       = '\033[95m'
    cyan       = '\033[36m'
    white      = '\033[37m'
    yellow     = '\033[93m'
    lightgrey  = '\033[37m'
    darkgrey   = '\033[90m'
    lightred   = '\033[91m'
    lightgreen = '\033[92m'
    lightblue  = '\033[94m'
    lightcyan  = '\033[96m'

class key_stroke:
    # common
    LF = '\x0d'
    CR = '\x0a'
    ENTER = '\x0d'
    BACKSPACE = '\x7f'
    SUPR = ''
    SPACE = '\x20'
    ESC = '\x1b'
    # CTRL
    CTRL_A = '\x01'
    CTRL_B = '\x02'
    CTRL_C = '\x03'
    CTRL_D = '\x04'
    CTRL_E = '\x05'
    CTRL_F = '\x06'
    CTRL_Z = '\x1a'
    # ALT
    ALT_A = '\x1b\x61'
    # CTRL + ALT
    CTRL_ALT_A = '\x1b\x01'
    # cursors
    UP = '\x1b\x5b\x41'
    DOWN = '\x1b\x5b\x42'
    LEFT = '\x1b\x5b\x44'
    RIGHT = '\x1b\x5b\x43'
    CTRL_ALT_SUPR = '\x1b\x5b\x33\x5e'
    # other
    F1 = '\x1b\x4f\x50'
    F2 = '\x1b\x4f\x51'
    F3 = '\x1b\x4f\x52'
    F4 = '\x1b\x4f\x53'
    F5 = '\x1b\x4f\x31\x35\x7e'
    F6 = '\x1b\x4f\x31\x37\x7e'
    F7 = '\x1b\x4f\x31\x38\x7e'
    F8 = '\x1b\x4f\x31\x39\x7e'
    F9 = '\x1b\x4f\x32\x30\x7e'
    F10 = '\x1b\x4f\x32\x31\x7e'
    F11 = '\x1b\x4f\x32\x33\x7e'
    F12 = '\x1b\x4f\x32\x34\x7e'
    PAGE_UP = '\x1b\x5b\x35\x7e'
    PAGE_DOWN = '\x1b\x5b\x36\x7e'
    HOME = '\x1b\x5b\x48'
    END = '\x1b\x5b\x46'
    INSERT = '\x1b\x5b\x32\x7e'
    SUPR = '\x1b\x5b\x33\x7e'
    