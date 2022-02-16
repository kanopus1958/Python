import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import EMail_credentials as cred

username = cred.FROM
password = cred.PASSWORD
mail_from = cred.FROM
mail_to = cred.TO
mail_subject = "Test Subject"
mail_body = "This is a test message"

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
