from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*roles):
    """Restrict a view to specific roles, e.g. @role_required('ADMIN', 'TEACHER')"""

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("accounts:login")
            if request.user.is_superuser and "ADMIN" in roles:
                return view_func(request, *args, **kwargs)
            if request.user.role not in roles:
                messages.error(request, "You do not have permission to view that page.")
                return redirect("accounts:home")
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator
