from functools import wraps

from flask import abort, request
from flask_login import current_user

from app.extensions import db
from app.models.log_seguranca import LogSeguranca


def permission_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if not current_user.is_role(*roles):
                log = LogSeguranca(
                    evento="permissao_negada",
                    user_id=current_user.id,
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get("User-Agent"),
                    rota=request.path,
                    detalhes=f"role={current_user.role} rotas_permitidas={roles}",
                )
                db.session.add(log)
                db.session.commit()
                abort(403)
            return view_func(*args, **kwargs)

        return wrapped

    return decorator
