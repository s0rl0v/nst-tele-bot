import sys


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class LambdaBase(object):
    @classmethod
    def get_handler(cls, *args, **kwargs):
        def handler(event, context):
            return cls(*args, **kwargs).handle(event, context)
        return handler

    def handle(self, event, context):
        raise NotImplementedError


def LambdaHandler(func):
    module = func.__module__
    handler_name = f'{func.__name__}Handler'
    setattr(sys.modules[module], handler_name, func.get_handler())
    return func
