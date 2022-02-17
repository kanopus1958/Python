#!/usr/bin/env python3

# Programm     : test_pynput.py
# Version      : 1.00
# SW-Stand     : 17.02.2022
# Autor        : Kanopus1958
# Beschreibung : Test Tastenüberwachung mit pynput
G_OS = ('Raspbian','Debian','Windows') 
G_HEADER_1 = '# Test PYNPUT - Funktionen    '
G_HEADER_2 = '      (Stop q/CTRL_C/CTRL_Z) #'

from pynput import keyboard
from rwm_steuerung import color as c
from rwm_mod01 import show_header
from time import sleep

def on_press(key):
    try:
        print('alphanumeric key {0} pressed'.format(
            key.char))
    except AttributeError:
        print('special key {0} pressed'.format(
            key))

def on_release(key):
    print('{0} released'.format(
        key))
    if key == keyboard.Key.esc:
        # Stop listener
        return False

def _main():
    try:
        show_header(G_HEADER_1, G_HEADER_2, __file__, G_OS)
        print('Start des Tests')
        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.start()
        while True:
            print('main loop still alive')
            sleep(5.0)
        print('Ende des Tests\n')
    except(KeyboardInterrupt, SystemExit):
        sleep(1.0)
        print(c.lightred, p.up)
        print(3*" ", "\n!!! Programm abgebrochen !!!\n", c.reset)

if __name__ == "__main__":
    _main()