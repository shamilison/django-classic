from django.conf import settings
from django.core.management.base import BaseCommand

from django_classic.models import ClassicSystemUser


class Command(BaseCommand):
    help = 'Create a market account'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        ClassicSystemUser.objects.create_superuser(
            username=settings.ADMIN_EMAIL, email=settings.ADMIN_EMAIL, password=settings.ADMIN_PASSWORD,
            first_name="Super", last_name="Admin",
        )
