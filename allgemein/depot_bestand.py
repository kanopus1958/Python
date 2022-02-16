#!/usr/bin/env python3

# Programm     : depot_bestand.py
# Version      : 1.00
# SW-Stand     : 16.02.2022
# Autor        : Rolf Weiss
# Beschreibung : Ermittlung Depotbestand und Versand per Mail

G_OS = ('Windows') 
G_HEADER_1 = '# Depot-Bestand ermitteln und '
G_HEADER_2 = 'per Mail versenden           #'

from rwm_mod01 import show_header
import pandas_datareader.data as web
import arrow
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import EMail_credentials as cred

def _main():
    show_header(G_HEADER_1, G_HEADER_2, __file__, G_OS)

    bestand = {"AMD.DE": {"Bez": "Advanced Micro Devices, Inc.", "Anz": 3},
            "MBG.DE": {"Bez": "Mercedes-Benz Group AG", "Anz": 1},
            "OG78.BE": {"Bez": "LBBW GLOBAL WARMING R", "Anz": 5},
            "DKDF.F": {"Bez": "Deka-Industrie 4.0", "Anz": 3},
            "H5AB.MU": {"Bez": "HAUSINVEST", "Anz": 10}}

    start_datum = arrow.now().shift(days=-4).date()
    end_datum = arrow.now().shift(days=-1).date()

    yahoo_ergebnis = web.DataReader(
        list(bestand.keys()), "yahoo", start_datum, end_datum)["Adj Close"].iloc[-1]
    print(yahoo_ergebnis)
    print(cred.FROM, cred.TO, cred.PASSWORD)

    nachricht = "AKTUELLER DEPOTWERT\n\n"
    gesamt_summe = 0
    for symbol, details in bestand.items():
        anz = details["Anz"]
        gesamt_summe += (summe:= yahoo_ergebnis[symbol] * anz)
        nachricht += f'{details["Bez"] + " ("+symbol+") ":<40} {yahoo_ergebnis[symbol]:>8.2f} x {anz:>5} = Summe {summe:>10,.2f}\n'
        nachricht += f'{gesamt_summe:>76,.2f}\n'

    msg = MIMEMultipart()
    msg["From"] = cred.FROM
    msg["To"] = cred.TO
    msg["Subject"] = "Aktueller Depot-Wert"
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
