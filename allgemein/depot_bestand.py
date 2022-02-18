#!/usr/bin/env python3

# Programm     : depot_bestand.py
# Version      : 1.00
# SW-Stand     : 17.02.2022
# Autor        : Kanopus1958
# Beschreibung : Ermittlung Depotbestand und Versand per Mail

import rwm_credentials01 as cred
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import arrow
import pandas_datareader.data as web
from rwm_mod01 import show_header

G_OS = ('Windows')
G_HEADER_1 = '# Depot-Bestand ermitteln und '
G_HEADER_2 = 'per Mail versenden           #'


def _main():
    show_header(G_HEADER_1, G_HEADER_2, __file__, G_OS)

    bestand = {"MBG.DE": {"Bez": "Mercedes-Benz Group AG", "Anz": 145},
               "AMD.DE": {"Bez": "Advanced Micro Devices, Inc.", "Anz": 1},
               "SAP.DE": {"Bez": "SAP SE", "Anz": 1},
               "PAH3.DE": {"Bez": "Porsche Automobil Holding SE", "Anz": 1}}

    start_datum = arrow.now().shift(days=-4).date()
    end_datum = arrow.now().shift(days=-1).date()

    yahoo_ergebnis = web.DataReader(
        list(bestand.keys()), "yahoo",
        start_datum, end_datum)["Adj Close"].iloc[-1]
    # print (yahoo_ergebnis)
    # exit(0)

    nachricht = "AKTUELLER DEPOTWERT\n\n"
    gesamt_summe = 0
    for symbol, details in bestand.items():
        anz = details["Anz"]
        gesamt_summe += (summe := yahoo_ergebnis[symbol] * anz)
        nachricht += f'{details["Bez"] + " ("+symbol+") ":<40} \
            {yahoo_ergebnis[symbol]:>8.2f} x {anz:>5} = Summe \
            {summe:>10,.2f}\n'
    nachricht += f'{gesamt_summe:>76,.2f}\n'

    msg = MIMEMultipart()
    msg["From"] = cred.FROM
    msg["To"] = cred.TO
    msg["Subject"] = "Test Aktueller Depot-Wert"
    msg.attach(MIMEText(nachricht, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(cred.FROM, cred.PASSWORD)
    error_text = server.sendmail(cred.FROM, cred.TO, msg.as_string())
    server.quit()
    if not error_text:
        print(nachricht)
    else:
        print(f'Probleme beim Versand ({error_text})')


if __name__ == "__main__":
    _main()
