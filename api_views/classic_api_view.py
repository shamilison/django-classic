__author__ = 'shamilsakib'

import importlib.util
import logging
import os
import re
import sys

from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, viewsets, mixins
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.exceptions import APIException
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.response import Response

from django_classic.extras.classic_authentication import ClassicTokenAuthentication, ClassicSessionAuthentication
from django_classic.extras.classic_renderers import ClassicJSONRenderer
from django_classic.logging.classic_logger import ClassicLogger
from django_classic.mixins.classic_view_mixin import ClassicGetViewMixin
from django_classic.serializers.classic_serializers import ClassicTokenSerializer

logging.setLoggerClass(ClassicLogger)
logger = logging.getLogger(__name__)


class ClassicVersionAPIViewSet(viewsets.GenericViewSet):
    authentication_classes = (ClassicTokenAuthentication, ClassicSessionAuthentication,)
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)
    # authentication_classes = ()
    # permission_classes = ()
    renderer_classes = (ClassicJSONRenderer, BrowsableAPIRenderer)
    parser_classes = (MultiPartParser, FormParser, JSONParser,)

    model = None
    version_pattern = re.compile("^\d+$")

    def model_serializer_finder(self, model_class, version, *args, **kwargs):
        version_path = "v{}".format(version)
        app_path = None
        try:
            # getting the app name
            app_name = model_class._meta.app_label
            # getting the app module
            app_module = apps.get_app_config(app_name).module
            # getting the app path
            app_path = os.path.dirname(app_module.__file__)
        except Exception as error:
            logger.exception(error)
        # model related data
        model_name = model_path = model_file_name = None
        try:
            # getting the model name
            model_name = model_class.__name__
            # getting the model object from model name
            model_object = apps.get_model(app_label=app_name, model_name=model_name)
            # from model object getting the path og the model file
            model_path = os.path.abspath(sys.modules[model_object.__module__].__file__)
            # extracting the model file name from the path
            model_file_name = model_path[model_path.rfind(os.sep) + 1:model_path.rfind(".")]
        except Exception as error:
            logger.exception(error)
        # difference in path - the models' directory inside the app
        app_model_path = os.path.join(app_path, "models")
        # difference between the app_model_path and model_path
        difference = os.path.relpath(model_path, app_model_path)
        # finding the last slash index
        last_slash_index = difference.rfind(os.sep)
        # if there is a slash this means the model_file is deep inside the models directory
        if last_slash_index != -1:
            # excluding file name, getting the different path only
            difference = difference[:last_slash_index]
            # if the path is too deep we need to replace `os.sep` with ``.``
            # difference = difference.replace(os.sep, ".")
            # adding a trailing ``dot``
            difference += os.sep
        # There is no slash so the model file is just inside the app_model_path directory
        else:
            difference = ""
        # Creating the exact file path
        file_path = os.path.join(app_path, 'serializers', version_path, difference)
        file_name = '{}_serializer'.format(model_file_name)
        # getting the exact serializer module
        module_spec = importlib.util.spec_from_file_location(
            file_name, os.path.join(file_path, '{}.py'.format(file_name)))
        serializer_module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(serializer_module)
        serializer_class = getattr(serializer_module, model_name + "Serializer")
        setattr(serializer_class.Meta, 'ref_name', '{}_{}'.format(file_name, self.action))
        return serializer_class

    def get_serializer_class(self):
        # getting the api version name
        model_class = self.model
        if self.request.version and self.version_pattern.match(self.request.version):
            version = int(self.request.version)
        else:
            version = 1
        model_serializer = self.model_serializer_finder(model_class=model_class, version=version)
        if model_serializer:
            return model_serializer
        return super(ClassicVersionAPIViewSet, self).get_serializer_class()


class ClassicVersionAPIGetViewSet(ClassicVersionAPIViewSet, ClassicGetViewMixin):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(ClassicVersionAPIGetViewSet, self).dispatch(request, *args, **kwargs)

    def finalize_response(self, request, response, *args, **kwargs):
        return super(ClassicVersionAPIGetViewSet, self).finalize_response(request, response, *args, **kwargs)

    def options(self, request, *args, **kwargs):
        return super(ClassicVersionAPIGetViewSet, self).options(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        response = super(ClassicVersionAPIGetViewSet, self).list(request, *args, **kwargs)
        return response

    def get_queryset(self, **kwargs):
        queryset = super(ClassicVersionAPIGetViewSet, self).get_queryset(**kwargs)
        if self.model.select_fields():
            queryset = queryset.select_related(self.model.select_fields())
        if self.model.prefetch_fields():
            queryset = queryset.prefetch_related(self.model.prefetch_fields())
        return queryset


class ClassicVersionAPICreateViewSet(ClassicVersionAPIViewSet, mixins.CreateModelMixin):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(ClassicVersionAPICreateViewSet, self).dispatch(request, *args, **kwargs)

    def finalize_response(self, request, response, *args, **kwargs):
        return super(ClassicVersionAPICreateViewSet, self).finalize_response(request, response, *args, **kwargs)

    def options(self, request, *args, **kwargs):
        return super(ClassicVersionAPICreateViewSet, self).options(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(
                data=request.data, many=isinstance(request.data, list),
                extras=self.model.get_api_extras(request=request, category="create"))
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as error:
            raise APIException(error)

    def get_queryset(self, **kwargs):
        queryset = self.model.objects
        if self.model.select_fields():
            queryset = queryset.select_related(self.model.select_fields())
        if self.model.prefetch_fields():
            queryset = queryset.prefetch_related(self.model.prefetch_fields())
        return queryset.all()


class ClassicVersionAPIUpdateViewSet(ClassicVersionAPIViewSet, mixins.UpdateModelMixin):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(ClassicVersionAPIUpdateViewSet, self).dispatch(request, *args, **kwargs)

    def finalize_response(self, request, response, *args, **kwargs):
        return super(ClassicVersionAPIUpdateViewSet, self).finalize_response(request, response, *args, **kwargs)

    def options(self, request, *args, **kwargs):
        return super(ClassicVersionAPIUpdateViewSet, self).options(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        try:
            return super(ClassicVersionAPIUpdateViewSet, self).update(request, *args, **kwargs)
        except Exception as error:
            raise APIException(error)

    def get_queryset(self, **kwargs):
        queryset = self.model.objects
        if self.model.select_fields():
            queryset = queryset.select_related(self.model.select_fields())
        if self.model.prefetch_fields():
            queryset = queryset.prefetch_related(self.model.prefetch_fields())
        return queryset.all()


class ClassicVersionAPIDestroyViewSet(ClassicVersionAPIViewSet, mixins.DestroyModelMixin):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(ClassicVersionAPIDestroyViewSet, self).dispatch(request, *args, **kwargs)

    def finalize_response(self, request, response, *args, **kwargs):
        return super(ClassicVersionAPIDestroyViewSet, self).finalize_response(request, response, *args, **kwargs)

    def options(self, request, *args, **kwargs):
        return super(ClassicVersionAPIDestroyViewSet, self).options(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        try:
            return super(ClassicVersionAPIDestroyViewSet, self).destroy(request, *args, **kwargs)
        except Exception as error:
            raise APIException(error)

    def get_queryset(self, **kwargs):
        return self.model.objects.all()


class ClassicAPITokenView(ObtainAuthToken):
    serializer_class = ClassicTokenSerializer
    model = get_user_model()

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(ClassicAPITokenView, self).dispatch(request, *args, **kwargs)

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, model=self.model)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            with transaction.atomic():
                token, created = Token.objects.get_or_create(user=user)
                response = {
                    'token': token.key,
                    'success': True,
                    "user_id": user.pk,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "username": user.username,
                }
                return Response(response)
        return Response(
            {'message': 'Cannot login with provided credentials.', 'success': False},
            status=status.HTTP_400_BAD_REQUEST
        )
