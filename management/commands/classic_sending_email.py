__author__ = 'shamilsakib'

import logging

from django.core.management.base import BaseCommand

from django_classic.logging.classic_logger import ClassicLogger

logging.setLoggerClass(ClassicLogger)
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Fix migration issues.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        try:
            raise Exception('Test sending alert email!')
        except Exception as error:
            logger.exception(error, send_email=True)
