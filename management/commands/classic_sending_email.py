__author__ = 'shamilsakib'

import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from django_classic.logging.classic_logger import ClassicLogger

logging.setLoggerClass(ClassicLogger)
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Fix migration issues.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        from django_classic.controllers.classic_mail import send_classic_email
        send_classic_email(
            f'{settings.ERROR_EMAIL_PREFIX}: Test',
            f'<b>Test Alert.</b>',
            settings.EMAIL_DEFAULT_FROM, settings.EMAIL_ERROR_SEND_TO.split(','))
