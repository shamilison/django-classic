__author__ = 'shamilsakib'

import hashlib
from collections import OrderedDict

from django.db.models import Count
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.pagination import _positive_int, CursorPagination, _reverse_ordering
from rest_framework.response import Response
from rest_framework.utils.urls import remove_query_param
from rest_framework.utils.urls import replace_query_param

from django_classic.extras.classic_cache import ClassicCache


class ClassicLimitOffsetAPIPagination(LimitOffsetPagination):
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('remaining_count',
             self.count - (self.offset + self.limit) if self.offset + self.limit < self.count else 0),
            ('next_offset', self.offset + self.limit if self.offset + self.limit < self.count else 0),
            ('current_page', int(self.offset / self.limit) + 1),
            ('total_page', int(self.count / self.limit) + (0 if (self.count % self.limit == 0) else 1)),
            ('results', data)
        ]))

    def get_next_link(self):
        if self.offset + self.limit >= self.count:
            return None
        try:
            url = self.request.get_full_path()
        except Exception as error:
            url = self.request.path
        url = replace_query_param(url, self.limit_query_param, self.limit)

        offset = self.offset + self.limit
        return replace_query_param(url, self.offset_query_param, offset)

    def get_previous_link(self):
        if self.offset <= 0:
            return None

        try:
            url = self.request.get_full_path()
        except Exception as error:
            url = self.request.path
        url = replace_query_param(url, self.limit_query_param, self.limit)

        if self.offset - self.limit <= 0:
            return remove_query_param(url, self.offset_query_param)

        offset = self.offset - self.limit
        return replace_query_param(url, self.offset_query_param, offset)

    def get_limit(self, request):
        if request.GET.get('disable_pagination', False):
            return 9999999  # self.max_limit
        if self.limit_query_param:
            try:
                return _positive_int(
                    request.query_params[self.limit_query_param],
                    cutoff=self.max_limit
                )
            except (KeyError, ValueError):
                pass

        return self.default_limit


class ClassicVersioningAPIPagination(ClassicLimitOffsetAPIPagination):
    def paginate_queryset(self, queryset, request, view=None):
        self.count = self._get_count(queryset)
        self.limit = self.get_limit(request)
        self.version = request.version
        if self.limit is None:
            return None
        self.offset = self.get_offset(request)
        self.request = request
        if self.count > self.limit and self.template is not None:
            self.display_page_controls = True
        if self.count == 0 or self.offset > self.count:
            return []
        return list(queryset[self.offset:self.offset + self.limit])

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.count),
            ('version', self.version),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('remaining_count',
             self.count - (self.offset + self.limit) if self.offset + self.limit < self.count else 0),
            ('next_offset', self.offset + self.limit if self.offset + self.limit < self.count else 0),
            ('current_page', int(self.offset / self.limit) + 1),
            ('total_page', int(self.count / self.limit) + (0 if (self.count % self.limit == 0) else 1)),
            ('results', data)
        ]))

    @staticmethod
    def _get_count(queryset):
        """
        Determine an object count, supporting either querysets or regular lists.
        """
        try:
            return queryset.count()
        except (AttributeError, TypeError):
            return len(queryset)


def cached_count(queryset, request):
    _count_cache_key = request.path + '_' + str(request.user.pk)
    _skip_keys = ['offset', 'limit', 'sort', 'downloaded']
    _query_filters = [key + value for key, value in request.GET.items() if key not in _skip_keys]
    _count_cache_key += '_'.join(_query_filters)
    _count_cache_key = 'query-count:' + str(request.c_organization.id) + '_' + queryset.model.__name__ + '_' + \
                       hashlib.md5(_count_cache_key.encode('utf8')).hexdigest()

    # return existing value, if any
    _count = ClassicCache.get_by_key(key=_count_cache_key)
    if _count is not None:
        return int(_count)
    # cache new value
    _count = queryset.aggregate(_count=Count('pk'))['_count']
    # Save to cache with 1 hour timeout
    ClassicCache.set_by_key(key=_count_cache_key, value=_count, expiry=60 * 60)
    return _count


class ClassicCursorAPIPagination(CursorPagination):
    cursor_query_param = 'offset'
    page_size = 200
    ordering = 'last_updated'
    limit_query_param = 'limit'
    limit_query_description = 'Number of results to return per page.'
    downloaded_query_param = 'downloaded'
    sort_query_param = 'sort'

    def get_page_size(self, request):
        if request.GET.get('disable_pagination', False):
            return 9999999
        if self.limit_query_param:
            try:
                return _positive_int(
                    request.query_params[self.limit_query_param],
                    cutoff=self.page_size
                )
            except (KeyError, ValueError):
                pass

        return self.page_size

    def get_downloaded(self, request):
        try:
            return _positive_int(
                request.query_params[self.downloaded_query_param],
            )
        except (KeyError, ValueError):
            return 0

    def get_sorting(self, request):
        try:
            return (request.query_params[self.sort_query_param],)
        except (KeyError, ValueError):
            return self.ordering

    def paginate_queryset(self, queryset, request, view=None):
        self.page_size = self.get_page_size(request)
        if not self.page_size:
            return None

        self.version = request.version
        self.downloaded = self.get_downloaded(request)

        self.base_url = request.get_full_path()
        self.ordering = self.get_ordering(request, queryset, view)
        self.ordering = self.get_sorting(request)

        self.cursor = self.decode_cursor(request)
        if self.cursor is None:
            (offset, reverse, current_position) = (0, False, None)
        else:
            (offset, reverse, current_position) = self.cursor

        # Cursor pagination always enforces an ordering.
        if reverse:
            queryset = queryset.order_by(*_reverse_ordering(self.ordering))
        else:
            queryset = queryset.order_by(*self.ordering)

        self.count = cached_count(queryset, request)

        # If we have a cursor with a fixed position then filter by that.
        if current_position is not None:
            order = self.ordering[0]
            is_reversed = order.startswith('-')
            order_attr = order.lstrip('-')

            # Test for: (cursor reversed) XOR (queryset reversed)
            if self.cursor.reverse != is_reversed:
                kwargs = {order_attr + '__lt': current_position}
            else:
                kwargs = {order_attr + '__gt': current_position}

            queryset = queryset.filter(**kwargs)

        # If we have an offset cursor then offset the entire page by that amount.
        # We also always fetch an extra item in order to determine if there is a
        # page following on from this one.
        results = list(queryset[offset:offset + self.page_size + 1])
        self.page = list(results[:self.page_size])

        # Determine the position of the final item following the page.
        self.current_page_len = len(self.page)
        if len(results) > self.current_page_len:
            has_following_position = True
            following_position = self._get_position_from_instance(results[-1], self.ordering)
        else:
            has_following_position = False
            following_position = None

        # If we have a reverse queryset, then the query ordering was in reverse
        # so we need to reverse the items again before returning them to the user.
        if reverse:
            self.page = list(reversed(self.page))

        if reverse:
            # Determine next and previous positions for reverse cursors.
            self.has_next = (current_position is not None) or (offset > 0)
            self.has_previous = has_following_position
            if self.has_next:
                self.next_position = current_position
            if self.has_previous:
                self.previous_position = following_position
        else:
            # Determine next and previous positions for forward cursors.
            self.has_next = has_following_position
            self.has_previous = (current_position is not None) or (offset > 0)
            if self.has_next:
                self.next_position = following_position
            if self.has_previous:
                self.previous_position = current_position

        # Display page controls in the browsable API if there is more
        # than one page.
        if (self.has_previous or self.has_next) and self.template is not None:
            self.display_page_controls = True

        return self.page

    def decode_cursor(self, request):
        """
        Given a request with a cursor, return a `Cursor` instance.
        """
        # Determine if we have a cursor, and if so then decode it.
        encoded = request.query_params.get(self.cursor_query_param)
        if not encoded or encoded == '0':
            return None
        return super(ClassicCursorAPIPagination, self).decode_cursor(request)

    def get_paginated_response(self, data):
        _downloaded = self.downloaded + self.current_page_len
        return Response(OrderedDict([
            ('count', self.count),
            ('version', self.version),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('remaining_count', self.count - _downloaded if self.count > _downloaded else 0),
            ('next_offset', _downloaded if self.count > _downloaded else 0),
            ('current_page', int(self.downloaded / self.page_size) + 1),
            ('total_page', int(self.count / self.page_size) + (0 if (self.count % self.page_size == 0) else 1)),
            ('results', data)
        ]))

    def encode_cursor(self, cursor):
        """
        Given a Cursor instance, return an url with encoded cursor.
        """
        encoded_url = super(ClassicCursorAPIPagination, self).encode_cursor(cursor)
        if cursor.reverse:
            return replace_query_param(encoded_url, self.downloaded_query_param, self.downloaded - self.page_size)
        else:
            return replace_query_param(encoded_url, self.downloaded_query_param, self.downloaded + self.page_size)
