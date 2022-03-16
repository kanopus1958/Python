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
from rwm_mod01 import show_header, aktuelles_datum, aktuelle_uhrzeit

G_OS = ('Windows')
G_HEADER_1 = '# Depot-Bestand ermitteln und '
G_HEADER_2 = 'per Mail versenden           #'


def _main():
    show_header(G_HEADER_1, G_HEADER_2, __file__, G_OS)

    bestand = {"MBG.DE": {"Bez": "Mercedes-Benz Group AG",
                          "Anz": 145, "Invest": 10_087.65},
               "H5AB.BE": {"Bez": "HAUSINVEST",
                           "Anz": 1175, "Invest": 50_010.23},
               "OG78.BE": {"Bez": "LBBW GLOBAL WARMING R",
                           "Anz": 250, "Invest": 20_072.50},
               "DKDF.BE": {"Bez": "DEKA-INDUSTRIE 4.0 CF",
                           "Anz": 140, "Invest": 29_721.99},
               #    "AMD.DE": {"Bez": "Advanced Micro Devices, Inc.",
               #               "Anz": 0, "Invest": 0},
               #    "SAP.DE": {"Bez": "SAP SE",
               #               "Anz": 0, "Invest": 0},
               #    "PAH3.DE": {"Bez": "Porsche Automobil Holding SE",
               #                "Anz": 0, "Invest": 0},
               "MBG.DE": {"Bez": "Mercedes-Benz Group AG",
                          "Anz": 145, "Invest": 10_087.65}}

    start_datum = arrow.now().shift(days=-4).date()
    end_datum = arrow.now().shift(days=-0).date()
    # end_datum = arrow.now().shift(days=-1).date()

    yahoo_ergebnis = web.DataReader(
        list(bestand.keys()), "yahoo",
        start_datum, end_datum)["Adj Close"].iloc[-1]

    nachricht = f'AKTUELLER DEPOTWERT ' \
                f'(Stand: {aktuelles_datum()} {aktuelle_uhrzeit()})\n\n'
    nachricht += f'Fond / Wertpapier                          Kurs     Anz' \
                 f'           Wert       Invest           G/V\n'
    nachricht += f'{97*"-"}\n'
    gesamt_invest = 0
    gesamt_summe = 0
    gesamt_resultat = 0
    for symbol, details in bestand.items():
        anz = details["Anz"]
        gesamt_invest += (invest := details["Invest"])
        gesamt_summe += (summe := yahoo_ergebnis[symbol] * anz)
        gesamt_resultat += (resultat := summe - details["Invest"])
        nachricht += f'{details["Bez"] + " ("+symbol+")":<40}' \
                     f'{yahoo_ergebnis[symbol]:>6.2f}€ x {anz:>5,d} =  ' \
                     f'{summe:>10,.2f}€  {invest:>10,.2f}€   ' \
                     f'{resultat:>10,.2f}€\n'
    nachricht += f'{gesamt_summe:>69,.2f}€  {gesamt_invest:10,.2f}€   ' \
                 f'{gesamt_resultat:10,.2f}€\n'

    msg = MIMEMultipart()
    msg["From"] = cred.FROM
    msg["To"] = cred.TO
    msg["Subject"] = f"Depot-Wert " \
                     f"(Stand: {aktuelles_datum()} {aktuelle_uhrzeit()} )"
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
