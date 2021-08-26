__author__ = 'shamil_sakib'

from django_classic.enums.classic_enum import ClassicEnum


class InsertType(ClassicEnum):
    Created = 0
    Imported = 1
    Generated = 2
    Version = 3
