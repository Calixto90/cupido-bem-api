import os

from flask import Flask, render_template

from config import config_by_name


def create_app(config_name=None):
    config_name = config_name or os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    db_uri = app.config.get("SQLALCHEMY_DATABASE_URI") or ""
    if db_uri.startswith("sqlite"):
        os.makedirs(os.path.join(app.root_path, "..", "instance"), exist_ok=True)

    _registrar_extensoes(app)
    _registrar_blueprints(app)
    _registrar_error_handlers(app)

    return app


def _registrar_extensoes(app):
    from app.extensions import csrf, db, limiter, login_manager, migrate

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Faça login para acessar esta página."
    csrf.init_app(app)
    limiter.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User

        return User.query.get(int(user_id))


def _registrar_blueprints(app):
    from app.admin import admin_bp
    from app.auth import auth_bp
    from app.caixa import caixa_bp
    from app.consignacoes import consignacoes_bp
    from app.equipes import equipes_bp
    from app.main import main_bp
    from app.precificacao import precificacao_bp
    from app.produtos import produtos_bp
    from app.relatorios import relatorios_bp
    from app.vendas import vendas_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(produtos_bp)
    app.register_blueprint(equipes_bp)
    app.register_blueprint(precificacao_bp)
    app.register_blueprint(consignacoes_bp)
    app.register_blueprint(vendas_bp)
    app.register_blueprint(caixa_bp)
    app.register_blueprint(relatorios_bp)


def _registrar_error_handlers(app):
    @app.errorhandler(403)
    def forbidden(_error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(_error):
        return render_template("errors/500.html"), 500
