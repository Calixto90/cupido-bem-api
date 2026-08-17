from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.admin import admin_bp
from app.admin.forms import UsuarioForm
from app.decorators import permission_required
from app.extensions import db
from app.models.equipe import Equipe
from app.models.log_seguranca import LogSeguranca
from app.models.user import User


def _equipe_choices():
    return [(0, "-- nenhuma --")] + [(e.id, e.nome) for e in Equipe.query.filter_by(ativo=True).order_by(Equipe.nome)]


@admin_bp.route("/usuarios")
@login_required
@permission_required("admin")
def listar_usuarios():
    usuarios = User.query.order_by(User.nome).all()
    return render_template("admin/usuarios.html", usuarios=usuarios)


@admin_bp.route("/usuarios/novo", methods=["GET", "POST"])
@login_required
@permission_required("admin")
def novo_usuario():
    form = UsuarioForm()
    form.equipe_id.choices = _equipe_choices()
    if form.validate_on_submit():
        if not form.senha.data:
            flash("Senha é obrigatória para novo usuário.", "error")
        elif User.query.filter_by(email=form.email.data.lower().strip()).first():
            flash("Já existe um usuário com esse email.", "error")
        else:
            usuario = User(
                nome=form.nome.data.strip(),
                email=form.email.data.lower().strip(),
                role=form.role.data,
                equipe_id=form.equipe_id.data or None,
                ativo=form.ativo.data,
            )
            usuario.set_senha(form.senha.data)
            db.session.add(usuario)
            db.session.commit()
            flash("Usuário criado.", "success")
            return redirect(url_for("admin.listar_usuarios"))
    return render_template("admin/usuario_form.html", form=form, titulo="Novo usuário")


@admin_bp.route("/usuarios/<int:usuario_id>/editar", methods=["GET", "POST"])
@login_required
@permission_required("admin")
def editar_usuario(usuario_id):
    usuario = User.query.get_or_404(usuario_id)
    form = UsuarioForm(obj=usuario)
    form.equipe_id.choices = _equipe_choices()
    if request.method == "GET":
        form.equipe_id.data = usuario.equipe_id or 0
    if form.validate_on_submit():
        email_normalizado = form.email.data.lower().strip()
        existente = User.query.filter(User.email == email_normalizado, User.id != usuario.id).first()
        if existente:
            flash("Já existe outro usuário com esse email.", "error")
        else:
            usuario.nome = form.nome.data.strip()
            usuario.email = email_normalizado
            usuario.role = form.role.data
            usuario.equipe_id = form.equipe_id.data or None
            usuario.ativo = form.ativo.data
            if form.senha.data:
                usuario.set_senha(form.senha.data)
            db.session.commit()
            flash("Usuário atualizado.", "success")
            return redirect(url_for("admin.listar_usuarios"))
    return render_template("admin/usuario_form.html", form=form, titulo="Editar usuário")


@admin_bp.route("/usuarios/<int:usuario_id>/desativar", methods=["POST"])
@login_required
@permission_required("admin")
def desativar_usuario(usuario_id):
    usuario = User.query.get_or_404(usuario_id)
    usuario.ativo = False
    db.session.commit()
    flash("Usuário desativado.", "success")
    return redirect(url_for("admin.listar_usuarios"))


@admin_bp.route("/logs")
@login_required
@permission_required("admin")
def logs_seguranca():
    logs = LogSeguranca.query.order_by(LogSeguranca.data_evento.desc()).limit(200).all()
    return render_template("admin/logs.html", logs=logs)
