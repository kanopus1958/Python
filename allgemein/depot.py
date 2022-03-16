#!/usr/bin/env python3

# Programm     : depot.py
# Version      : 1.00
# SW-Stand     : 15.03.2022
# Autor        : Kanopus1958
# Beschreibung : Aktueller Depotbestand

import sys
import os
import requests
from bs4 import BeautifulSoup
import time
from rwm_mod01 import show_header, aktuelles_datum_kurz, aktuelle_uhrzeit
from rwm_steuerung import color as c

G_OS = ('Raspbian', 'Debian', 'Windows')
G_HEADER_1 = '# Aktueller Depotbestand      '
G_HEADER_2 = '                             #'

HILFS_LISTE = ['Anz', 'Invest', 'Url', 'Bez', 'Datum',
               'Uhrzeit', 'Handel', 'Wert', 'DiffEur', 'DiffProz']

depot = {}
wps = {}
wp_temp = {}
del_id = []


def einlesen_input():
    input_datei = os.path.realpath(__file__).replace(".py", ".input")
    if not os.path.isfile(input_datei):
        print(f'{c.lightred}\nError --> Input-Datei exitiert '
              f'nicht :\n{input_datei}{c.reset}\n')
        return False
    with open(input_datei, 'r') as fobj:
        for line in fobj:
            if line.strip().count('@@@'):
                zeile = line.strip().split()
                if '@@@URL@@@' in zeile:
                    depot['Url'] = zeile[1]
                if '@@@KONTO@@@' in zeile:
                    depot['Konto'] = float(zeile[1])
                if '@@@KOSTEN@@@' in zeile:
                    depot['Kosten'] = float(zeile[1])
                if '@@@WP@@@' in zeile:
                    zeile = zeile[1:]
                    zeile[1] = int(zeile[1])
                    zeile[2] = float(zeile[2])
                    wps[zeile[0]] = dict(zip(HILFS_LISTE, zeile[1:]))
    return True


def depot_bestandsermittlung(id):
    page = requests.get(depot['Url'] + wps[id]['Url'])
    if page.status_code != 200:
        print(f'{c.lightred}\nFehler bei Wertpapierabfrage "{id}"\n'
              f'Return-Code der HTML-Seite = {page.status_code}{c.reset}')
        return False
    soup = BeautifulSoup(page.content, 'html.parser')
    wps[id].update({'Bez': soup.h1.string.strip()})
    zeilen = soup.find_all('div', class_="row quotebox")
    for zeile in zeilen:
        werte = []
        for string in zeile.stripped_strings:
            werte.append(string)
        werte = [wert.replace(',', '.') for wert in werte]
        werte = [wert for wert in werte if (wert != 'EUR') and (wert != '%')]
        if (len(werte) == 5) or ((len(werte) > 5) and (werte[4] == 'NAV')):
            werte = [wert for wert in werte[:5]]
            werte.append(werte[len(werte)-1])
            if werte[3].count(':'):
                werte[4] = werte[3]
                werte[3] = aktuelles_datum_kurz()
            else:
                werte[4] = '00:00:00'
            # print(werte)
    wp_temp = {'Datum': werte[3], 'Uhrzeit': werte[4],
               'Handel': werte[5], 'Wert': float(werte[0]),
               'DiffEur': float(werte[1]),
               'DiffProz': float(werte[2])}
    wps[id].update(wp_temp)
    return True


def wertpapier_entwicklung():
    msg = f''
    msg += f'WERTPAPIER ENTWICKLUNG ' \
        f'(Stand: {aktuelles_datum_kurz()} {aktuelle_uhrzeit()})\n'
    msg += f'Fond / Wertpapier                             Kurs  Diff €' \
        f'  Diff %  Handel          Datum/Uhrzeit\n'
    msg += f'{97*"-"}\n'
    for wp, details in wps.items():
        msg += f'{details["Bez"]:38s} : ' \
            f'{details["Wert"]:8.2f}€ ' \
            f'{details["DiffEur"]:+6.2f}€ ' \
            f'{details["DiffProz"]:+6.2f}%     ' \
            f'{details["Handel"]:3s}  ' \
            f'({details["Datum"]} {details["Uhrzeit"]})\n'
    return msg


def depot_bestand():
    gesamt_invest = 0
    gesamt_summe = 0
    gesamt_resultat = 0
    msg = f''
    msg += f'AKTUELLER DEPOTWERT    ' \
        f'(Stand: {aktuelles_datum_kurz()} {aktuelle_uhrzeit()})\n'
    msg += f'Fond / Wertpapier                             Kurs     Anz' \
        f'         Wert       Invest          G/V\n'
    msg += f'{97*"-"}\n'
    for wp, details in wps.items():
        anz = details["Anz"]
        gesamt_invest += (invest := details["Invest"])
        gesamt_summe += (summe := details["Wert"] * anz)
        gesamt_resultat += (resultat := summe - details["Invest"])
        msg += f'{details["Bez"]:38s} : ' \
            f'{details["Wert"]:8.2f}€ x ' \
            f'{anz:5d}' \
            f'{summe:12.2f}€' \
            f'{details["Invest"]:12.2f}€' \
            f'{resultat:12.2f}€\n'
    msg += f'{gesamt_summe:>70,.2f}€  {gesamt_invest:10,.2f}€  ' \
        f'{gesamt_resultat:10,.2f}€\n\n'
    msg += f'Vermögen (inkl. Konto {depot["Konto"]:+8.2f}€ ' \
        f'und Kosten {-1.0*depot["Kosten"]:+8.2f}€) :' \
        f'{gesamt_summe + depot["Konto"] - depot["Kosten"]:>15,.2f}€  ' \
        f'{gesamt_invest + depot["Konto"]:10,.2f}€  ' \
        f'{gesamt_resultat - depot["Kosten"]:10,.2f}€\n'
    return msg


def _main():
    show_header(G_HEADER_1, G_HEADER_2, __file__, G_OS)
    if not einlesen_input():
        sys.exit(False)
    for id in wps:
        if not depot_bestandsermittlung(id):
            del_id.append(id)
    for loesch_eintrag in del_id:
        del wps[loesch_eintrag]
    print(f'\n{wertpapier_entwicklung()}')
    print(f'{depot_bestand()}')


if __name__ == "__main__":
    t0 = time.perf_counter()
    _main()
    # print(f'Laufzeit : {time.perf_counter() - t0:8,.4f} Sekunden\n')
