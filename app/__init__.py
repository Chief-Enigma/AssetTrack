from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager


db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)

    app.config.from_object("config.Config")

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Bitte melde dich zuerst an."
    login_manager.login_message_category = "warning"

    from app import models

    from app.main.routes import main
    from app.auth.routes import auth
    from app.api.routes import api
    from app.devices.routes import devices
    from app.categories.routes import categories
    from app.maintenance.routes import maintenance
    from app.system.routes import system

    app.register_blueprint(main)

    app.register_blueprint(
        auth,
        url_prefix="/auth"
    )

    app.register_blueprint(
        api,
        url_prefix="/api"
    )

    app.register_blueprint(
        devices,
        url_prefix="/devices"
    )

    app.register_blueprint(
        categories,
        url_prefix="/categories"
    )

    app.register_blueprint(
        maintenance,
        url_prefix="/maintenance"
    )

    app.register_blueprint(
        system,
        url_prefix="/system"
    )

    return app