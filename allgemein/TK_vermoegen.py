#!/usr/bin/env python3

# Programm     : TK_vermoegen.py
# Version      : 1.00
# SW-Stand     : 23.05.2022
# Autor        : Kanopus1958
# Beschreibung : Anzeige Depot-Vermögen (TKinter-GUI mit SQLite-DB)

import os
from tkinter import *
from tkinter import ttk
from rwm_class01 import MyDB

dbPath = r'O:\01_Daten\DatenLocal\Datenbanken\SQLite'
dbFile = r'finanzanlage.db'

winTitle = 'Anlage-Vermögen R.W.'
winWidth = 312
winHeight = 300
winStatusText = 'Version 1.00 (2022)'


class FrmMain:

    def __init__(self, root):
        self.txtIdVar = StringVar()
        self.txtDatumVar = StringVar()
        self.txtTimestampVar = StringVar()
        self.txtDatum_ZeitVar = StringVar()
        self.txtKontoVar = StringVar()
        self.txtKostenVar = StringVar()
        self.txtWertVar = StringVar()
        self.txtInvestVar = StringVar()
        self.txtG_VVar = StringVar()
        self.pointer = len(datatable) - 1
        self.RefreshFormData(self.pointer)

        root.title(winTitle)
        scrWidth = root.winfo_screenwidth()
        scrHeight = root.winfo_screenheight()
        x_cor = int((scrWidth/2) - (winWidth/2))
        y_cor = int((scrHeight/2) - (winHeight/2))
        root.geometry("{}x{}+{}+{}".format(winWidth,
                      winHeight, x_cor, y_cor))
        root.resizable(width=0, height=0)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        content = ttk.Frame(root, borderwidth=5, relief="sunken",
                            padding=(3, 3, 3, 3))

        lblId = ttk.Label(content, text="Id")
        lblDatum = ttk.Label(content, text="Datum")
        lblTimestamp = ttk.Label(content, text="Timestamp")
        lblDatum_Zeit = ttk.Label(content, text="Datum_Zeit")
        lblKonto = ttk.Label(content, text="Konto")
        lblKosten = ttk.Label(content, text="Kosten")
        lblWert = ttk.Label(content, text="Wert")
        lblInvest = ttk.Label(content, text="Invest")
        lblG_V = ttk.Label(content, text="G_V")
        lblStatus = ttk.Label(content, text=winStatusText, justify=RIGHT)

        txtId = ttk.Entry(content, textvariable=self.txtIdVar, justify=RIGHT)
        txtDatum = ttk.Entry(
            content, textvariable=self.txtDatumVar, justify=RIGHT)
        txtTimestamp = ttk.Entry(
            content, textvariable=self.txtTimestampVar, justify=RIGHT)
        txtDatum_Zeit = ttk.Entry(
            content, textvariable=self.txtDatum_ZeitVar, justify=RIGHT)
        txtKonto = ttk.Entry(
            content, textvariable=self.txtKontoVar, justify=RIGHT)
        txtKosten = ttk.Entry(
            content, textvariable=self.txtKostenVar, justify=RIGHT)
        txtWert = ttk.Entry(
            content, textvariable=self.txtWertVar, justify=RIGHT)
        txtInvest = ttk.Entry(
            content, textvariable=self.txtInvestVar, justify=RIGHT)
        txtG_V = ttk.Entry(content, textvariable=self.txtG_VVar, justify=RIGHT)

        cmdFirst = ttk.Button(content, text="|< First",
                              command=self.cmdFirst_Click)
        cmdPrev = ttk.Button(content, text="< Prev",
                             command=self.cmdPrev_Click)
        cmdNext = ttk.Button(content, text="Next >",
                             command=self.cmdNext_Click)
        cmdLast = ttk.Button(content, text="Last >|",
                             command=self.cmdLast_Click)
        cmdRefresh = ttk.Button(content, text="Refresh DB",
                                command=self.cmdRefresh_Click, default=NORMAL)
        cmdExit = ttk.Button(content, text="Exit")

        content.grid(column=0, row=0, sticky=(N, S, E, W))

        lblId.grid(row=0, column=0, sticky=(W))
        lblDatum.grid(row=1, column=0, sticky=(W))
        lblTimestamp.grid(row=2, column=0, sticky=(W))
        lblDatum_Zeit.grid(row=3, column=0, sticky=(W))
        lblKonto.grid(row=4, column=0, sticky=(W))
        lblKosten.grid(row=5, column=0, sticky=(W))
        lblWert.grid(row=6, column=0, sticky=(W))
        lblInvest.grid(row=7, column=0, sticky=(W))
        lblG_V.grid(row=8, column=0, sticky=(W))
        lblStatus.grid(row=9, column=1, sticky=(E))

        txtId.grid(row=0, column=1)
        txtDatum.grid(row=1, column=1)
        txtTimestamp.grid(row=2, column=1)
        txtDatum_Zeit.grid(row=3, column=1)
        txtKonto.grid(row=4, column=1)
        txtKosten.grid(row=5, column=1)
        txtWert.grid(row=6, column=1)
        txtInvest.grid(row=7, column=1)
        txtG_V.grid(row=8, column=1)

        cmdFirst.grid(row=0, column=2)
        cmdPrev.grid(row=1, column=2)
        cmdNext.grid(row=2, column=2)
        cmdLast.grid(row=3, column=2)
        cmdRefresh.grid(row=5, column=2)
        cmdExit.grid(row=8, column=2)

        content.rowconfigure(0, pad=5)
        content.rowconfigure(1, pad=5)
        content.rowconfigure(2, pad=5)
        content.rowconfigure(3, pad=5)
        content.rowconfigure(4, pad=5)
        content.rowconfigure(5, pad=5)
        content.rowconfigure(6, pad=5)
        content.rowconfigure(7, pad=5)
        content.rowconfigure(8, pad=5)
        content.rowconfigure(9, pad=15)
        content.columnconfigure(0, pad=10)
        content.columnconfigure(1, pad=0)
        content.columnconfigure(2, pad=40)

        cmdExit.bind(sequence='<ButtonPress-1>',
                     func=lambda e: root.destroy())
        root.bind(sequence='<Return>', func=lambda e: cmdRefresh.invoke())

        cmdRefresh.focus()

    def cmdFirst_Click(self, *args):
        self.pointer = 0
        self.RefreshFormData(self.pointer)

    def cmdPrev_Click(self, *args):
        if self.pointer > 0:
            self.pointer -= 1
        self.RefreshFormData(self.pointer)

    def cmdNext_Click(self, *args):
        if self.pointer < (len(datatable) - 1):
            self.pointer += 1
        self.RefreshFormData(self.pointer)

    def cmdLast_Click(self, *args):
        self.pointer = len(datatable) - 1
        self.RefreshFormData(self.pointer)

    def cmdRefresh_Click(self, *args):
        global datatable
        datatable = GetDataTable()
        if datatable:
            self.pointer = len(datatable) - 1
            self.RefreshFormData(self.pointer)

    def RefreshFormData(self, poin):
        row = list(datatable[poin])
        for i in range(0, 4):
            row[i] = str(row[i])
        for i in range(4, 9):
            row[i] = f"{row[i]:,}".replace('.', '#').replace(
                ',', '.').replace('#', ',') + ' €'
        self.txtIdVar.set(row[0])
        self.txtDatumVar.set(row[1])
        self.txtTimestampVar.set(row[2])
        self.txtDatum_ZeitVar.set(row[3])
        self.txtKontoVar.set(row[4])
        self.txtKostenVar.set(row[5])
        self.txtWertVar.set(row[6])
        self.txtInvestVar.set(row[7])
        self.txtG_VVar.set(row[8])


def GetDataTable():
    sql_select = f''' SELECT * FROM vermoegen ORDER BY ? ASC'''
    sql_param = ["Timestamp", ]
    datensaetze = db.dbReadAllRows(sql_select, sql_param)
    if datensaetze:
        return datensaetze
    else:
        return False


def _main():
    global datatable
    global db
    dbFullPath = dbPath + '\\' + dbFile
    if not os.path.isfile(dbFullPath):
        print(f'\nFehler : Datenbankdatei existiert nicht\nError  : '
              f'"{dbFullPath}"')
        print(f'Programm wurde abgebrochen')
        return False
    db = MyDB(dbFullPath)
    datatable = GetDataTable()
    if datatable:
        root = Tk()
        FrmMain(root)
        root.mainloop()


if __name__ == "__main__":
    _main()
