#!/usr/bin/env python3

# Programm     : tankstellen.py
# Version      : 1.00
# SW-Stand     : 21.05.2022
# Autor        : Kanopus1958
# Beschreibung : Ermittlung aktueller Treibstoffpreise

import os
import requests
from bs4 import BeautifulSoup
import time
from rwm_mod01 import show_header, datum_zu_ts, ts_zu_datum
from rwm_class01 import MyDB

G_OS = ('Windows')
G_HEADER_1 = '# Aktuelle Treibstoffpreise au'
G_HEADER_2 = 'sgewaehlter Tankstellen      #'

database = r'O:\01_Daten\DatenLocal\Datenbanken\SQLite\treibstoffpreise.db'
station_ids = ['147028#', '28100', '52998']
tankstellen = []


class Tankstelle():
    def __init__(self, url):
        self.daten = {'Url': url, 'Name': '', 'Strasse': '', 'Plz': '',
                      'Stadt': '', 'Aktualisierung': '',
                      'Treibstoffe': {}}

    def preise_ermitteln(self):
        URL_basis = f'https://www.clever-tanken.de'
        URL_detail = f'/tankstelle_details/'
        page = requests.get(URL_basis + URL_detail + self.daten['Url'])
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
        tankstelle = (self.daten["Url"], self.daten["Name"],
                      self.daten["Plz"],
                      self.daten["Stadt"], self.daten["Strasse"])
        tankstelle_id = self.create_tankstelle(tankstelle)
        # print(f'tankstelle_id = {tankstelle_id}')
        for k in self.daten['Treibstoffe'].keys():
            treibstoff = (k,)
            treibstoff_id = self.create_treibstoff(treibstoff)
            # print(f'treibstoff_id = {treibstoff_id}')
            preis = (tankstelle_id, treibstoff_id,
                     datum_zu_ts(self.daten["Aktualisierung"] + ':00'),
                     self.daten["Treibstoffe"][k],
                     self.daten["Aktualisierung"])
            preis_id = self.create_preis(preis)
            # print(f'preis_id = {preis_id}')
        return

    def create_tankstelle(self, tankstelle):
        lastkey = None
        sql_select = ''' SELECT * FROM tankstellen WHERE
                         Url = ? '''
        sql_param = [tankstelle[0], ]
        datensatz = db.dbReadOneRow(sql_select, sql_param)
        if datensatz:
            lastkey = datensatz[0]
        else:
            sql_insupddel = ''' INSERT INTO tankstellen(Url,Name,
                                Plz,Stadt,Strasse)
                                VALUES(?,?,?,?,?) '''
            sql_param = tankstelle
            lastkey = db.dbInsUpdDelRow(sql_insupddel, sql_param)
        return lastkey

    def create_treibstoff(self, treibstoff):
        lastkey = None
        sql_select = ''' SELECT * FROM treibstoffe WHERE
                Bezeichnung = ? '''
        sql_param = [treibstoff[0], ]
        datensatz = db.dbReadOneRow(sql_select, sql_param)
        if datensatz:
            lastkey = datensatz[0]
        else:
            sql_insupddel = ''' INSERT INTO treibstoffe(Bezeichnung)
                                VALUES(?) '''
            sql_param = [treibstoff[0], ]
            lastkey = db.dbInsUpdDelRow(sql_insupddel, sql_param)
        return lastkey

    def create_preis(self, preis):
        lastkey = None
        sql_select = ''' SELECT * FROM preise WHERE
                         Tankstelle_Id = ? AND
                         Treibstoff_Id = ? AND
                         Timestamp = ? '''
        sql_param = preis[:3]
        datensatz = db.dbReadOneRow(sql_select, sql_param)
        if datensatz:
            lastkey = datensatz[0]
        else:
            sql_insupddel = ''' INSERT INTO preise(Tankstelle_Id,
                                Treibstoff_Id,Timestamp,Preis,Datum_Zeit)
                                VALUES(?,?,?,?,?) '''
            sql_param = preis
            lastkey = db.dbInsUpdDelRow(sql_insupddel, sql_param)
        return lastkey


def init_database():
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
    db.dbCreateDropTable(sql_create_tankstellen_table)
    db.dbCreateDropTable(sql_create_treibstoffe_table)
    db.dbCreateDropTable(sql_create_preise_table)
    return True


def _main():
    global db
    show_header(G_HEADER_1, G_HEADER_2, __file__, G_OS)
    if not os.path.isfile(database):
        print(f'\nFehler : Datenbankdatei existiert nicht\nError  : '
              f'"{database}"')
        print(f'Programm wurde abgebrochen')
        return False
    db = MyDB(database)
    init_database()
    for url in station_ids:
        tankstellen.append(Tankstelle(url))
    for tanke in tankstellen:
        tanke.preise_ermitteln()
        tanke.drucken()
        tanke.db_update()


if __name__ == "__main__":
    t0 = time.perf_counter()
    _main()
    print(f'\nLaufzeit : {time.perf_counter() - t0:8,.4f} Sekunden\n')
