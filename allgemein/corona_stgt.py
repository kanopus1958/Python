#!/usr/bin/env python3

# Programm     : corona_stgt.py
# Version      : 1.00
# SW-Stand     : 09.04.2022
# Autor        : Kanopus1958
# Beschreibung : Ermittlung Coronafallzahlen für Stuttgart

import os
import requests
from bs4 import BeautifulSoup
import time
import sqlite3
from sqlite3 import Error
from rwm_mod01 import show_header, aktuelles_datum_kurz, \
    aktuelles_datum, aktuelle_uhrzeit, datum_zu_ts
from rwm_steuerung import color as c

G_OS = ('Windows')
G_HEADER_1 = '# Corona Fallzahlen für Stuttg'
G_HEADER_2 = 'art                          #'

URL = f'https://www.stuttgart.de/leben/gesundheit/' \
      f'corona/fallzahlen-und-impfungen.php'
URLRKI = f'https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/' \
         f'Fallzahlen.html'
database = r'O:\01_Daten\DatenLocal\Datenbanken\SQLite\corona_stgt.db'
print_gebiet = ('Baden-Württemberg', 'Gesamt Deutschland', 'Hessen')

cov = {'Datum': "01.01.2022", 'Zeit': "00:00:00",
       'Faelle_Abs': 0, 'Faelle_Delta': 0,
       'Neu7t_Abs': 0, 'Neu7t_Vortag': 0,
       'Inz7t_Abs': 0.0, 'Inz7t_Vortag': 0.0,
       'Tote_Abs': 0, 'Tote_Delta': 0
       }

covRKI = []

cov_temp = {'Datum': "01.01.2022", 'Zeit': "00:00:00", 'Gebiet': "Bundesland",
            'Anzahl': 0, 'Delta': 0,
            'Anz7t': 0, 'Inz7t': 0.0,
            'Tote': 0
            }


def create_connection(db_file):
    if os.path.isfile(db_file):
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            print(f'\nFehler : Datenbankverbindung gescheitert\nError : "{e}"')
        return None
    else:
        print(f'\nFehler : Datenbankdatei existiert nicht\nError : '
              f'"{db_file}"')
        return None


def init_database(conn):
    sql_create_fallzahlen_table = '''
    CREATE TABLE IF NOT EXISTS fallzahlen (
    Id              INTEGER PRIMARY KEY,
    Datum           TEXT    NOT NULL
                            UNIQUE,
    Timestamp       REAL    NOT NULL,
    Datum_Zeit      TEXT    NOT NULL,
    Faelle_Abs      INTEGER NOT NULL,
    Faelle_Delta    INTEGER NOT NULL,
    Neu7t_Abs       INTEGER NOT NULL,
    Neu7t_Vortag    INTEGER NOT NULL,
    Inz7t_Abs       REAL    NOT NULL,
    Inz7t_Vortag    REAL    NOT NULL,
    Tote_Abs        INTEGER NOT NULL,
    Tote_Delta      INTEGER NOT NULL
    );
    '''
    sql_create_rkifallzahlen_table = '''
    CREATE TABLE IF NOT EXISTS rkifallzahlen (
    Id              INTEGER PRIMARY KEY,
    Datum           TEXT    NOT NULL,
    Timestamp       REAL    NOT NULL,
    Datum_Zeit      TEXT    NOT NULL,
    Gebiet          TEXT    NOT NULL,
    Anzahl          INTEGER NOT NULL,
    Delta           INTEGER NOT NULL,
    Anz7t           INTEGER NOT NULL,
    Inz7t           REAL    NOT NULL,
    Tote            INTEGER NOT NULL
    );
    '''
    create_table(conn, sql_create_fallzahlen_table)
    create_table(conn, sql_create_rkifallzahlen_table)
    return True


def create_table(conn, create_table_sql):
    try:
        cur = conn.cursor()
        cur.execute(create_table_sql)
        conn.commit()
        cur.close()
    except Error as e:
        print(f'\nFehler : Neuanlage Tabelle fehlgeschlagen\nError : "{e}"')


def lese_datensatz(conn, sql, sql_param):
    cur = conn.cursor()
    datensatz = cur.execute(sql, sql_param).fetchone()
    if datensatz is not None:
        return datensatz
    else:
        return None


def create_fallzahl(conn, fallzahl):
    lastkey = None
    sql = f''' SELECT * FROM fallzahlen WHERE
                Datum = ? '''
    sql_param = [fallzahl[0], ]
    datensatz = lese_datensatz(conn, sql, sql_param)
    if not datensatz:
        sql = ''' INSERT INTO fallzahlen (Datum,Timestamp,Datum_Zeit,
                Faelle_Abs,Faelle_Delta,Neu7t_Abs,Neu7t_Vortag,
                Inz7t_Abs,Inz7t_Vortag,Tote_Abs,Tote_Delta)
                VALUES(?,?,?,?,?,?,?,?,?,?,?) '''
        sql_param = fallzahl
        try:
            cur = conn.cursor()
            cur.execute(sql, sql_param)
            conn.commit()
            lastkey = cur.lastrowid
            cur.close()
        except Error as e:
            print(f'\nInfo : Fallzahleneintrag '
                  f'existiert schon \nError : "{e}"\n')
    else:
        sql = ''' UPDATE fallzahlen
                  SET Timestamp = ?,
                      Datum_Zeit = ?,
                      Faelle_Abs = ?,
                      Faelle_Delta = ?,
                      Neu7t_Abs = ?,
                      Neu7t_Vortag = ?,
                      Inz7t_Abs = ?,
                      Inz7t_Vortag = ?,
                      Tote_Abs = ?,
                      Tote_Delta = ?
                  WHERE Id = ? '''
        sql_param = fallzahl[1:]
        sql_param.append(datensatz[0])
        cur = conn.cursor()
        cur.execute(sql, sql_param)
        conn.commit()
        cur.close()
        lastkey = datensatz[0]
    return lastkey


def create_fallzahl_RKI(conn, fallzahl):
    lastkey = None
    sql = f''' SELECT * FROM rkifallzahlen WHERE
                Datum = ? AND Gebiet = ?'''
    sql_param = [fallzahl[0], fallzahl[3]]
    datensatz = lese_datensatz(conn, sql, sql_param)
    if not datensatz:
        sql = ''' INSERT INTO rkifallzahlen (Datum,Timestamp,Datum_Zeit,
                  Gebiet,Anzahl,Delta,Anz7t,
                  Inz7t,Tote)
                  VALUES(?,?,?,?,?,?,?,?,?) '''
        sql_param = fallzahl
        try:
            cur = conn.cursor()
            cur.execute(sql, sql_param)
            conn.commit()
            lastkey = cur.lastrowid
            cur.close()
        except Error as e:
            print(f'\nInfo : Fallzahleneintrag '
                  f'existiert schon \nError : "{e}"\n')
    else:
        sql = ''' UPDATE rkifallzahlen
                  SET Timestamp = ?,
                      Datum_Zeit = ?,
                      Gebiet = ?,
                      Anzahl = ?,
                      Delta = ?,
                      Anz7t = ?,
                      Inz7t = ?,
                      Tote = ?
                  WHERE Id = ? '''
        sql_param = fallzahl[1:]
        sql_param.append(datensatz[0])
        cur = conn.cursor()
        cur.execute(sql, sql_param)
        conn.commit()
        cur.close()
        lastkey = datensatz[0]
    return lastkey


def db_update(conn):
    datum_zeit = cov["Datum"] + ' ' + cov["Zeit"]
    datensatz_fallzahl = [cov["Datum"], datum_zu_ts(datum_zeit),
                          datum_zeit,
                          cov["Faelle_Abs"],
                          cov["Faelle_Delta"],
                          cov["Neu7t_Abs"],
                          cov["Neu7t_Vortag"],
                          cov["Inz7t_Abs"],
                          cov["Inz7t_Vortag"],
                          cov["Tote_Abs"],
                          cov["Tote_Delta"]
                          ]
    lastkey = create_fallzahl(conn, datensatz_fallzahl)
    for z in covRKI:
        datum_zeit = z["Datum"] + ' ' + z["Zeit"]
        datensatz_rkifallzahl = [z["Datum"], datum_zu_ts(datum_zeit),
                                 datum_zeit,
                                 z["Gebiet"],
                                 z["Anzahl"],
                                 z["Delta"],
                                 z["Anz7t"],
                                 z["Inz7t"],
                                 z["Tote"]
                                 ]
        lastkey = create_fallzahl_RKI(conn, datensatz_rkifallzahl)


def einlesen_webdaten():
    datum_zeile = ""
    fallzahlen_zeile = ""
    page = requests.get(URL)
    if page.status_code != 200:
        print(f'{c.lightred}\nFehler bei WEB-Seiten-Abfrage\n'
              f'Return-Code der HTML-Seite = {page.status_code}{c.reset}')
        return False
    soup = BeautifulSoup(page.content, 'html.parser')
    datum_zeile = soup.find(
        'h2', class_="SP-Collapsible__trigger__text SP-Iconized__text").text
    # print(f'datum_zeile : {datum_zeile}')
    zeilen = soup.find_all('section', class_="SP-Text")
    for zeile in zeilen:
        if 'Fallzahlen für Stuttgart' in zeile.text:
            # print(f'zeilentext : {zeile.text}')
            fallzahlen_zeile = zeile.text
    if len(datum_zeile) and len(fallzahlen_zeile):
        aufbereitung_daten(datum_zeile, fallzahlen_zeile)
        return True
    else:
        print(f'{c.lightred}\nFehler bei der Fallzahlenermittlung\n'
              f'{c.reset}')
        return False


def einlesen_webdaten_RKI():
    datum_zeile = ""
    fallzahlen_zeilen = []
    page = requests.get(URLRKI)
    if page.status_code != 200:
        print(f'{c.lightred}\nFehler bei WEB-Seiten-Abfrage\n'
              f'Return-Code der HTML-Seite = {page.status_code}{c.reset}')
        return False
    soup = BeautifulSoup(page.content, 'html.parser')
    zeilen = soup.find_all('h2', class_='null')
    for zeile in zeilen:
        if 'Fallzahlen in Deutschland' in zeile.text:
            datum_zeile = zeile.parent.p.text
            # print(f'\ndatum_zeile : {datum_zeile}\n')
    zeilen = soup.find('tbody')
    zeilen = zeilen.find_all('tr')
    for zeile in zeilen:
        fallzahlen_zeilen.append([])
        eintraege = zeile.find_all('td')
        for eintrag in eintraege:
            fallzahlen_zeilen[-1].append(eintrag.text)
    # print(f'\nfallzahlen_zeilen : {fallzahlen_zeilen}\n')

    if len(datum_zeile) and len(fallzahlen_zeilen):
        aufbereitung_daten_RKI(datum_zeile, fallzahlen_zeilen)
        return True
    else:
        print(f'{c.lightred}\nFehler bei der Fallzahlenermittlung\n'
              f'{c.reset}')
        return False


def aufbereitung_daten(datum_zeile, fallzahlen_zeile):
    datum_zeile = datum_zeile.replace('Corona-Kennzahlen vom ', '')
    cov["Datum"] = datum_zeile[:10]
    datum_zeile = datum_zeile[10:].replace(
        ' (Stand: ', '').replace(' Uhr)', '')
    if len(datum_zeile) == 1:
        datum_zeile = '0' + datum_zeile
    cov["Zeit"] = datum_zeile + ':00:00'
    # print(f'\nfallzahlen_zeile 1 : {fallzahlen_zeile}')
    fallzahlen_zeile = \
        fallzahlen_zeile.replace('Fallzahlen für Stuttgart', ''). \
        replace('Bestätigte Fälle:', ''). \
        replace('Neuinfektionen innerhalb der letzten 7 Tage in Summe', ''). \
        replace('7-Tage-Inzidenz, also Neuinfektionen innerhalb der ', ''). \
        replace('letzten 7 Tage pro 100.000 Einwohner', ''). \
        replace('Verstorbene', '')
    fallzahlen_zeile = fallzahlen_zeile.split(':')
    fallzahlen_zeile = [n.replace('\xa0', '') for n in fallzahlen_zeile]
    fallzahlen_zeile = [n.replace('.', '') for n in fallzahlen_zeile]
    fallzahlen_zeile = [n.replace(',', '.') for n in fallzahlen_zeile]
    # print(f'\nfallzahlen_zeile 2 : {fallzahlen_zeile}')
    faelle = fallzahlen_zeile[0]
    neu7t = fallzahlen_zeile[1]
    inz7t = fallzahlen_zeile[2]
    tote = fallzahlen_zeile[3]
    # print(f'\nfaelle : {faelle}\n')
    # print(f'neu7t : {neu7t}\n')
    # print(f'inz7t : {inz7t}\n')
    # print(f'tote : {tote}\n')
    cov["Faelle_Abs"] = int(faelle[:faelle.find(' Personen')])
    cov["Faelle_Delta"] = int(
        faelle[faelle.find('plus')+5:faelle.find(' gegenüber')])
    cov["Neu7t_Abs"] = int(neu7t[:neu7t.find(' Personen')])
    neu7t = neu7t.split(' ')
    cov["Neu7t_Vortag"] = int(neu7t[-1].replace(')', ''))
    cov["Inz7t_Abs"] = float(inz7t[:inz7t.find(' (gegenüber')])
    inz7t = inz7t.split(' ')
    cov["Inz7t_Vortag"] = float(inz7t[-1].replace(')', ''))
    cov["Tote_Abs"] = int(tote[:tote.find(' Personen')])
    if tote.count('(+'):
        cov["Tote_Delta"] = int(
            tote[tote.find('(+')+2:tote.find(' gegenüber')])
    if tote.count('plus'):
        cov["Tote_Delta"] = int(
            tote[tote.find('plus')+5:tote.find(' gegenüber')])
    # print(f'\ncov : {cov}\n')


def aufbereitung_daten_RKI(datum_zeile, fallzahlen_zeilen):
    datum_zeile = datum_zeile.split(',')
    datum = datum_zeile[0].split(' ')[-1]
    parts = datum.split('.')
    for n in range(2):
        if len(parts[n]) == 1:
            parts[n] = '0' + parts[n] + '.'
        else:
            parts[n] = parts[n] + '.'
    datum = ''
    for n in parts:
        datum += n
    zeit = datum_zeile[1].replace(' Uhr)', '').split(' ')[-1] + ":00"
    for zeile in fallzahlen_zeilen:
        # print(zeile)
        cov_temp["Datum"] = datum
        cov_temp["Zeit"] = zeit
        cov_temp["Gebiet"] = zeile[0].replace('\xad', '').replace('\n', '')
        if cov_temp["Gebiet"] == 'Gesamt':
            cov_temp["Gebiet"] += ' Deutschland'
        cov_temp["Anzahl"] = int(zeile[1].replace('.', ''))
        cov_temp["Delta"] = int(zeile[2].replace('.', ''))
        cov_temp["Anz7t"] = int(zeile[3].replace('.', ''))
        cov_temp["Inz7t"] = float(zeile[4].replace('.', '').replace(',', '.'))
        cov_temp["Tote"] = int(zeile[5].replace('.', ''))
        # print(cov_temp)
        covRKI.append(dict(cov_temp))
    # print(f'\ncovRKI : {covRKI}\n')


def druckdaten():
    anz = 63
    msg = f'\n'
    msg += f'{anz*"-"}'
    msg += f'\nCORONA FALLZAHLEN STUTTGART\n' \
        f'(Abfragezeitpunkt: {aktuelles_datum()} ' \
        f'{aktuelle_uhrzeit()})\n'
    for key, value in cov.items():
        msg += f'{key:16s} : {value:>10}\n'
    msg += f'{anz*"-"}'
    msg += f'\nCORONA FALLZAHLEN RKI\n' \
        f'(Aktualisierungzeitpunkt: {covRKI[0]["Datum"]} ' \
        f'{covRKI[0]["Zeit"]})\n'
    msg += f'{" ":<23s}{"Anzahl":>10s}{"Delta":>8s}{"Anz7t":>8s}' \
        f'{"Inz7t":>6s}{"Tote":>8s}\n'
    for z in covRKI:
        if z["Gebiet"] in print_gebiet:
            msg += f'{z["Gebiet"]:<23s}'
            msg += f'{z["Anzahl"]:>10,d}'
            msg += f'{z["Delta"]:>8,d}'
            msg += f'{z["Anz7t"]:>8,d}'
            msg += f'{z["Inz7t"]:>6,.0f}'
            msg += f'{z["Tote"]:>8,d}\n'
    msg += f'{anz*"-"}\n'
    return msg


def _main():
    show_header(G_HEADER_1, G_HEADER_2, __file__, G_OS)
    stop = False
    conn = create_connection(database)
    if not conn:
        stop = True
    if not stop:
        init_database(conn)
        if einlesen_webdaten():
            if einlesen_webdaten_RKI():
                print(f'{druckdaten()}')
                db_update(conn)
                conn.close()
    else:
        print(f'Programm abgebrochen\n')


if __name__ == "__main__":
    t0 = time.perf_counter()
    _main()
    print(f'\nLaufzeit : {time.perf_counter() - t0:8,.4f} Sekunden\n')
    time.sleep(0.1)
