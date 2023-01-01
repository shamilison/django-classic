__author__ = 'shamilsakib'

from django.contrib.auth import authenticate
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.exceptions import APIException

from django_classic.models import ClassicModel


class ClassicTokenSerializer(AuthTokenSerializer):

    def __init__(self, model=None, **kwargs):
        super(ClassicTokenSerializer, self).__init__(self, **kwargs)
        self.model = model

    def update(self, instance, validated_data):
        super(ClassicTokenSerializer, self).update(instance, validated_data)

    def create(self, validated_data):
        super(ClassicTokenSerializer, self).create(validated_data)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if not (username and password):
            message = _('Must include "username" and "password".')
            raise serializers.ValidationError(message, code='authorization')

        _user = authenticate(username=username, password=password)
        if not _user:
            raise APIException(_("User for provided username/password does not exist in the system."))
        elif _user.is_deleted:
            raise APIException(_("User has been deleted from the system."))
        elif not _user.is_active:
            raise APIException(_("User has been deactivated."))
        elif not _user.is_active:
            raise APIException(_('User account is disabled.'))

        attrs['user'] = _user
        return attrs


class ClassicModelSerializer(serializers.ModelSerializer):

    def __init__(self, *args, fields=None, context=None, **kwargs):
        super(ClassicModelSerializer, self).__init__(*args, context=context, **kwargs)

    def to_representation(self, instance):
        return super(ClassicModelSerializer, self).to_representation(instance)

    def update(self, instance, validated_data):
        with transaction.atomic():
            return super(ClassicModelSerializer, self).update(instance, validated_data)

    def save(self, **kwargs):
        return super(ClassicModelSerializer, self).save(**kwargs)

    def create(self, validated_data):
        with transaction.atomic():
            return super(ClassicModelSerializer, self).create(validated_data)

    def mutate(self, **kwargs):
        return self.instance.mutate_to()

    class Meta:
        model = ClassicModel
        read_only_fields = ['uuid', 'identifier', 'is_active', 'is_locked', 'update_time', 'create_time']
