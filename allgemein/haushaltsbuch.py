#!/usr/bin/env python3

# Programm     : haushaltsbuch.py
# Version      : 1.00
# SW-Stand     : 26.04.2022
# Autor        : Kanopus1958
# Beschreibung : Haushaltsbuch (TKinter-GUI it SQLite-DB)

import os
from tkinter import *
from tkinter import ttk
import sqlite3
from sqlite3 import Error

database = r'O:\01_Daten\DatenLocal\Datenbanken\SQLite\finanzanlage.db'

winTitle = 'Anlage-Vermögen R.W.'
winWidth = 312
winHeight = 272


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


def lese_datensaetze(conn, sql, sql_param):
    cur = conn.cursor()
    rows = cur.execute(sql, sql_param).fetchall()
    if rows is not None:
        return rows
    else:
        return None


def get_vermoeg(conn):
    sql = f''' SELECT * FROM vermoegen ORDER BY Timestamp ASC'''
    sql_param = []
    datensaetze = lese_datensaetze(conn, sql, sql_param)
    if datensaetze:
        return datensaetze
    else:
        return False


class MyFrame:

    def __init__(self, root):
        # for row in verm:
        #     print(row)
        # print(len(verm))
        # print(verm[len(verm)-1])
        self.txt00Var = StringVar()
        self.txt01Var = StringVar()
        self.txt02Var = StringVar()
        self.txt03Var = StringVar()
        self.txt04Var = StringVar()
        self.txt05Var = StringVar()
        self.txt06Var = StringVar()
        self.txt07Var = StringVar()
        self.txt08Var = StringVar()

        self.pointer = len(verm) - 1
        self.SetCellContent(self.pointer)

        root.title(winTitle)
        scrWidth = root.winfo_screenwidth()
        scrHeight = root.winfo_screenheight()
        x_cor = int((scrWidth/2) - (winWidth/2))
        y_cor = int((scrHeight/2) - (winHeight/2))
        root.geometry("{}x{}+{}+{}".format(winWidth,
                      winHeight, x_cor, y_cor))
        root.minsize(winWidth, winHeight)
        root.maxsize(winWidth, winHeight)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        content = ttk.Frame(root, borderwidth=5, relief="sunken",
                            padding=(3, 3, 3, 3))

        lbl00 = ttk.Label(content, text="Id")
        lbl01 = ttk.Label(content, text="Datum")
        lbl02 = ttk.Label(content, text="Timestamp")
        lbl03 = ttk.Label(content, text="Datum_Zeit")
        lbl04 = ttk.Label(content, text="Konto")
        lbl05 = ttk.Label(content, text="Kosten")
        lbl06 = ttk.Label(content, text="Wert")
        lbl07 = ttk.Label(content, text="Invest")
        lbl08 = ttk.Label(content, text="G_V")

        txt00 = ttk.Entry(content, textvariable=self.txt00Var, justify=RIGHT)
        txt01 = ttk.Entry(content, textvariable=self.txt01Var, justify=RIGHT)
        txt02 = ttk.Entry(content, textvariable=self.txt02Var, justify=RIGHT)
        txt03 = ttk.Entry(content, textvariable=self.txt03Var, justify=RIGHT)
        txt04 = ttk.Entry(content, textvariable=self.txt04Var, justify=RIGHT)
        txt05 = ttk.Entry(content, textvariable=self.txt05Var, justify=RIGHT)
        txt06 = ttk.Entry(content, textvariable=self.txt06Var, justify=RIGHT)
        txt07 = ttk.Entry(content, textvariable=self.txt07Var, justify=RIGHT)
        txt08 = ttk.Entry(content, textvariable=self.txt08Var, justify=RIGHT)

        btn00 = ttk.Button(content, text="|< First", command=self.btn00_Click)
        btn01 = ttk.Button(content, text="< Prev", command=self.btn01_Click)
        btn02 = ttk.Button(content, text="Next >", command=self.btn02_Click)
        btn03 = ttk.Button(content, text="Last >|", command=self.btn03_Click)
        btn05 = ttk.Button(content, text="Refresh DB",
                           command=self.btn05_Click)
        btn08 = ttk.Button(content, text="Exit")

        content.grid(column=0, row=0, sticky=(N, S, E, W))

        lbl00.grid(row=0, column=0, sticky=(W))
        lbl01.grid(row=1, column=0, sticky=(W))
        lbl02.grid(row=2, column=0, sticky=(W))
        lbl03.grid(row=3, column=0, sticky=(W))
        lbl04.grid(row=4, column=0, sticky=(W))
        lbl05.grid(row=5, column=0, sticky=(W))
        lbl06.grid(row=6, column=0, sticky=(W))
        lbl07.grid(row=7, column=0, sticky=(W))
        lbl08.grid(row=8, column=0, sticky=(W))

        txt00.grid(row=0, column=1)
        txt01.grid(row=1, column=1)
        txt02.grid(row=2, column=1)
        txt03.grid(row=3, column=1)
        txt04.grid(row=4, column=1)
        txt05.grid(row=5, column=1)
        txt06.grid(row=6, column=1)
        txt07.grid(row=7, column=1)
        txt08.grid(row=8, column=1)

        btn00.grid(row=0, column=2)
        btn01.grid(row=1, column=2)
        btn02.grid(row=2, column=2)
        btn03.grid(row=3, column=2)
        btn05.grid(row=5, column=2)
        btn08.grid(row=8, column=2)

        content.rowconfigure(0, pad=5)
        content.rowconfigure(1, pad=5)
        content.rowconfigure(2, pad=5)
        content.rowconfigure(3, pad=5)
        content.rowconfigure(4, pad=5)
        content.rowconfigure(5, pad=5)
        content.rowconfigure(6, pad=5)
        content.rowconfigure(7, pad=5)
        content.rowconfigure(8, pad=5)
        content.columnconfigure(0, pad=10)
        content.columnconfigure(1, pad=0)
        content.columnconfigure(2, pad=40)

        btn08.bind(sequence='<ButtonPress-1>',
                   func=lambda e: root.destroy())

        btn05.focus()

    def btn00_Click(self, *args):
        self.pointer = 0
        self.SetCellContent(self.pointer)

    def btn01_Click(self, *args):
        if self.pointer > 0:
            self.pointer -= 1
        self.SetCellContent(self.pointer)

    def btn02_Click(self, *args):
        if self.pointer < (len(verm) - 1):
            self.pointer += 1
        self.SetCellContent(self.pointer)

    def btn03_Click(self, *args):
        self.pointer = len(verm) - 1
        self.SetCellContent(self.pointer)

    def btn05_Click(self, *args):
        global verm
        verm = list(get_vermoeg(conn))
        if verm:
            self.pointer = len(verm) - 1
            self.SetCellContent(self.pointer)

    def SetCellContent(self, poin):
        row = list(verm[poin])
        for i in range(0, 4):
            row[i] = str(row[i])
        for i in range(4, 9):
            row[i] = f"{row[i]:,}".replace('.', '#').replace(
                ',', '.').replace('#', ',') + ' €'
        self.txt00Var.set(row[0])
        self.txt01Var.set(row[1])
        self.txt02Var.set(row[2])
        self.txt03Var.set(row[3])
        self.txt04Var.set(row[4])
        self.txt05Var.set(row[5])
        self.txt06Var.set(row[6])
        self.txt07Var.set(row[7])
        self.txt08Var.set(row[8])


def _main():
    global conn
    global verm
    conn = create_connection(database)
    if conn:
        verm = list(get_vermoeg(conn))
        if verm:
            root = Tk()
            MyFrame(root)
            root.mainloop()
        conn.close()


if __name__ == "__main__":
    _main()
