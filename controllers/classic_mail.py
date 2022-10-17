__author__ = 'shamilsakib'

import logging

from django.conf import settings
from mailersend.emails import NewEmail

from django_classic.logging.classic_logger import ClassicLogger

logging.setLoggerClass(ClassicLogger)
logger = logging.getLogger(__name__)


def send_classic_email(subject, html_content, from_email, to_email, **kwargs):
    try:
        if subject and html_content and from_email and to_email:
            # if isinstance(to_email, str):
            #     to_email = [to_email]
            # msg = EmailMultiAlternatives(subject, html_content, from_email, to_email)
            # msg.content_subtype = "html"
            # msg.send()

            # assigning NewEmail() without params defaults to MAILERSEND_API_KEY env var
            mailer = NewEmail(settings.MAILERSEND_API_KEY)

            if isinstance(to_email, list):
                recipients = []
                for _email in to_email:
                    recipients.append({
                        "name": _email,
                        "email": _email,
                    })
            else:
                recipients = [{
                    "name": to_email,
                    "email": to_email,
                }]
            # define an empty dict to populate with mail values
            mail_body = {}
            mail_from = {
                "name": "No Reply",
                "email": from_email,
            }
            reply_to = [
                {
                    "name": from_email,
                    "email": from_email,
                }
            ]
            mailer.set_mail_from(mail_from, mail_body)
            mailer.set_mail_to(recipients, mail_body)
            mailer.set_subject(subject, mail_body)
            mailer.set_html_content(html_content, mail_body)
            mailer.set_reply_to(reply_to, mail_body)
            # using print() will also return status code and data
            _result = mailer.send(mail_body)
            logger.info(_result)
    except Exception as error:
        logger.exception(error)
