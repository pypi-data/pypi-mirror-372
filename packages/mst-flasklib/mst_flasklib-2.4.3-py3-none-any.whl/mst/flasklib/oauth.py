from flask import Flask
from authlib.integrations.flask_client import OAuth
from mst.vault import MSTVault


oauth = OAuth()


def init_oauth(app: Flask):
    """Registers and initalizes the oauth connection

    Args:
        app (Flask): the current flask app
    """
    if not app.config["OIDC_VAULT_PATH"]:
        raise RuntimeError(
            "missing OIDC_VAULT_PATH environment variable! (this is needed for oauth mechanisms to work)"
        )

    vault = MSTVault()
    oidc_data = vault.read_secret(app.config["OIDC_VAULT_PATH"])

    oauth.register(
        name="azure",
        client_id=oidc_data["OIDC_CLIENT_ID"],
        client_secret=oidc_data["OIDC_CLIENT_SECRET"],
        server_metadata_url=app.config["OAUTH_CONF_URL"],
        client_kwargs={"scope": "openid email profile"},
    )

    oauth.init_app(app)
