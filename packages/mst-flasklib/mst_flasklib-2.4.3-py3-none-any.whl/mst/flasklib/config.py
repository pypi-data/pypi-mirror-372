import os
import logging
import warnings
from markupsafe import Markup

from mst.core import local_env
from . import util


class DefaultConfig:
    """Default configuration settings applicable to most/all applications. May be overridden per app."""

    INDEX_VIEW = "main.index"

    CONTACT_LABEL = "IT HelpDesk"
    CONTACT_URL = "https://help.mst.edu"

    DEBUG = False
    TESTING = False
    LOG_LEVEL = logging.INFO

    OIDC_VAULT_PATH = os.getenv("OIDC_VAULT_PATH")
    if not OIDC_VAULT_PATH and os.getenv("DEVEL"):
        OIDC_VAULT_PATH = "apps-shared/k8s/k8s-localhost-dev/oidc-env"

    OAUTH_CONF_URL = (
        "https://login.microsoftonline.com/e3fefdbe-f7e9-401b-a51a-355e01b05a89/v2.0/.well-known/openid-configuration"
    )
    LOGOUT_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/logout"

    LOCAL_ENV = local_env()
    APP_URL = os.getenv("APP_URL", "/")
    APP_TEMPLATE = os.getenv("APP_TEMPLATE", "https://apptemplate.mst.edu/v4-alpha/")

    if LOCAL_ENV == "dev":
        DEBUG = True
        LOG_LEVEL = logging.DEBUG

    @classmethod
    def wrap_env(cls, app_title: str, use_css: bool = False) -> str:
        warnings.warn(
            "DefaultConfig.wrap_env() is deprecated; "
            "please use mst.flasklib.util.wrap_env() "
            "(or {{ title | wrap_env }} filter) instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return util.wrap_env(app_title, use_css=use_css)
