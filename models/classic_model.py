__author__ = 'shamil_sakib'

import logging
import uuid

from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import timezone

from django_classic.enums.model_enums import InsertType
from django_classic.enums.util_enums import ProcessingStatus
from django_classic.logging.classic_logger import ClassicLogger

logging.setLoggerClass(ClassicLogger)
logger = logging.getLogger(__name__)

get_model = apps.get_model


class ClassicModel(models.Model):
    # Scalable unique value and primary key
    uuid = models.CharField(max_length=64, default=uuid.uuid4, primary_key=True)

    # Manual identifier
    identifier = models.CharField(max_length=64, default=None, null=True)

    # Object state controller
    is_active = models.BooleanField(default=True)
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

    @classmethod
    def prefetch_fields(cls):
        return None

    @classmethod
    def select_fields(cls):
        return None

    @classmethod
    def get_unique_field_maps(cls, json_ob):
        return {}

    @classmethod
    def insert_or_update_from_json(cls, json_ob, return_instance=False, **kwargs):
        if not json_ob:
            if return_instance:
                return ProcessingStatus.CORRUPTED, None
            return ProcessingStatus.CORRUPTED
        try:
            _unique_keys = cls.get_unique_field_maps(json_ob=json_ob)
            if _unique_keys:
                _instance, _is_created = cls.objects.get_or_create(**_unique_keys)
            else:
                _instance, _is_created = cls(), True
            for _key in json_ob.keys():
                setattr(_instance, _key, json_ob.get(_key))
            _instance.save()
            if return_instance:
                return ProcessingStatus.INSERTED if _is_created else ProcessingStatus.UPDATED, _instance
            return ProcessingStatus.INSERTED if _is_created else ProcessingStatus.UPDATED
        except Exception as error:
            logger.exception(error)
            if return_instance:
                return ProcessingStatus.ERROR, None
            return ProcessingStatus.ERROR

    @classmethod
    def remove_using_json(cls, json_ob, using='pk'):
        try:
            if using == 'country':
                _instance = cls.objects.get(root_id=json_ob.get('root_id'), country=json_ob.get('country'))
            else:
                _instance = cls.objects.get(uuid=json_ob.get('uuid'))
            _instance.delete()
        except ObjectDoesNotExist:
            pass
        except Exception as error:
            logger.exception(error)

    @classmethod
    def build_key(cls, pk):
        return '{}_{}'.format(cls.__name__, pk)

    def clean_fields(self, exclude=None):
        return super(ClassicModel, self).clean_fields(exclude)

    @classmethod
    def order_by(cls, **kwargs):
        return ['update_time', ]

    @classmethod
    def datetime_fields(cls, **kwargs):
        return ['update_time', 'create_time', ]

    def save(self, update_time=True, **kwargs):
        if update_time:
            self.update_time = timezone.localtime()
        super(ClassicModel, self).save()

    def delete(self, **kwargs):
        if kwargs.get('hard'):
            # Delete from the universe
            return super(ClassicModel, self).delete()
        else:
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

    @classmethod
    def get_api_extras(cls, **kwargs):
        return None
