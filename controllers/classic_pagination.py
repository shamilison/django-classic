__author__ = 'shamilsakib'

from collections import OrderedDict

from rest_framework.pagination import LimitOffsetPagination
from rest_framework.pagination import _positive_int, CursorPagination, _reverse_ordering
from rest_framework.response import Response
from rest_framework.utils.urls import remove_query_param
from rest_framework.utils.urls import replace_query_param


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
        if request.GET.get('disable_pagination', False) == '1':
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


class ClassicCursorAPIPagination(CursorPagination):
    page_size = 200
    ordering = 'update_time'
    limit_query_param = 'limit'
    cursor_query_param = 'offset'
    sort_query_param = 'sort'
    downloaded_query_param = 'downloaded'
    limit_query_description = 'Number of results to return per page.'

    def __init__(self):
        self.version = 'v1'
        self.downloaded = 0
        self.base_url = self.cursor = self.page = None
        self.next_position = self.previous_position = None
        self.current_page_len = self.has_next = self.has_previous = None

    def get_page_size(self, request):
        if request.GET.get('disable_pagination', False) == '1':
            return 5000
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

    def get_sorting(self, queryset, request):
        try:
            return request.query_params[self.sort_query_param],
        except (KeyError, ValueError):
            return self.ordering,

    def decode_cursor(self, request):
        """
        Given a request with a cursor, return a `Cursor` instance.
        """
        # Determine if we have a cursor, and if so then decode it.
        encoded = request.query_params.get(self.cursor_query_param)
        if not encoded or encoded == '0':
            return None
        return super(ClassicCursorAPIPagination, self).decode_cursor(request)

    def paginate_queryset(self, queryset, request, view=None):
        if request.GET.get('disable_pagination', False) == '1':
            self.page = list(queryset)
            self.current_page_len = len(self.page)
            return self.page
        self.page_size = self.get_page_size(request)
        if not self.page_size:
            return None

        self.version = request.version
        self.downloaded = self.get_downloaded(request)

        self.base_url = request.get_full_path()
        self.ordering = self.get_sorting(queryset, request)

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

    def get_paginated_response(self, data):
        _downloaded = self.downloaded + self.current_page_len
        return Response(OrderedDict([
            ('version', self.version),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('current_page', int(self.downloaded / self.page_size) + 1),
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
