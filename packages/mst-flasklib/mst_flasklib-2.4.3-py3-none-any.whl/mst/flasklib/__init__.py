from flask import Blueprint, Flask, g
from .before_request import register_before_request
from .routes import register_error_handlers
from .routes import oauth_bp
from .login_manager import init_login, has_priv
from .oauth import init_oauth
from .apptemplate import update_apptemplate
from .logging import configure_logging
from . import util


bp = Blueprint("mstflask", __name__, template_folder="templates")


class MSTFlask:
    """The main entrypoint to the MSTFlask module.
    Create an instance then call `init_app(app)` to initialize and configure the module.
    """

    def init_app(self, app: Flask):
        """Initalizes and configures the MSTFlask module.

        Args:
            app (Flask): The current flask application.
        """
        # Configure Logging
        configure_logging(app)

        # Register the blueprint for MSTFlask
        app.register_blueprint(bp)

        # Update apptemplate
        update_apptemplate(app.config["APP_TEMPLATE"])

        # Register the before request handlers
        register_before_request(app)

        # Register the error handlers
        register_error_handlers(app)

        # Register the health check
        @app.route("/health")
        def health():
            return "OK\n"

        # Initialize the login manager
        init_login(app)

        # Initalize the oauth connection
        init_oauth(app)

        # Register the auth flow blueprint
        app.register_blueprint(oauth_bp)

        # Provides values to all templates
        @app.context_processor
        def render_base_template():
            base_template_vars = {
                "APP_TITLE": app.config["APP_TITLE"],
                "PAGE_TITLE": app.config.get("PAGE_TITLE", app.config["APP_TITLE"]),
                "CONTACT_LABEL": app.config["CONTACT_LABEL"],
                "CONTACT_URL": app.config["CONTACT_URL"],
                "APP_URL": app.config["APP_URL"],
            }

            base_template_funcs = {"has_priv": has_priv}

            return base_template_vars | base_template_funcs

        @app.template_filter()
        def wrap_env(value):
            return util.wrap_env(value)

        @app.template_filter()
        def wrap_env_css(value):
            return util.wrap_env(value, use_css=True)
