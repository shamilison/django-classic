__author__ = 'shamilsakib'

import logging
from datetime import datetime

from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.db.models import Q
from django.utils import timezone
from pytz import timezone
from rest_framework import viewsets, mixins

from django_classic.logging.classic_logger import ClassicLogger

logging.setLoggerClass(ClassicLogger)
logger = logging.getLogger(__name__)


class ClassicGetViewMixin(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    model = None

    def _prepare_search_fields(self, query_params):
        """
        Get list of search parameters
        :param query_params: a dictionary, generally request.GET
        :return: list of search fields
        """
        search_fields = list()
        if query_params.get('s', '0') == '1':
            ignore = ['s', 'sort', 'offset', 'limit', 'downloaded', 'page', 'page-size', 'depth', 'expand', 'format',
                      'disable-limit', 'disable_pagination', 'csrfmiddlewaretoken']
            for key in [key for key in query_params if key not in ignore]:
                _value = list()
                _values = list(filter(lambda x: x.strip() != '', query_params.get(key).split(',')))
                if key in self.model.datetime_fields():
                    for _val in _values:
                        _value.append(datetime.strptime(_val, '%Y-%m-%dT%H:%M:%S.%fZ%z').strftime('%Y-%m-%dT%H:%M:%S.%fZ%z'))
                    if len(_value) == 1:
                        _value.append(timezone.localtime().strftime('%Y-%m-%dT%H:%M:%S.%fZ%z'))
                else:
                    _value = _values
                search_fields.append((key, _value))
        return search_fields

    def _build_orm_query(self, query_string, search_fields, _in=False, _range=False, _bool=False, **kwargs):
        query = None  # Query to search for every search term
        # terms = normalize_query(query_string)
        if _in:
            or_query = None  # Query to search for a given term in each field
            for field_name in search_fields:
                q = Q(**{"%s__in" % field_name: tuple(query_string)})
                if or_query is None:
                    or_query = q
                else:
                    or_query |= q
            query = or_query
        elif _range:
            or_query = None  # Query to search for a given term in each field
            for field_name in search_fields:
                q = Q(**{"%s__range" % field_name: tuple(query_string)})
                if or_query is None:
                    or_query = q
                else:
                    or_query |= q
            query = or_query
        elif _bool:
            or_query = None  # Query to search for a given term in each field
            for field_name in search_fields:
                q = Q(**{"%s" % field_name: query_string[0]})
                if or_query is None:
                    or_query = q
                else:
                    or_query |= q
            query = or_query
        else:
            or_query = None  # Query to search for a given term in each field
            for term in query_string:
                for field_name in search_fields:
                    q = Q(**{"%s__icontains" % field_name: term})
                    if or_query is None:
                        or_query = q
                    else:
                        or_query |= q
            if query is None:
                query = or_query
            else:
                query &= or_query
        return query

    def _build_single_query(self, model, prop, query_strings, prefix='', **kwargs):
        entry_query = None
        if prop.find('.') == -1:
            try:
                field = model._meta.get_field(prop)
                # Though this is a direct model field but we implemented custom search method we want to handle this
                # field manually. So returning None here so that we can take care of the search field in apply_search_filter method
                # Here `not prefix` means we are in the parent model. Sometimes we might come to this method
                # by traversing through foreign key models
                if isinstance(field, models.AutoField):
                    entry_query = self._build_orm_query([int(q) for q in query_strings], [prefix + prop], _in=True)
                elif isinstance(field, models.ForeignKey):
                    entry_query = self._build_search_query(field.remote_field.model, 'name', query_strings,
                                                           prefix=prefix + field.name + '__')
                elif isinstance(field, models.ManyToManyField):
                    pass
                elif isinstance(field, models.DecimalField):
                    entry_query = self._build_orm_query([float(q) for q in query_strings], [prefix + prop],
                                                        range=len(query_strings) > 1)
                elif isinstance(field, (models.BigIntegerField, models.IntegerField)):
                    entry_query = self._build_orm_query([int(float(q)) for q in query_strings], [prefix + prop],
                                                        range=len(query_strings) > 1)
                elif isinstance(field, (models.DateField, models.DateTimeField)):
                    entry_query = self._build_orm_query([datetime.strptime(str(q), '%Y-%m-%dT%H:%M:%S.%fZ%z') for q in query_strings],
                                                        [prefix + prop],
                                                        range=len(query_strings) > 1)
                elif isinstance(field, models.BooleanField):
                    entry_query = self._build_orm_query([bool(q) for q in query_strings], [prefix + prop], _bool=True)
                else:
                    entry_query = self._build_orm_query(query_strings, [prefix + prop])
            except FieldDoesNotExist:
                pass
        else:
            property_list = prop.split('.')
            field = model._meta.get_field(property_list[0])
            entry_query = self._build_single_query(
                field.remote_field.model, ".".join(property_list[1:]), query_strings,
                prefix=prefix + property_list[0] + '__')
        return entry_query

    def _build_search_query(self, model, prop, query_strings, prefix='', **kwargs):
        return self._build_single_query(model, prop, query_strings, prefix=prefix)

    def _apply_search_filter(self, query_params=None, queryset=None, **kwargs):
        """
        apply search filter on queryset based on the search params provided in request
        :param query_params: a dictionary, generally request.GET
        :param queryset: queryset on which filtering should be applied
        :param kwargs: extra params
        :return: queryset with search filters applied
        """
        if queryset is None:
            return self.model.objects.none()
        _searched_fields = self._prepare_search_fields(query_params=query_params)
        for key, value in _searched_fields:
            if len(value) > 0:
                if key.startswith('custom:'):
                    if not hasattr(self.model, key.replace(':', '__') + '_search'):
                        continue
                    queryset = getattr(self.model, key.replace(':', '__') + '_search')(queryset, value)
                else:
                    entry_query = self._build_search_query(self.model, key, value)
                    if entry_query is not None:
                        queryset = queryset.filter(entry_query)
        return queryset

    def _add_sign_prefix(self, descending_sorts, field_name):
        if descending_sorts.get(field_name.replace('-', '')):
            if not field_name.startswith('-'):
                return '-' + field_name
            else:
                return field_name
        else:
            if field_name.startswith('-'):
                return field_name.replace('-', '')
            else:
                return field_name

    def _apply_distinct(self, queryset=None, order_by=None, **kwargs):
        if hasattr(self.model, "distinct_fields"):
            # TODO: Update with regular expression, to avoid hassle processing model name containing 'details'
            distinct_fields = [f for f in getattr(self.model, "distinct_fields")()]
            _orderings = list(distinct_fields)
            if not order_by:
                kwargs.update({"request": self.request})
                order_by = self.model.default_order_by(**kwargs)
            if type(order_by) == str:
                _orderings += [order_by]
            else:
                _orderings += list(order_by)
            _queryset = queryset.order_by(*_orderings)
            item_ids = _queryset.distinct(*distinct_fields).values_list('pk', flat=True)
            queryset = queryset.model.objects.filter(pk__in=item_ids)

            # TODO: The following order by is redundant. This has been required to apply distinct in the ordered
            # queryset and then again ordering it in required order. Will be handful to get a work around here
            if type(order_by) == str:
                queryset = queryset.order_by(order_by)
            else:
                order_by = list(order_by)
                queryset = queryset.order_by(*order_by)
        return queryset

    def get_queryset(self, **kwargs):
        """
        This method is used to generate appropriate queryset for current request
        returns filtered queryset
        """
        _user = self.request.user
        _sort_by = self.request.GET.get('sort')
        # Assuming all objects first
        _queryset = self.model.objects.all()
        _queryset = self._apply_search_filter(query_params=self.request.GET, queryset=_queryset, **kwargs)
        order_by_filter = []
        if _sort_by:
            _descending_sorts = {_sort_by.replace('-', ''): _sort_by.startswith('-')}
            _field_name = _sort_by.replace("-", "").replace("render_", "")
            _field_name = _field_name.split(":")[0]
            _field = self.model._meta.get_field(_field_name.replace("-", ""))
            if isinstance(_field, models.ForeignKey) or isinstance(_field, models.ManyToManyField):
                if hasattr(_queryset.model, "order_by_%s" % _field_name.replace('-', '')):
                    order_by_filter = getattr(_queryset.model,
                                              "order_by_%s" % _field_name.replace('-', ''))()
                    temp_filters = []
                    for of in order_by_filter:
                        if _descending_sorts.get(_field.name.replace('-', '')):
                            if not of.startswith('-'):
                                temp_filters += ['-' + of]
                            else:
                                temp_filters += [of]
                        else:
                            if of.startswith('-'):
                                temp_filters += [of.replace('-', '')]
                            else:
                                temp_filters += [of]
                    order_by_filter = temp_filters
                else:
                    try:
                        _name = _field.remote_field.model._meta.get_field('name')
                    except Exception as exp:
                        _name = None
                    if _name:
                        order_by_filter = [self._add_sign_prefix(_descending_sorts, _field.name) + "__name"]
                    else:
                        order_by_filter = []
            else:
                if _descending_sorts.get(_sort_by.replace('-', '')):
                    if not _field_name.startswith('-'):
                        order_by_filter = ['-' + _field_name]
                    else:
                        order_by_filter = [_field_name]
                else:
                    if _field_name.startswith('-'):
                        order_by_filter = [_field_name.replace('-', '')]
                    else:
                        order_by_filter = [_field_name]
            if not ('pk' in order_by_filter or '-pk' in order_by_filter):
                order_by_filter.append('pk')
            _queryset = _queryset.order_by(*order_by_filter)
        else:
            kwargs.update({'request': self.request})
            order_by = self.model.order_by(**kwargs)
            if type(order_by) == str:
                _queryset = _queryset.order_by(order_by)
            else:
                order_by = list(order_by)
                _queryset = _queryset.order_by(*order_by)
        _queryset = self._apply_distinct(queryset=_queryset, order_by=order_by_filter)
        return _queryset
