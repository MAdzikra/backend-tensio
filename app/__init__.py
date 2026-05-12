from flask import Flask
from flask_cors import CORS
from app.extensions import db, bcrypt, jwt
from app.routes.auth import auth
from app.routes.profile import profile
from app.routes.screening import screening
from app.routes.admin import admin
from app.extensions import db, bcrypt, jwt, migrate, mail
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    # register routes
    app.register_blueprint(auth, url_prefix="/api/auth")
    app.register_blueprint(profile, url_prefix="/api")
    app.register_blueprint(screening, url_prefix="/api")
    app.register_blueprint(admin, url_prefix="/api/admin")

    return app