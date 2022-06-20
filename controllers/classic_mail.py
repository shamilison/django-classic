__author__ = 'shamilsakib'

import logging

from django.core.mail import EmailMultiAlternatives

from django_classic.logging.classic_logger import ClassicLogger

logging.setLoggerClass(ClassicLogger)
logger = logging.getLogger(__name__)


def send_classic_email(subject, html_content, from_email, to_email, **kwargs):
    try:
        if subject and html_content and from_email and to_email:
            msg = EmailMultiAlternatives(subject, html_content, from_email, to_email)
            msg.content_subtype = "html"
            msg.send()
    except Exception as error:
        logger.exception(error)
