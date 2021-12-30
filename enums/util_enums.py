__author__ = 'shamil_sakib'

from django_classic.enums.classic_enum import ClassicEnum


class ResponseStatus(ClassicEnum):
    Fail = 0
    Success = 1


class ProcessingStatus(ClassicEnum):
    IGNORED = -2
    ERROR = -1
    CORRUPTED = 0
    INSERTED = 1
    UPDATED = 2


class ModelRuntimeCacheType(ClassicEnum):
    SINGLE = 'single'
    MANY = 'many'
