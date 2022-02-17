#!/usr/bin/env python3

# Programm     : test_mail.py
# Version      : 1.00
# SW-Stand     : 17.02.2022
# Autor        : Kanopus1958
# Beschreibung : Ermittlung Depotbestand und Versand per Mail

G_OS = ('Windows') 
G_HEADER_1 = '# Versand von eMail per gmail'
G_HEADER_2 = '.com                        #'

from rwm_mod01 import show_header
from socket import gethostname
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import rwm__credentials01 as cred

def _main():
    show_header(G_HEADER_1, G_HEADER_2, __file__, G_OS)

    username = cred.FROM
    password = cred.PASSWORD
    mail_from = cred.FROM
    mail_to = cred.TO
    mail_subject = "Test Mail von Rechner "+gethostname()
    mail_body = f'Hallo Empfänger,\n'
    mail_body += f'dies ist eine Testmail generiert unter Python.2*\n'
    mail_body += f'Mit freundlichen Grüßen\n'
    mail_body += gethostename()

    mimemsg = MIMEMultipart()
    mimemsg['From']=mail_from
    mimemsg['To']=mail_to
    mimemsg['Subject']=mail_subject
    mimemsg.attach(MIMEText(mail_body, 'plain'))
    connection = smtplib.SMTP(host='smtp.gmail.com', port=587)
    connection.starttls()
    connection.login(username,password)
    error_text = connection.send_message(mimemsg)
    connection.quit()

    if not error_text:
        print(mail_body)
    else:
        print(f'Probleme beim Versand ({error_text})')

if __name__ == "__main__":
    _main()
