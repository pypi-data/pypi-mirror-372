from markupsafe import Markup

from mst.core import local_env


def wrap_env(app_title: str, use_css: bool = False) -> str:
    """Wraps the input string with the current local_env, if not prod

    Simple CSS to add to any application to control the color:
        .env-marker {
            color: red;
            font-weight: bold;
        }

    Args:
        app_title (str): The string to wrap, usually the APP_TITLE
        use_css(bool): If True, the markup tags will be provided so that
            css can be used in the appliction, otherwise, just plain text
            is provided.  Defaults to False, for compatibility.

    Returns:
        str: The input string wrapped with the local_env
    """
    env = local_env()
    if env != "prod":
        ENV = env.upper()
        if use_css:
            tag = f'<span class="env-marker">{ENV}</span>'
            return Markup(f"{tag} - {app_title} - {tag}")
        else:
            return f"{ENV} - {app_title} - {ENV}"
    return app_title
