import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_oauthlib.provider import OAuth2Provider
import dotenv

dotenv.load_dotenv()
db = SQLAlchemy()
oauth = OAuth2Provider()
url_prefix = "/ims/oneroster/v1p1"

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database.db').replace('\\', '/')}"
    app.config["OAUTH2_PROVIDER_TOKEN_EXPIRES_IN"] = 3600
    if os.environ.get("MODE") != "PRODUCTION":
        os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")
    db.init_app(app)

    from .models.AcademicSessions import AcademicSession
    from .models.Category import Category
    from .models.Class import Class
    from .models.Course import Course
    from .models.Demographics import Demographics
    from .models.Enrollment import Enrollment
    from .models.LineItem import LineItem
    from .models.Org import Org
    from .models.OAuthClient import ONEROSTER_SCOPES, OAuthClient
    from .models.OAuthNonce import OAuthNonce
    from .models.OAuthToken import OAuthToken
    from .models.ProviderConfiguration import ProviderConfiguration
    from .models.ProviderImportRun import ProviderImportRun
    from .models.ImportedRecord import ImportedRecord
    from .models.Resource import Resource
    from .models.Result import Result
    from .models.User import User

    with app.app_context():
        db.create_all()
        if not OAuthClient.query.filter_by(client_id=os.environ.get("ONEROSTER_CLIENT_ID", "oneroster-client")).first():
            db.session.add(
                OAuthClient(
                    client_id=os.environ.get("ONEROSTER_CLIENT_ID", "oneroster-client"),
                    client_secret=os.environ.get("ONEROSTER_CLIENT_SECRET", "oneroster-secret"),
                    scopes_text=os.environ.get("ONEROSTER_CLIENT_SCOPES", " ".join(ONEROSTER_SCOPES)),
                )
            )
            db.session.commit()

    from .routes.oauth import oauth_routes as oauth_blueprint
    from .routes.docs import docs_routes as docs_blueprint
    from .routes.frontend import frontend as frontend_blueprint
    from .routes.rostering import rostering as rostering_blueprint
    from .routes.resources import resources as resources_blueprint
    from .routes.gradebooks import gradebooks as gradebooks_blueprint
    from .routes.provider_configurations import (
        provider_configurations as provider_configurations_blueprint,
    )
    
    app.register_blueprint(frontend_blueprint)
    app.register_blueprint(docs_blueprint, url_prefix=url_prefix)
    app.register_blueprint(oauth_blueprint, url_prefix=url_prefix)
    app.register_blueprint(rostering_blueprint, url_prefix=url_prefix)
    app.register_blueprint(resources_blueprint, url_prefix=url_prefix)
    app.register_blueprint(gradebooks_blueprint, url_prefix=url_prefix)
    app.register_blueprint(provider_configurations_blueprint, url_prefix=url_prefix)

    oauth.init_app(app)
    return app
    
