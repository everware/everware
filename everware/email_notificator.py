import smtplib

class EmailNotificator:
    def __init__(self):
        self._smtp = smtplib.SMTP('localhost')

    def send_email(self, from_, to, subject, message):
        mail = """From: From Person <{from_}>
To: To Person <{to}>
Subject: {subject}

{message}
""".format(from_=from_, to=to, message=message, subject=subject)
        self._smtp.sendmail(from_, to, mail)
