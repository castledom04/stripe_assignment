from rest_framework.views import exception_handler


def app_exception_handler(exc, context):
    response = exception_handler(exc, context)
    return response
