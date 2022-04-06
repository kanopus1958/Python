#!/usr/bin/env python3

# Programm     : corona_stgt.py
# Version      : 1.00
# SW-Stand     : 06.04.2022
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

G_OS = ('Windows')
G_HEADER_1 = '# Corona Fallzahlen für Stuttg'
G_HEADER_2 = 'art                          #'

URL = f'https://www.stuttgart.de/leben/gesundheit/' \
      f'corona/fallzahlen-und-impfungen.php'
database = r'O:\01_Daten\DatenLocal\Datenbanken\SQLite\corona_stgt.db'

cov = {'Datum': "01.01.2022", 'Zeit': "00:00:00",
       'Faelle_Abs': 0, 'Faelle_Delta': 0,
       'Neu7t_Abs': 0, 'Neu7t_Vortag': 0,
       'Inz7t_Abs': 0.0, 'Inz7t_Vortag': 0.0,
       'Tote_Abs': 0, 'Tote_Delta': 0
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
    create_table(conn, sql_create_fallzahlen_table)
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
            print(f'\nInfo : Vermöegenseintrag '
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


def db_update(conn):
    datum_zeit = cov["Datum"] + ' ' + cov["Zeit"]
    datensatz_fallzahl = [cov["Datum"], datum_zu_ts(datum_zeit), datum_zeit,
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


def aufbereitung_daten(datum_zeile, fallzahlen_zeile):
    datum_zeile = datum_zeile.replace('Corona-Kennzahlen vom ', '')
    cov["Datum"] = datum_zeile[:10]
    datum_zeile = datum_zeile[10:].replace(
        ' (Stand: ', '').replace(' Uhr)', '')
    if len(datum_zeile) == 1:
        datum_zeile = '0' + datum_zeile
    cov["Zeit"] = datum_zeile + ':00:00'
    print(f'\nfallzahlen_zeile 1 : {fallzahlen_zeile}')
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
    print(f'\nfallzahlen_zeile 2 : {fallzahlen_zeile}')
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


def druckdaten():
    msg = f''
    msg += f'\nCORONA FALLZAHLEN Stuttgart\n' \
        f'(Abfragezeitpunkt: {aktuelles_datum()} ' \
        f'{aktuelle_uhrzeit()})\n'
    msg += f'{60*"-"}\n'
    for key, value in cov.items():
        msg += f'{key:12s} : {value:>10}\n'
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
            print(f'{druckdaten()}')
            db_update(conn)
            conn.close()
    else:
        print(f'Programm abgebrochen\n')


if __name__ == "__main__":
    t0 = time.perf_counter()
    _main()
    print(f'\nLaufzeit : {time.perf_counter() - t0:8,.4f} Sekunden\n')
