#!/usr/bin/env python3

# Programm     : depot.py
# Version      : 1.00
# SW-Stand     : 21.05.2022
# Autor        : Kanopus1958
# Beschreibung : Aktueller Depotbestand

import os
import requests
from bs4 import BeautifulSoup
import time
from rwm_steuerung import color as c
from rwm_mod01 import show_header, aktuelles_datum_kurz, \
    aktuelle_uhrzeit, datum_zu_ts
from rwm_class01 import MyDB

G_OS = ('Windows')
G_HEADER_1 = '# Aktueller Depotbestand      '
G_HEADER_2 = '                             #'

database = r'O:\01_Daten\DatenLocal\Datenbanken\SQLite\finanzanlage.db'

HILFS_LISTE = ['Anz', 'Invest', 'Url', 'Bez', 'Datum',
               'Uhrzeit', 'Handel', 'Kurs', 'DiffEur',
               'DiffProz', 'Wert', 'G_V']
wp_temp = {}
del_id = []
md = {}
wps = {}
summen = {}
bErrHTML = False


def einlesen_input(input_datei):
    with open(input_datei, 'r') as fobj:
        for line in fobj:
            if line.strip().count('@@@'):
                zeile = line.strip().split()
                if '@@@KONTO@@@' in zeile:
                    md['Konto'] = float(zeile[1])
                if '@@@KOSTEN@@@' in zeile:
                    md['Kosten'] = float(zeile[1])
                if '@@@WP@@@' in zeile:
                    zeile = zeile[1:]
                    zeile[1] = int(zeile[1])
                    zeile[2] = float(zeile[2])
                    zeile[3] = zeile[3] + zeile[4]
                    zeile.pop()
                    wps[zeile[0]] = dict(zip(HILFS_LISTE, zeile[1:]))
    # print(f'md : {md}')
    # print(f'wps : {wps}')
    return True


def init_database():
    sql_create_vermoegen_table = '''
    CREATE TABLE IF NOT EXISTS vermoegen (
    Id         INTEGER PRIMARY KEY,
    Datum      TEXT    NOT NULL
                       UNIQUE,
    Timestamp  REAL    NOT NULL,
    Datum_Zeit TEXT    NOT NULL,
    Konto      REAL    NOT NULL,
    Kosten     REAL    NOT NULL,
    Wert       REAL    NOT NULL,
    Invest     REAL    NOT NULL,
    G_V        REAL    NOT NULL
    );
    '''
    sql_create_wertpapiere_table = '''
    CREATE TABLE IF NOT EXISTS wertpapiere (
    Id       INTEGER PRIMARY KEY,
    Kurz_Bez TEXT UNIQUE
                  NOT NULL,
    Url      TEXT NOT NULL,
    Bez      TEXT NOT NULL,
    Handel   TEXT NOT NULL    );
    '''
    sql_create_kurse_table = '''
    CREATE TABLE IF NOT EXISTS kurse (
    Id            INTEGER PRIMARY KEY,
    Wertpapier_Id INTEGER NOT NULL,
    Datum         TEXT    NOT NULL,
    Timestamp     REAL    NOT NULL,
    Datum_Zeit    TEXT    NOT NULL,
    Anz           INTEGER NOT NULL,
    Kurs          REAL    NOT NULL,
    Diff_EUR      REAL    NOT NULL,
    Diff_Proz     REAL    NOT NULL,
    Wert          REAL    NOT NULL,
    Invest        REAL    NOT NULL,
    G_V           REAL    NOT NULL,
    FOREIGN KEY (
        Wertpapier_Id
    )
    REFERENCES wertpapiere (Id)    );
    '''
    db.dbCreateDropTable(sql_create_vermoegen_table)
    db.dbCreateDropTable(sql_create_wertpapiere_table)
    db.dbCreateDropTable(sql_create_kurse_table)
    return True


def create_vermoeg(vermoeg):
    lastkey = None
    sql_select = ''' SELECT * FROM vermoegen WHERE
                     Datum = ? '''
    sql_param = [vermoeg[0], ]
    datensatz = db.dbReadOneRow(sql_select, sql_param)
    if not datensatz:
        sql_insupddel = ''' INSERT INTO vermoegen(Datum,Timestamp,Datum_Zeit,
                            Konto,Kosten,Wert,Invest,G_V)
                            VALUES(?,?,?,?,?,?,?,?) '''
        sql_param = vermoeg
        lastkey = db.dbInsUpdDelRow(sql_insupddel, sql_param)
    else:
        sql_insupddel = ''' UPDATE vermoegen
                            SET Timestamp = ?,
                                Datum_Zeit = ?,
                                Konto = ?,
                                Kosten = ?,
                                Wert = ?,
                                Invest = ?,
                                G_V = ?
                            WHERE Id = ? '''
        sql_param = vermoeg[1:]
        sql_param.append(datensatz[0])
        db.dbInsUpdDelRow(sql_insupddel, sql_param)
        lastkey = datensatz[0]
    return lastkey


def create_wertpapier(wertpapier):
    lastkey = None
    sql_select = ''' SELECT * FROM wertpapiere WHERE
                     Kurz_Bez = ? '''
    sql_param = (wertpapier[0],)
    datensatz = db.dbReadOneRow(sql_select, sql_param)
    if not datensatz:
        sql_insupddel = ''' INSERT INTO wertpapiere(Kurz_Bez,Url,Bez,Handel)
                            VALUES(?,?,?,?) '''
        sql_param = wertpapier
        lastkey = db.dbInsUpdDelRow(sql_insupddel, sql_param)
    else:
        sql_insupddel = ''' UPDATE wertpapiere
                            SET Url = ?,
                                Bez = ?,
                                Handel = ?
                            WHERE Id = ? '''
        sql_param = wertpapier[1:]
        sql_param.append(datensatz[0])
        db.dbInsUpdDelRow(sql_insupddel, sql_param)
        lastkey = datensatz[0]
    return lastkey


def create_kurs(kurs):
    lastkey = None
    sql_select = ''' SELECT * FROM kurse WHERE
                     Wertpapier_Id = ?  AND Datum = ? '''
    sql_param = kurs[0:2]
    datensatz = db.dbReadOneRow(sql_select, sql_param)
    if not datensatz:
        sql_insupddel = ''' INSERT INTO kurse(Wertpapier_Id,Datum,
                            Timestamp,Datum_Zeit,Anz,Kurs,Diff_EUR,
                            Diff_Proz,Wert,Invest,G_V)
                            VALUES(?,?,?,?,?,?,?,?,?,?,?) '''
        sql_param = kurs
        lastkey = db.dbInsUpdDelRow(sql_insupddel, sql_param)
    else:
        sql_insupddel = ''' UPDATE kurse
                            SET Timestamp = ?,
                                Datum_Zeit = ?,
                                Anz = ?,
                                Kurs = ?,
                                Diff_EUR = ?,
                                Diff_Proz = ?,
                                Wert = ?,
                                Invest = ?,
                                G_V = ?
                            WHERE Id = ? '''
        sql_param = kurs[2:]
        sql_param.append(datensatz[0])
        db.dbInsUpdDelRow(sql_insupddel, sql_param)
        lastkey = datensatz[0]
    return lastkey


def db_update():
    datum = aktuelles_datum_kurz()
    zeit = aktuelle_uhrzeit()
    datum_zeit = datum + ' ' + zeit
    datensatz_depot = [datum, datum_zu_ts(datum_zeit), datum_zeit,
                       summen["Konto"],
                       summen["Kosten"],
                       summen["Wert_abs"],
                       summen["Invest_abs"],
                       summen["G_V_abs"]
                       ]
    lastkey = create_vermoeg(datensatz_depot)
    for wp, details in wps.items():
        datensatz_wertpapier = [wp,
                                details["Url"],
                                details["Bez"],
                                details["Handel"]
                                ]
        wertpapier_id = create_wertpapier(datensatz_wertpapier)
        datum_zeit = details["Datum"] + ' ' + details["Uhrzeit"]
        datensatz_kurs = [wertpapier_id,
                          details["Datum"],
                          datum_zu_ts(datum_zeit),
                          datum_zeit,
                          details["Anz"],
                          details["Kurs"],
                          details["DiffEur"],
                          details["DiffProz"],
                          details["Wert"],
                          details["Invest"],
                          details["G_V"]
                          ]
        lastkey = create_kurs(datensatz_kurs)


def einlesen_webdaten(id):
    global bErrHTML
    page = requests.get(wps[id]['Url'])
    if page.status_code != 200:
        print(f'{c.lightred}\nFehler bei Wertpapierabfrage "{id}"\n'
              f'Return-Code der HTML-Seite = {page.status_code}{c.reset}')
        bErrHTML = True
        return False
    if 'finanzen' in wps[id]['Url']:
        if not web_finanzen(id, page):
            print(f'{c.lightred}\nFehler bei Einlesen Web-Page "{id}"\n'
                  f'Keine Werte gefunden{c.reset}')
            bErrHTML = True
            return False
    elif 'fondsprofessionell' in wps[id]['Url']:
        if not web_fondsprofessionell(id, page):
            print(f'{c.lightred}\nFehler bei Einlesen Web-Page "{id}"\n'
                  f'Keine Werte gefunden{c.reset}')
            bErrHTML = True
            return False
    else:
        print(f'{c.lightred}\nFehler bei Einlesen Web-Page "{id}"\n'
              f'Keine entsprechende Einlesefunktion gefunden{c.reset}')
        bErrHTML = True
        return False
    return True


def web_finanzen(id, page):
    soup = BeautifulSoup(page.content, 'html.parser')
    wps[id].update({'Bez': soup.h1.string.strip()})
    zeilen = soup.find_all('div', class_="row quotebox")
    werte = []
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
    if len(werte) == 0:
        return False
    wp_temp['Datum'] = werte[3]
    wp_temp['Uhrzeit'] = werte[4]
    wp_temp['Handel'] = werte[5]
    wp_temp['Kurs'] = float(werte[0])
    try:
        wp_temp['DiffEur'] = float(werte[1])
        wp_temp['DiffProz'] = float(werte[2])
    except ValueError:
        wp_temp['DiffEur'] = 0.0
        wp_temp['DiffProz'] = 0.0
    wp_temp['Wert'] = round(float(wps[id]['Anz'] * wp_temp['Kurs']), 2)
    wp_temp['G_V'] = round(
        float((wps[id]['Anz'] * wp_temp['Kurs']) - wps[id]['Invest']), 2)
    # print(f"wp_temp : {wp_temp}")
    wps[id].update(wp_temp)
    return True


def web_fondsprofessionell(id, page):
    soup = BeautifulSoup(page.content, 'html.parser')
    wps[id].update({'Bez': soup.h1.text})
    zeile = soup.find('table')
    werte = []
    for string in zeile.stripped_strings:
        werte.append(string)
    if len(werte) == 0:
        return False
    del werte[2]
    werte = [wert.replace(',', '.') for wert in werte]
    werte = [wert.replace(' EUR', '') for wert in werte]
    werte = [wert.replace(' am', '') for wert in werte]
    werte = [wert.replace('(', '') for wert in werte]
    werte = [wert.replace('%)', '') for wert in werte]
    temp = werte[0].split(' ')
    wp_temp['Datum'] = temp[1]
    wp_temp['Uhrzeit'] = '00:00:00'
    wp_temp['Handel'] = temp[0]
    wp_temp['Kurs'] = float(werte[1])
    temp = werte[2].split(' ')
    try:
        wp_temp['DiffEur'] = float(temp[0])
        wp_temp['DiffProz'] = float(temp[1])
    except ValueError:
        wp_temp['DiffEur'] = 0.0
        wp_temp['DiffProz'] = 0.0
    wp_temp['Wert'] = round(float(wps[id]['Anz'] * wp_temp['Kurs']), 2)
    wp_temp['G_V'] = round(
        float((wps[id]['Anz'] * wp_temp['Kurs']) - wps[id]['Invest']), 2)
    # print(f"wp_temp : {wp_temp}")
    wps[id].update(wp_temp)
    return True


def aufbereitung_daten():
    gesamt_invest = 0.0
    gesamt_summe = 0.0
    gesamt_resultat = 0.0
    for wp, details in wps.items():
        gesamt_invest += details["Invest"]
        gesamt_summe += details["Wert"]
        gesamt_resultat += details["G_V"]
    summen["Konto"] = round(md["Konto"], 2)
    summen["Kosten"] = -1.0*round(md["Kosten"], 2)
    summen["Wert"] = round(gesamt_summe, 2)
    summen["Invest"] = round(gesamt_invest, 2)
    summen["G_V"] = round(gesamt_resultat, 2)
    summen["Wert_abs"] = round(gesamt_summe + md["Konto"] - md["Kosten"], 2)
    summen["Invest_abs"] = round(gesamt_invest + md["Konto"], 2)
    summen["G_V_abs"] = round(gesamt_resultat - md["Kosten"], 2)
    # print(f'\nwps : {wps}')
    # print(f'\nsummen : {summen}')


def druckdaten_depot():
    msg = f''
    msg += f'AKTUELLER DEPOTWERT    ' \
           f'(Stand: {aktuelles_datum_kurz()} {aktuelle_uhrzeit()})\n'
    msg += f'Fond / Wertpapier                             Kurs     Anz' \
           f'         Wert       Invest          G/V\n'
    msg += f'{97*"-"}\n'
    for wp, details in wps.items():
        anz = details["Anz"]
        msg += f'{details["Bez"]:38s} : ' \
            f'{details["Kurs"]:8.2f}€ x ' \
            f'{details["Anz"]:5d}' \
            f'{details["Wert"]:12.2f}€' \
            f'{details["Invest"]:12.2f}€' \
            f'{details["G_V"]:12.2f}€\n'
    msg += f'{summen["Wert"]:>70,.2f}€  {summen["Invest"]:10,.2f}€  ' \
           f'{summen["G_V"]:10,.2f}€\n\n'
    msg += f'Vermögen (inkl. Konto {summen["Konto"]:+8.2f}€ ' \
           f'und Kosten {summen["Kosten"]:+8.2f}€) :' \
           f'{summen["Wert_abs"]:>15,.2f}€  ' \
           f'{summen["Invest_abs"]:10,.2f}€  ' \
           f'{summen["G_V_abs"]:10,.2f}€\n'
    return msg


def druckdaten_wp():
    msg = f''
    msg += f'WERTPAPIER ENTWICKLUNG ' \
           f'(Stand: {aktuelles_datum_kurz()} {aktuelle_uhrzeit()})\n'
    msg += f'Fond / Wertpapier                             Kurs  Diff €' \
           f'  Diff %  Handel          Datum/Uhrzeit\n'
    msg += f'{97*"-"}\n'
    for wp, details in wps.items():
        msg += f'{details["Bez"]:38s} : ' \
               f'{details["Kurs"]:8.2f}€ ' \
               f'{details["DiffEur"]:+6.2f}€ ' \
               f'{details["DiffProz"]:+6.2f}%     ' \
               f'{details["Handel"]:3s}  ' \
               f'({details["Datum"]} {details["Uhrzeit"]})\n'
    return msg


def _main():
    global db
    show_header(G_HEADER_1, G_HEADER_2, __file__, G_OS)
    input_datei = os.path.realpath(__file__).replace(".py", ".input")
    if not os.path.isfile(input_datei):
        print(f'\nFehler : Input-Datei existiert nicht\nError : '
              f'"{input_datei}"')
        print(f'Programm wurde abgebrochen')
        return False
    if not os.path.isfile(database):
        print(f'\nFehler : Datenbankdatei existiert nicht\nError  : '
              f'"{database}"')
        print(f'Programm wurde abgebrochen')
        return False
    einlesen_input(input_datei)
    db = MyDB(database)
    init_database()
    for id in wps:
        if not einlesen_webdaten(id):
            del_id.append(id)
    for loesch_eintrag in del_id:
        del wps[loesch_eintrag]
    aufbereitung_daten()
    print(f'\n{druckdaten_wp()}')
    print(f'{druckdaten_depot()}')
    if not bErrHTML:
        db_update()
    else:
        print(f'{c.yellow}Warnung bei Datenbank-Update\n'
              f'Keine Datenbankaktualisierung durchgeführt{c.reset}')


if __name__ == "__main__":
    t0 = time.perf_counter()
    _main()
    print(f'\nLaufzeit : {time.perf_counter() - t0:8,.4f} Sekunden\n')
