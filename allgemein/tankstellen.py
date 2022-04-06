#!/usr/bin/env python3

# Programm     : tankstellen.py
# Version      : 1.00
# SW-Stand     : 21.03.2022
# Autor        : Kanopus1958
# Beschreibung : Ermittlung aktueller Treibstoffpreise

from os import path
import requests
from bs4 import BeautifulSoup
import time
import sqlite3
from sqlite3 import Error
from rwm_mod01 import show_header, datum_zu_ts, ts_zu_datum

G_OS = ('Windows')
G_HEADER_1 = '# Aktuelle Treibstoffpreise au'
G_HEADER_2 = 'sgewaehlter Tankstellen      #'

database = r'O:\01_Daten\DatenLocal\Datenbanken\SQLite\treibstoffpreise.db'
station_ids = ['147028#', '28100', '52998']
tankstellen = []


class tankstelle():
    def __init__(self, id):
        self.daten = {'Id': id, 'Name': '', 'Strasse': '', 'Plz': '',
                      'Stadt': '', 'Aktualisierung': '',
                      'Treibstoffe': {}}

    def preise_ermitteln(self):
        URL_basis = f'https://www.clever-tanken.de'
        URL_detail = f'/tankstelle_details/'
        page = requests.get(URL_basis + URL_detail + self.daten['Id'])
        if page.status_code != 200:
            print(f'Return-Code der HTML-Seite = {page.status_code}\n')
            return page.status_code
        soup = BeautifulSoup(page.content, 'html.parser')
        self.daten['Name'] = soup.find('span', class_="strong-title").text
        t_adresse = soup.find(
            'div', itemprop="http://schema.org/address").text.split('\n')
        t_adresse = [n for n in t_adresse if n != '']
        self.daten['Strasse'] = t_adresse[0]
        self.daten['Plz'] = t_adresse[1]
        self.daten['Stadt'] = t_adresse[2]
        zeit = soup.find('div', class_="price-footer row col-12 "
                         "text text-color-ice-blue "
                         "d-flex flex-column").text.split('\n')
        self.daten['Aktualisierung'] = zeit[1].replace(
            'Letzte MTS-K Preisänderung: ', '')
        fuels = soup.find_all(
            'div', class_="price-row row d-flex align-items-center")
        for fuel in fuels:
            fuel_type = fuel.find('div', class_='price-type-name').text
            preis_komponenten = fuel.find(
                'div', class_='price-field').text.split('\n')
            preis_komponenten = [n for n in preis_komponenten if n != '']
            preis = "".join(preis_komponenten)
            try:
                fuel_price = float(preis)
                self.daten['Treibstoffe'][fuel_type] = fuel_price
            except(ValueError):
                pass
        return

    def drucken(self):
        # print(f'\nself.daten : {self.daten}')
        print(f'\n{self.daten["Name"]} ( {self.daten["Plz"]} '
              f'{self.daten["Stadt"]} , {self.daten["Strasse"]} )')
        print(f'{self.daten["Aktualisierung"]}')
        # print(f'{self.daten["Aktualisierung"]} '
        #       f'({datum_zu_ts(self.daten["Aktualisierung"] + ":00")})')
        for k in self.daten['Treibstoffe'].keys():
            print(f'   {k:<20s} : {self.daten["Treibstoffe"][k]:>8.3f} €')
        return

    def db_update(self, conn):
        tankstelle = (self.daten["Id"], self.daten["Name"],
                      self.daten["Plz"],
                      self.daten["Stadt"], self.daten["Strasse"])
        tankstelle_id = create_tankstelle(conn, tankstelle)
        if tankstelle_id is None:
            sql = f''' SELECT * FROM tankstellen WHERE
                    Url = "{self.daten["Id"]}" '''
            tankstelle_id = lese_datensatz(conn, sql)[0]
        # print(f'tankstelle_id = {tankstelle_id}')
        for k in self.daten['Treibstoffe'].keys():
            treibstoff = (k,)
            treibstoff_id = create_treibstoff(conn, treibstoff)
            if treibstoff_id is None:
                sql = f''' SELECT * FROM treibstoffe WHERE
                        Bezeichnung = "{k}" '''
                treibstoff_id = lese_datensatz(conn, sql)[0]
                # print(f'treibstoff_id = {treibstoff_id}')
            preis = (tankstelle_id, treibstoff_id,
                     datum_zu_ts(self.daten["Aktualisierung"] + ':00'),
                     self.daten["Treibstoffe"][k],
                     self.daten["Aktualisierung"])
            sql = f''' SELECT * FROM preise WHERE
                        Tankstelle_Id = "{preis[0]}" AND
                        Treibstoff_Id = "{preis[1]}" AND
                        Timestamp = "{preis[2]}"'''
            if not lese_datensatz(conn, sql):
                preis_id = create_preis(conn, preis)
        return


def create_connection(db_file):
    if path.isfile(db_file):
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
    sql_create_tankstellen_table = '''
    CREATE TABLE IF NOT EXISTS tankstellen (
        Id      INTEGER PRIMARY KEY ASC AUTOINCREMENT,
        Url     TEXT    NOT NULL
                        UNIQUE ON CONFLICT ROLLBACK,
        Name    TEXT    NOT NULL,
        Plz     TEXT    NOT NULL,
        Stadt   TEXT    NOT NULL,
        Strasse TEXT    NOT NULL
    );
    '''
    sql_create_treibstoffe_table = '''
    CREATE TABLE IF NOT EXISTS treibstoffe (
        Id          INTEGER PRIMARY KEY ASC AUTOINCREMENT,
        Bezeichnung TEXT    UNIQUE ON CONFLICT ROLLBACK
                            NOT NULL
    );
    '''
    sql_create_preise_table = '''
    CREATE TABLE IF NOT EXISTS preise (
        Id            INTEGER PRIMARY KEY ASC AUTOINCREMENT,
        Tankstelle_Id INTEGER NOT NULL,
        Treibstoff_Id INTEGER NOT NULL,
        Timestamp     REAL NOT NULL,
        Preis         REAL NOT NULL,
        Datum_Zeit    TEXT NOT NULL,
        FOREIGN KEY (
            Tankstelle_Id
        )
        REFERENCES tankstellen (Id),
        FOREIGN KEY (
            Treibstoff_Id
        )
        REFERENCES treibstoffe (Id)
    );
    '''
    create_table(conn, sql_create_tankstellen_table)
    create_table(conn, sql_create_treibstoffe_table)
    create_table(conn, sql_create_preise_table)
    return True


def create_table(conn, create_table_sql):
    try:
        cur = conn.cursor()
        cur.execute(create_table_sql)
        conn.commit()
        cur.close()
    except Error as e:
        print(f'\nFehler : Neuanlage Tabelle fehlgeschlagen\nError : "{e}"')


def create_tankstelle(conn, tankstelle):
    lastkey = None
    sql = ''' INSERT INTO tankstellen(Url,Name,Plz,Stadt,Strasse)
              VALUES(?,?,?,?,?) '''
    # print(f'Tankstelle : {tankstelle}')
    try:
        cur = conn.cursor()
        cur.execute(sql, tankstelle)
        conn.commit()
        lastkey = cur.lastrowid
        cur.close()
    except Error as e:
        # print(f'\nInfo : Tankstelle existiert schon \nError : "{e}"\n')
        pass
    return lastkey


def create_treibstoff(conn, treibstoff):
    lastkey = None
    sql = ''' INSERT INTO treibstoffe(Bezeichnung)
              VALUES(?) '''
    # print(f'Treibstoff : {treibstoff}')
    try:
        cur = conn.cursor()
        cur.execute(sql, treibstoff)
        conn.commit()
        lastkey = cur.lastrowid
        cur.close()
    except Error as e:
        # print(f'\nInfo : Treibstoff existiert schon \nError : "{e}"\n')
        pass
    return lastkey


def create_preis(conn, preis):
    lastkey = None
    sql = ''' INSERT INTO
           preise(Tankstelle_Id,Treibstoff_Id,Timestamp,Preis,Datum_Zeit)
           VALUES(?,?,?,?,?) '''
    # print(f'Preiseintrag : {preis}')
    try:
        cur = conn.cursor()
        cur.execute(sql, preis)
        conn.commit()
        lastkey = cur.lastrowid
        cur.close()
    except Error as e:
        print(f'\nFehler : Preiseintrag nicht erfolgreich\nError : "{e}"\n')
    return lastkey


def lese_datensatz(conn, sql):
    cur = conn.cursor()
    # print(f'SQL = {sql}')
    datensatz = cur.execute(sql).fetchone()
    # print(f'datensatz = {datensatz}')
    if datensatz is not None:
        return datensatz
    else:
        return None


def _main():
    show_header(G_HEADER_1, G_HEADER_2, __file__, G_OS)
    stop = False
    conn = create_connection(database)
    if not conn:
        stop = True
    if not stop:
        init_database(conn)
        for id in station_ids:
            tankstellen.append(tankstelle(id))
        for tanke in tankstellen:
            tanke.preise_ermitteln()
            tanke.drucken()
            tanke.db_update(conn)
        conn.close()
    else:
        print(f'Programm abgebrochen\n')


if __name__ == "__main__":
    t0 = time.perf_counter()
    _main()
    print(f'\nLaufzeit : {time.perf_counter() - t0:8,.4f} Sekunden\n')
