from __future__ import annotations

from functools import wraps
from typing import Callable, TypeVar

from flask import g, jsonify, session

from app.extensions import db
from app.models import User

F = TypeVar("F", bound=Callable[..., object])


def current_user() -> User | None:
    uid = session.get("user_id")
    if not uid:
        return None
    return db.session.get(User, uid)


def login_required(f: F) -> F:
    @wraps(f)
    def wrapper(*args, **kwargs):
        user = current_user()
        if user is None:
            return jsonify({"error": "Unauthorized"}), 401
        g.current_user = user
        return f(*args, **kwargs)

    return wrapper  # type: ignore[return-value]
