from functools import wraps
from uuid import uuid4

from flask import abort
from flask_login import current_user
from werkzeug.utils import secure_filename


def roles_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                abort(403)
            return view(*args, **kwargs)

        return wrapped

    return decorator


def unique_filename(filename):
    safe_name = secure_filename(filename)
    extension = safe_name.rsplit(".", 1)[-1].lower()
    return f"{uuid4().hex}.{extension}"

