import smtplib
import urllib3
from datetime import datetime
import time
import os

def health_check():
    http = urllib3.PoolManager()

    health_check_passing = False
    attempts_remaining = 2
    first_attempt = True
    while (not health_check_passing and attempts_remaining > 0):
        if not first_attempt:
            time.sleep(2)
        resp = http.request(
            "GET", 
            os.getenv('HEALTH_CHECK_ADDRESS')
        )

        health_check_passing = resp.status == 200 and resp.data.decode('ascii') == "healthy"
        attempts_remaining = attempts_remaining - 1
        first_attempt = False
    
    return health_check_passing


def send_unhealthy_email():
    gmail_user = os.getenv('EMAIL_USER')
    gmail_app_password = os.getenv('EMAIL_PASSWORD')
    sent_from = gmail_user
    sent_to = [os.getenv('EMAIL_RECIPIENT')]
    subject = "🚨 GateKey is unhealthy! 🚨"

    now = datetime.now()

    current_time = now.strftime("%H:%M:%S")
    body = f"GateKey did not respond healthy to a ping at {current_time}"

    email_text = """\
From: %s
To: %s
Subject: %s

%s
""" % (sent_from, ", ".join(sent_to), subject, body)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_app_password)
        server.sendmail(sent_from, sent_to, email_text.encode("utf-8"))
        server.close()
    except Exception as exception:
        print("Error: %s!\n\n" % exception)

def lambda_handler(event, context):
    if not health_check():
        print("Failed to ping GateKey. Sending mail")
        send_unhealthy_email()
    else:
        print("GateKey is healthy")

if __name__ == "__main__":
    lambda_handler(None, None)
