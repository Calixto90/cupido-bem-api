from datetime import datetime, timezone

from flask import flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.auth import auth_bp
from app.auth.forms import AlterarSenhaForm, LoginForm
from app.extensions import db, limiter
from app.models.log_seguranca import LogSeguranca
from app.models.user import User


def _log_seguranca(evento, user_id=None, email_tentativa=None, detalhes=None):
    log = LogSeguranca(
        evento=evento,
        user_id=user_id,
        email_tentativa=email_tentativa,
        ip_address=request.remote_addr,
        user_agent=request.headers.get("User-Agent"),
        rota=request.path,
        detalhes=detalhes,
    )
    db.session.add(log)
    db.session.commit()


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user and user.ativo and user.check_senha(form.senha.data):
            user.ultimo_login = datetime.now(timezone.utc)
            db.session.commit()
            _log_seguranca("login_sucesso", user_id=user.id, email_tentativa=user.email)
            login_user(user)
            session.permanent = True
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.index"))

        _log_seguranca("login_falho", email_tentativa=form.email.data.lower().strip())
        flash("Email ou senha inválidos.", "error")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth_bp.route("/alterar-senha", methods=["GET", "POST"])
@login_required
def alterar_senha():
    form = AlterarSenhaForm()
    if form.validate_on_submit():
        if not current_user.check_senha(form.senha_atual.data):
            flash("Senha atual incorreta.", "error")
        elif form.nova_senha.data != form.confirmar_senha.data:
            flash("As senhas não coincidem.", "error")
        else:
            current_user.set_senha(form.nova_senha.data)
            db.session.commit()
            flash("Senha alterada com sucesso.", "success")
            return redirect(url_for("main.index"))
    return render_template("auth/alterar_senha.html", form=form)
