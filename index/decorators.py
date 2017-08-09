from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def group_required(*group_names):
    def in_groups(u):
        if u.is_authenticated():
            if u.groups.filter(name__in=group_names).count() > 0 or u.is_superuser:
                return True
        raise PermissionDenied("Not part of required group")

    actual_decorator = user_passes_test(
        in_groups,
        login_url='index:staffLogin',
        redirect_field_name='next',
    )

    return actual_decorator

def superuser_required(fn):
    def wrapper(*args, **kw):
        request = args[0]
        if request.user.is_superuser:
            return fn(*args, **kw)
        raise PermissionDenied("Didnt think so!")

    return wrapper

def staff_required(fn):
    def wrapper(*args, **kw):
        request = args[0]
        if request.user.is_staff:
            return fn(*args, **kw)
        raise PermissionDenied("Didnt think so!")

    return wrapper