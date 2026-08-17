from flask import flash, redirect, render_template, url_for
from flask_login import login_required

from app.decorators import permission_required
from app.equipes import equipes_bp
from app.equipes.forms import EquipeForm
from app.extensions import db
from app.models.equipe import Equipe
from app.models.user import User


def _vendedor_choices(equipe=None):
    query = User.query.filter_by(role="vendedor", ativo=True)
    if equipe is not None:
        query = query.filter(db.or_(User.equipe_id.is_(None), User.equipe_id == equipe.id))
    else:
        query = query.filter(User.equipe_id.is_(None))
    return [(u.id, f"{u.nome} ({u.email})") for u in query.order_by(User.nome)]


@equipes_bp.route("/")
@login_required
@permission_required("admin", "gerente")
def listar_equipes():
    equipes = Equipe.query.filter_by(ativo=True).order_by(Equipe.nome).all()
    return render_template("equipes/listar.html", equipes=equipes)


@equipes_bp.route("/novo", methods=["GET", "POST"])
@login_required
@permission_required("admin", "gerente")
def nova_equipe():
    form = EquipeForm()
    form.vendedores.choices = _vendedor_choices()
    if form.validate_on_submit():
        if Equipe.query.filter_by(nome=form.nome.data.strip()).first():
            flash("Já existe uma equipe com esse nome.", "error")
        else:
            equipe = Equipe(nome=form.nome.data.strip(), descricao=form.descricao.data)
            db.session.add(equipe)
            db.session.flush()
            for vendedor_id in form.vendedores.data:
                User.query.get(vendedor_id).equipe_id = equipe.id
            db.session.commit()
            flash("Equipe criada.", "success")
            return redirect(url_for("equipes.listar_equipes"))
    return render_template("equipes/form.html", form=form, titulo="Nova equipe")


@equipes_bp.route("/<int:equipe_id>/editar", methods=["GET", "POST"])
@login_required
@permission_required("admin", "gerente")
def editar_equipe(equipe_id):
    equipe = Equipe.query.get_or_404(equipe_id)
    form = EquipeForm(obj=equipe)
    form.vendedores.choices = _vendedor_choices(equipe)
    if form.validate_on_submit():
        duplicado = Equipe.query.filter(Equipe.nome == form.nome.data.strip(), Equipe.id != equipe.id).first()
        if duplicado:
            flash("Já existe outra equipe com esse nome.", "error")
        else:
            equipe.nome = form.nome.data.strip()
            equipe.descricao = form.descricao.data
            selecionados = set(form.vendedores.data)
            for membro in list(equipe.membros):
                if membro.id not in selecionados:
                    membro.equipe_id = None
            for vendedor_id in selecionados:
                User.query.get(vendedor_id).equipe_id = equipe.id
            db.session.commit()
            flash("Equipe atualizada.", "success")
            return redirect(url_for("equipes.listar_equipes"))
    elif not form.is_submitted():
        form.vendedores.data = [m.id for m in equipe.membros]
    return render_template("equipes/form.html", form=form, titulo="Editar equipe")


@equipes_bp.route("/<int:equipe_id>/excluir", methods=["POST"])
@login_required
@permission_required("admin", "gerente")
def excluir_equipe(equipe_id):
    equipe = Equipe.query.get_or_404(equipe_id)
    if equipe.tem_consignacao_ativa():
        flash("Não é possível excluir: a equipe tem consignações ativas.", "error")
        return redirect(url_for("equipes.listar_equipes"))
    for membro in list(equipe.membros):
        membro.equipe_id = None
    equipe.ativo = False
    db.session.commit()
    flash("Equipe excluída.", "success")
    return redirect(url_for("equipes.listar_equipes"))
