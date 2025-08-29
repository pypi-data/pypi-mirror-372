from flask import (
    Blueprint,
    g,
    redirect,
    url_for,
    current_app,
    session,
    request,
    Flask,
    render_template,
)
from flask_login import login_user, login_required, logout_user
from mst.flasklib.oauth import oauth
from .login_manager import User


def register_error_handlers(app: Flask):
    """Registers all of the HTTP error handlers for the app.

    Args:
        app (Flask): The flask app to register against
    """

    @app.errorhandler(400)
    def bad_request(_):
        """Error handler for HTTP 400 - Bad Request errors."""
        return render_template("errors/400.html"), 400

    @app.errorhandler(401)
    def unauthorized(_):
        """Error handler for HTTP 401 - Unauthorized."""
        return render_template("errors/401.html"), 401

    @app.errorhandler(403)
    def forbidden(error):
        """Error handler for HTTP 403 - Forbidden errors."""
        if isinstance(error.description, dict):
            priv_code = error.description.get("priv_code", "undefined")
        else:
            priv_code = "undefined"
        return render_template("errors/403.html", priv_code=priv_code), 403

    @app.errorhandler(404)
    def page_not_found(_):
        """Error handler for HTTP 404 - Page Not Found errors."""
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(_):
        """Error handler for HTTP 500 - Internal Server Error errors."""
        return render_template("errors/500.html"), 500


# Handle Authentication Routes
oauth_bp = Blueprint("oauth", __name__)


@oauth_bp.route("/login")
def login():
    """Directs the user to azure for login"""
    current_app.logger.debug("login")
    redirect_uri = url_for("oauth.oidc_redirect", _external=True)
    session["next_url"] = request.args.get("next")
    return oauth.azure.authorize_redirect(redirect_uri)


@oauth_bp.route("/oidc/redirect_uri")
def oidc_redirect():
    """Logs the user in and redirects to index."""
    current_app.logger.debug("auth check")
    token = oauth.azure.authorize_access_token()

    session["user"] = token["userinfo"]

    user = User(
        id_=token["userinfo"]["aud"],
        email=(token["userinfo"]["email"] if token["userinfo"].get("email") is not None else ""),
        upn=token["userinfo"]["upn"],
    )

    # Begin user session by logging the user in
    login_user(user)

    if session.get("next_url"):
        next_url = session.get("next_url")
        session.pop("next_url", None)
        return redirect(next_url)

    return redirect(url_for(current_app.config["INDEX_VIEW"]))


@oauth_bp.route("/logout")
@login_required
def logout():
    """Logs the user out then redirects to index."""
    current_app.logger.debug("auth logout")
    session.pop("user", None)
    g.pop("user", None)
    logout_user()
    return redirect(current_app.config["LOGOUT_URL"])
