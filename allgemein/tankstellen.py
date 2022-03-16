#!/usr/bin/env python3

# Programm     : tankstellen.py
# Version      : 1.00
# SW-Stand     : 13.03.2022
# Autor        : Kanopus1958
# Beschreibung : Ermittlung aktueller Treibstoffpreise

import requests
from bs4 import BeautifulSoup
import time
from rwm_mod01 import show_header

G_OS = ('Raspbian', 'Debian', 'Windows')
G_HEADER_1 = '# Aktuelle Treibstoffpreise au'
G_HEADER_2 = 'sgewaehlter Tankstellen      #'

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
        # print(self.daten)
        print(f'\n{self.daten["Name"]} ( {self.daten["Plz"]} '
              f'{self.daten["Stadt"]} , {self.daten["Strasse"]} )')
        print(f'{self.daten["Aktualisierung"]}')
        for k in self.daten['Treibstoffe'].keys():
            print(f'   {k:<20s} : {self.daten["Treibstoffe"][k]:>8.3f} €')


def _main():
    show_header(G_HEADER_1, G_HEADER_2, __file__, G_OS)
    for id in station_ids:
        tankstellen.append(tankstelle(id))
    for tanke in tankstellen:
        tanke.preise_ermitteln()
        tanke.drucken()


if __name__ == "__main__":
    t0 = time.perf_counter()
    _main()
    print(f'\nLaufzeit : {time.perf_counter() - t0:8,.4f} Sekunden\n')
