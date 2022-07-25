import json
import smtplib
from flask import request
import urllib.parse
from uploads.config import SMTP
from flask_jwt_extended import create_access_token


def send_verification_email(email, username):
    """
        Sends verification email to the given user.

    :param email:
    :param username: User to send the email.
    """
    token = create_access_token(identity=email, additional_claims={"is_admin": True})

    params = {'token': token, 'email': email}
    verification_URL = f"{request.url_root}email-verification?" + urllib.parse.urlencode(params)

    message_body = f"""Please verify account for {username} by clicking on the following link:
           {verification_URL}
           """

    send_email(email, "Please verify account", message_body)


def send_email(receiver_email, subject, message_body):
    """
        Sends a plain-text email to receiver_email address with
        subject and message body

    :param receiver_email Email address of the receiver (To)
    :param subject Subject field of the email
    :param message_body Body of the email.
    """
    message = f"""\
    Subject: {subject}

    {message_body}."""

    with smtplib.SMTP(SMTP['host'], SMTP['port']) as server:
        server.ehlo()
        server.starttls()
        server.login(SMTP['sender_email'], SMTP['sender_password'])
        server.sendmail(SMTP['sender_email'], receiver_email, message)
        server.quit()


telemetry=[{'id': 2, 'GPS': 4, 'Battery': 'none', 'Altitude': 5, 'System-status': 'standby',
              'Vehicle-mode': 'stabilized', 'EKF ok?': 'false'},
             {'id': 4, 'GPS': 6, 'Battery': 'none', 'Altitude': 150, 'System-status': 'standby',
              'Vehicle-mode': 'stabilized', 'EKF ok?': 'false'},
             {'id': 3, 'GPS': 10, 'Battery': 'none', 'Altitude': 10, 'System-status': 'standby',
              'Vehicle-mode': 'stabilized', 'EKF ok?': 'false'}]
