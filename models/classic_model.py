import uuid

from django.apps import apps
from django.db import models
from django.utils import timezone

from django_classic.enums.model_enums import InsertType

get_model = apps.get_model


class ClassicModel(models.Model):
    # Scalable unique value and primary key
    uuid = models.CharField(max_length=64, default=uuid.uuid4, primary_key=True)

    # Manual identifier
    identifier = models.CharField(max_length=64, default=None, null=True)

    # Object state controller
    is_active = models.BooleanField(default=True, editable=False)
    is_locked = models.BooleanField(default=False, editable=False)

    # Deletion controller
    deleted_level = models.SmallIntegerField(default=0)
    is_deleted = models.BooleanField(default=False, editable=False)

    # Insert information
    insert_type = models.SmallIntegerField(default=InsertType.Created.value)

    # Auditable timestamp
    update_time = models.DateTimeField(default=timezone.localtime)
    create_time = models.DateTimeField(editable=False, default=timezone.localtime)

    class Meta:
        abstract = True

    def clean_fields(self, exclude=None):
        return super(ClassicModel, self).clean_fields(exclude)

    def save(self, update_time=True, **kwargs):
        if update_time:
            self.update_time = timezone.localtime()
        super(ClassicModel, self).save()

    def delete(self, **kwargs):
        self.deleted_level += 1
        self.is_deleted = True
        self.save(**kwargs)

    def restore(self, **kwargs):
        if self.deleted_level > 0:
            self.deleted_level -= 1
        else:
            self.is_active = True
            self.is_deleted = False
        self.save(**kwargs)
