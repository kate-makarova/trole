import requests
from django.conf import settings


class MailClient:
    def __init__(self):
        self.sender = "Trole Online <system@mail.trole.online>"
        self.url = "https://api.mailgun.net/v3/mail.trole.online/messages"
        self.key = "UTF-8"
    
    def send(self, subject, body_text, body_html, recipient):
        requests.post(
            self.url,
            auth=("api", settings.MAILGUN_API_KEY),
            data={"from": self.sender,
                  "to": ""+recipient+">",
                  "subject": subject,
                  "text": body_text,
                  "html": body_html
                  })
