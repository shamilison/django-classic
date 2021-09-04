__author__ = 'shamilsakib'

from django.contrib.auth.models import AbstractUser
from django.db import models

from django_classic.models import ClassicModel


class ClassicSystemUser(AbstractUser, ClassicModel):
    # Phone number
    phone = models.CharField(max_length=64, blank=True)

    class Meta:
        app_label = 'django_classic'
