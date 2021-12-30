from django.db.models import Q

from django_classic.enums.util_enums import ModelRuntimeCacheType


def load_into_cache(model=None, key=None, filters=None, fields=None, order_by=None,
                    value_type=ModelRuntimeCacheType.SINGLE):
    if not model or not filter or not fields:
        return {}
    _cached_entities = {}
    _queryset = model.objects.filter(Q(**filters)).values(*fields)
    if order_by:
        _queryset = _queryset.order_by(order_by)
    for _instance in _queryset:
        if _instance[key] is None:
            continue
        if value_type == ModelRuntimeCacheType.SINGLE:
            _cached_entities[_instance[key]] = _instance
        elif value_type == ModelRuntimeCacheType.MANY:
            if _instance[key] not in _cached_entities:
                _cached_entities[_instance[key]] = [_instance]
            else:
                _cached_entities[_instance[key]].append(_instance)
    return _cached_entities
