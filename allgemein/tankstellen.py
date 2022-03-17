#!/usr/bin/env python3

# Programm     : tankstellen.py
# Version      : 1.00
# SW-Stand     : 18.03.2022
# Autor        : Kanopus1958
# Beschreibung : Ermittlung aktueller Treibstoffpreise

import sys
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

    def db_update(self):
        with create_connection(database)as conn:
            tankstelle = (self.daten["Id"], self.daten["Name"],
                          self.daten["Plz"],
                          self.daten["Stadt"], self.daten["Strasse"])
            tankstelle_id = create_tankstelle(conn, tankstelle)
            if tankstelle_id is None:
                sql = f''' SELECT * FROM tankstellen WHERE
                        Url = "{self.daten["Id"]}" '''
                tankstelle_id = get_primk(conn, sql)
            # print(f'tankstelle_id = {tankstelle_id}')
            for k in self.daten['Treibstoffe'].keys():
                treibstoff = (k,)
                treibstoff_id = create_treibstoff(conn, treibstoff)
                if treibstoff_id is None:
                    sql = f''' SELECT * FROM treibstoffe WHERE
                            Bezeichnung = "{k}" '''
                    treibstoff_id = get_primk(conn, sql)
                    # print(f'treibstoff_id = {treibstoff_id}')
                preis = (tankstelle_id, treibstoff_id,
                         datum_zu_ts(self.daten["Aktualisierung"] + ':00'),
                         self.daten["Treibstoffe"][k],
                         self.daten["Aktualisierung"])
                if not check_preis(conn, preis):
                    preis_id = create_preis(conn, preis)
        return


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    return conn


def init_database():
    sql_create_tankstellen_table = """
    CREATE TABLE IF NOT EXISTS tankstellen (
        id      INTEGER PRIMARY KEY ASC AUTOINCREMENT,
        Url     TEXT    NOT NULL
                        UNIQUE ON CONFLICT ROLLBACK,
        Name    TEXT    NOT NULL,
        Plz     TEXT    NOT NULL,
        Stadt   TEXT    NOT NULL,
        Strasse TEXT    NOT NULL
    );
    """
    sql_create_treibstoffe_table = """
    CREATE TABLE IF NOT EXISTS treibstoffe (
        id          INTEGER PRIMARY KEY ASC AUTOINCREMENT,
        Bezeichnung TEXT    UNIQUE ON CONFLICT ROLLBACK
                            NOT NULL
    );
    """
    sql_create_preise_table = """
    CREATE TABLE IF NOT EXISTS preise (
        id            INTEGER PRIMARY KEY ASC AUTOINCREMENT,
        tankstelle_id INTEGER NOT NULL,
        treibstoff_id INTEGER NOT NULL,
        timestamp     DECIMAL,
        preis         DECIMAL,
        datum_zeit    TEXT,
        FOREIGN KEY (
            tankstelle_id
        )
        REFERENCES tankstellen (id),
        FOREIGN KEY (
            treibstoff_id
        )
        REFERENCES treibstoffe (id)
    );
    """
    try:
        with create_connection(database) as conn:
            create_table(conn, sql_create_tankstellen_table)
            create_table(conn, sql_create_treibstoffe_table)
            create_table(conn, sql_create_preise_table)
            return True
    except Error as e:
        print(f'Error! cannot create the database connection. {e}')
        return False


def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def create_tankstelle(conn, tankstelle):
    sql = ''' INSERT INTO tankstellen(Url,Name,Plz,Stadt,Strasse)
              VALUES(?,?,?,?,?) '''
    # print(f'Tankstelle : {tankstelle}')
    cur = conn.cursor()
    try:
        cur.execute(sql, tankstelle)
        conn.commit()
        return cur.lastrowid
    except Error as e:
        # print(f'Tankstelle existiert schon : {e}')
        return None


def create_treibstoff(conn, treibstoff):
    sql = ''' INSERT INTO treibstoffe(Bezeichnung)
              VALUES(?) '''
    # print(f'Treibstoff : {treibstoff}')
    cur = conn.cursor()
    try:
        cur.execute(sql, treibstoff)
        conn.commit()
        return cur.lastrowid
    except Error as e:
        # print(f'Treibstoff existiert schon : {e}')
        return None


def create_preis(conn, preis):
    sql = ''' INSERT INTO
           preise(tankstelle_id,treibstoff_id,timestamp,preis,datum_zeit)
           VALUES(?,?,?,?,?) '''
    # print(f'Preiseintrag : {preis}')
    cur = conn.cursor()
    try:
        cur.execute(sql, preis)
        conn.commit()
        return cur.lastrowid
    except Error as e:
        print(f'Preiseintrag existiert schon : {e}')
        return None


def get_primk(conn, sql):
    cur = conn.cursor()
    # print(f'SQL = {sql}')
    datensatz = cur.execute(sql).fetchone()
    # print(f'datensatz = {datensatz}')
    if datensatz is not None:
        return datensatz[0]
    else:
        return None


def check_preis(conn, preis):
    cur = conn.cursor()
    sql = f''' SELECT * FROM preise WHERE
                tankstelle_id = "{preis[0]}" AND
                treibstoff_id = "{preis[1]}" AND
                timestamp = "{preis[2]}"'''
    # print(f'\nSQL = {sql}')
    datensatz = cur.execute(sql).fetchone()
    # print(f'datensatz = {datensatz}')
    if datensatz is not None:
        return True
    else:
        return False


def _main():
    show_header(G_HEADER_1, G_HEADER_2, __file__, G_OS)
    if not init_database():
        sys.exit(1)
    for id in station_ids:
        tankstellen.append(tankstelle(id))
    for tanke in tankstellen:
        tanke.preise_ermitteln()
        tanke.drucken()
        tanke.db_update()


if __name__ == "__main__":
    t0 = time.perf_counter()
    _main()
    print(f'\nLaufzeit : {time.perf_counter() - t0:8,.4f} Sekunden\n')
