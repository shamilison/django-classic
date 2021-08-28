import subprocess

from django.core.management.base import BaseCommand
from django.db.migrations.recorder import MigrationRecorder
from django.core.management.commands.migrate import Command as MigrateCommand


class Command(BaseCommand):
    help = 'Fix migration issues.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        # Clean migration in database
        MigrationRecorder.Migration.objects.all().delete()
        print('Now, run the `python manage.py migrate --fake` to stabilize your migrations with database.')
