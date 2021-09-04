__author__ = 'shamilsakib'

from django.apps import apps


def decorate(*decorators):
    def register_wrapper(_origin_class):
        for _decorator_func in decorators[::-1]:
            _origin_class = _decorator_func(_origin_class)
        _origin_class._decorators = decorators
        return _origin_class

    return register_wrapper


def enable_api(route):
    def enable_api(original_class):
        original_class._enable_api = {'route': route}
        return original_class

    return enable_api


def get_orm_models_by_decorator_in_app(app_name, decorator=None, include_class=False, **kwargs):
    _classes = list()
    _app = apps.get_app_config(app_name)
    _decorator_attr = '_{}'.format(decorator)
    for _model in _app.get_models():
        for _decorator in getattr(_model, '_decorators', []):
            if _decorator.__name__ == decorator:
                _class = _model if include_class else _model.__name__
                _classes.append((_app, _class, getattr(_model, _decorator_attr)))
    return _classes


def get_orm_models_by_decorator(decorator, apps, include_class=False, **kwargs):
    _classes = list()
    for app in apps:
        _app_name = app[app.rfind(".") + 1:]
        _classes += get_orm_models_by_decorator_in_app(
            _app_name, decorator=decorator, include_class=include_class, **kwargs)
    return _classes
