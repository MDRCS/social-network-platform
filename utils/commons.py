import time
from flask import current_app
import boto3


def utc_now_timestamp():
    return int(time.time())


def utc_now_ts_ms():
    return lambda: int(round(time.time() * 1000))


def email(to_email, subject, body_html, body_text):
    # don't run this if we're running a test or setting is False
    if current_app.config.get('TESTING') or not current_app.config.get('AWS_SEND_MAIL'):
        return False

    client = boto3.client('ses')
    return client.send_email(
        Source='elrahali.md@gmail.com',
        Destination={
            'ToAddresses': [
                to_email,
            ]
        },
        Message={
            'Subject': {
                'Data': subject,
                'Charset': 'UTF-8'
            },
            'Body': {
                'Text': {
                    'Data': body_text,
                    'Charset': 'UTF-8'
                },
                'Html': {
                    'Data': body_html,
                    'Charset': 'UTF-8'
                },
            }
        }
    )
