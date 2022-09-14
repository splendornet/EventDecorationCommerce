# django imports
from django.core.exceptions import PermissionDenied


def check_is_superuser(function):

    """
    Custom decorator to check user is admin.
    :param function:
    :return: true/false
    """

    def wrap(request, *args, **kwargs):
        if request.user.is_superuser:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
