#!/usr/bin/env python3

# Programm     : test_pynput.py
# Version      : 1.00
# SW-Stand     : 17.02.2022
# Autor        : Kanopus1958
# Beschreibung : Test Tastenüberwachung mit pynput

from time import sleep
from rwm_mod01 import show_header
from rwm_steuerung import color as c, position as p
from pynput import keyboard

G_OS = ('Raspbian', 'Debian', 'Windows')
G_HEADER_1 = '# Test PYNPUT - Funktionen    '
G_HEADER_2 = '      (Stop q/CTRL_C/CTRL_Z) #'


def on_press(key):
    sleep(0.00)
    try:
        print(f'\r{c.lightgreen}alphanumeric key {key.char} pressed{c.reset}')
    except AttributeError:
        print(f'\r{c.lightgreen}special key {key} pressed{c.reset}')


def on_release(key):
    sleep(0.01)
    print(f'{c.lightgrey}  {key} released{c.reset}')
    if key == keyboard.Key.esc:
        # Stop listener
        return False


def _main():
    try:
        show_header(G_HEADER_1, G_HEADER_2, __file__, G_OS)
        print('Start des Tests')
        listener = keyboard.Listener(on_press=on_press, on_release=None)
        listener.start()
        with keyboard.Events() as events:
            for event in events:
                if event.key == keyboard.Key.esc:
                    break
                else:
                    sleep(0.03)
                    print(f'\r{c.yellow}Received event {event}{c.reset}')
        print('Ende des Tests\n')
 ßß   except(KeyboardInterrupt, SystemExit):
        sleep(1.0)
        print(c.lightred, p.up)
        print(3*" ", "\n!!! Programm abgebrochen !!!\n", c.reset)


if __name__ == "__main__":
    _main()
