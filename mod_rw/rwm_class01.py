#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Programm     : rwm_class01.py
# Version      : 1.00
# SW-Stand     : 20.05.2022
# Autor        : Kanopus1958
# Beschreibung : Klassendefinitionen 01
#                MyDB

import sqlite3
from sqlite3 import Error


class MyDB:

    def __init__(self, database):
        self.database = database

    def dbGetTableViewNames(self):
        sql_select = '''
        SELECT tbl_name, type
        FROM sqlite_master
        WHERE type = "table" OR type = "view"
        ORDER BY type ASC, tbl_name ASC;
        '''
        try:
            with sqlite3.connect(self.database) as conn:
                cur = conn.cursor()
                tvall = cur.execute(sql_select).fetchall()
                return list(tvall)
        except Error as e:
            print(f'\nFehler : SELECT alle Tabellen und Views\nError : "{e}"')
            return False

    def GetTableSequences(self):
        sql_select = '''
        SELECT * FROM sqlite_sequence;
        '''
        try:
            with sqlite3.connect(self.database) as conn:
                cur = conn.cursor()
                sequences = cur.execute(sql_select).fetchall()
                return list(sequences)
        except Error as e:
            print(f'\nFehler : SELECT Sequences aller Tabellen\nError : "{e}"')
            return False

    def dbGetColNames(self, sql_select):
        try:
            with sqlite3.connect(self.database) as conn:
                cur = conn.cursor()
                data = cur.execute(sql_select)
                colnames = [col[0] for col in data.description]
                if len(colnames) > 0:
                    return list(colnames)
                else:
                    return None
        except Error as e:
            print(f'\nFehler : SELECT eines Datensatzes\nError : "{e}"')
            return False

    def dbCreateDropTable(self, sql_createdrop):
        try:
            with sqlite3.connect(self.database) as conn:
                cur = conn.cursor()
                cur.execute(sql_createdrop)
                conn.commit()
                cur.close()
                return True
        except Error as e:
            print(
                f'\nFehler : CREATE DROP Tabelle\nError : "{e}"')
            return False

    def dbReadOneRow(self, sql_select, sql_param):
        try:
            with sqlite3.connect(self.database) as conn:
                cur = conn.cursor()
                row = cur.execute(sql_select, sql_param).fetchone()
                if row is not None:
                    return row
                else:
                    return None
        except Error as e:
            print(f'\nFehler : SELECT eines Datensatzes\nError : "{e}"')
            return False

    def dbReadAllRows(self, sql_select, sql_param):
        try:
            with sqlite3.connect(self.database) as conn:
                cur = conn.cursor()
                rowsall = cur.execute(sql_select, sql_param).fetchall()
                if rowsall is not None:
                    return rowsall
                else:
                    return None
        except Error as e:
            print(f'\nFehler : SELECT aller Datensaetze\nError : "{e}"')
            return False

    def dbInsUpdDelRow(self, sql_insupddel, sql_param):
        try:
            with sqlite3.connect(self.database) as conn:
                cur = conn.cursor()
                cur.execute(sql_insupddel, sql_param)
                conn.commit()
                lastkey = cur.lastrowid
                cur.close()
                if lastkey > 0:
                    return lastkey
                else:
                    return None
        except Error as e:
            print(f'\nFehler : INSERT UPDATE DELETE '
                  f'Datensatz\nError : "{e}"\n')
            return False

    def dbTableToCSV(self, csvfile, tablename, delimiter=';'):
        sql = "SELECT * FROM " + tablename
        headers = self.dbGetColNames(sql)
        # print(headers)
        table = self.dbReadAllRows(sql, [])
        # print(table)
        buf = ""
        n = 0
        for header in headers:
            if n == 0:
                buf += header
            else:
                buf += delimiter + header
            n += 1
        buf += "\n"
        n = 0
        for row in table:
            li = 0
            line = ""
            for col in row:
                if li == 0:
                    line += str(col)
                else:
                    line += delimiter + str(col)
                li += 1
                line = line.replace(".", ",")
            if (len(table) - 1) == n:
                buf += line
            else:
                buf += line + "\n"
            n += 1
        print(buf)
        with open(csvfile, "w") as f:
            f.write(buf)
