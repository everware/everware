import smtplib

class EmailNotificator:
    def __init__(self):
        self._smtp = None

    def send_email(self, from_, to, subject, message):
        if self._smtp is None:
            self._smtp = smtplib.SMTP('localhost')
        mail = """From: From Person <{from_}>
To: To Person <{to}>
Subject: {subject}

{message}
""".format(from_=from_, to=to, message=message, subject=subject)
        self._smtp.sendmail(from_, to, mail)
