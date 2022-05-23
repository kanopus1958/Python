#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Programm     : db_sqlite.py
# Version      : 1.00
# SW-Stand     : 19.05.2022
# Autor        : Kanopus1958
# Beschreibung : Test verschiendener SQLite DB-Funktionen

import os
import time
from rwm_mod01 import show_header
from rwm_class01 import MyDB

G_OS = ('Windows')
G_HEADER_1 = '# SQLite Datenbank Funktionen '
G_HEADER_2 = 'in Python                    #'

dbPath = r'O:\01_Daten\DatenLocal\Datenbanken\SQLite'
dbFile = r'xxxTESTxxx.db'
csvFile = r'TEST.csv'


def _main():
    show_header(G_HEADER_1, G_HEADER_2, __file__, G_OS)
    dbFullPath = dbPath + '\\' + dbFile
    if not os.path.isfile(dbFullPath):
        print(f'\nFehler : Datenbankdatei existiert nicht\nError  : '
              f'"{dbFullPath}"')
        print(f'Programm wurde abgebrochen')
        return False

    pers = MyDB(dbFullPath)

    sql = '''
    DROP TABLE IF EXISTS droptabelle;
    '''
    print(f"Return-Code DROP table   : {pers.dbCreateDropTable(sql)}")

    sql = '''
    CREATE TABLE IF NOT EXISTS personen (
        Id      INTEGER PRIMARY KEY ASC AUTOINCREMENT,
        Name    TEXT    NOT NULL,
        Vorname TEXT    NOT NULL,
        Plz     TEXT    NOT NULL,
        Stadt   TEXT    NOT NULL,
        Strasse TEXT    NOT NULL,
        Hausnr  TEXT    NOT NULL,
        Zahl    REAL    NOT NULL);
    '''
    print(f"Return-Code CREATE table : {pers.dbCreateDropTable(sql)}")

    tablesviews = pers.dbGetTableViewNames()
    print(f"Tables und Views         : {tablesviews}")

    print(f"Table Sequences          : {pers.GetTableSequences()}")

    sql = '''
    SELECT * FROM view_personen;
    '''
    colnames = pers.dbGetColNames(sql)
    print(f"Spaltennamen             : {colnames}")

    sql = '''
    INSERT INTO personen (Name,Vorname,Plz,Stadt,Strasse,Hausnr,Zahl)
                VALUES   (?,?,?,?,?,?,?);
    '''
    sql_param = ['Weiss', 'Rolf', '70329',
                 'Stuttgart', 'Uhlbacher Strasse', '217', 12.345]
    print(f"INSERT Last Index        : {pers.dbInsUpdDelRow(sql, sql_param)}")

    sql = '''
    UPDATE personen
    SET Name = ?,
        Vorname = ?,
        Plz = ?,
        Stadt = ?,
        Strasse = ?,
        Hausnr = ?,
        Zahl = ?
    WHERE Id = ?;
    '''
    sql_param = ['Hess', 'Angelika', '70329',
                 'Stuttgart', 'Uhlbacher Strasse', '217', 98.765, 91]
    print(f"UPDATE Last Index        : {pers.dbInsUpdDelRow(sql, sql_param)}")

    sql = '''
    DELETE FROM personen
    WHERE Id = ?;
    '''
    sql_param = [90, ]
    print(f"DELETE Last Index        : {pers.dbInsUpdDelRow(sql, sql_param)}")

    sql = '''
    SELECT * FROM personen WHERE Name = ?;
    '''
    sql_param = ['Hess', ]
    print(f"SELECT One Datensatz     : {pers.dbReadOneRow(sql, sql_param)}")

    sql = '''
    SELECT * FROM personen;
    '''
    sql_param = []
    table = pers.dbReadAllRows(sql, sql_param)
    # print(table)

    csvFullPath = dbPath + '\\' + csvFile
    pers.dbTableToCSV(csvFullPath, "view_personen")


if __name__ == "__main__":
    t0 = time.perf_counter()
    _main()
    print(f'\nLaufzeit : {time.perf_counter() - t0:8,.4f} Sekunden\n')
    time.sleep(0.1)
