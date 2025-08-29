import re
import shutil
import logging
from pathlib import Path
import os
import requests


def sanitize_jinja(template_text: str) -> str:
    """Replaces jinja tags with html encoded characters
    Attribution: https://stackoverflow.com/a/17730939

    Args:
        template_text (str): The text to sanitize

    Returns:
        str: The sanitized text
    """
    mappings = {
        r"{{": "&#123;&#123;",  # Jinja Expressions
        r"}}": "&#125;&#125;",
        r"{%": "&#123;&#37;",  # Jinja Statements
        r"%}": "&#37;&#125;",
        r"{#": "&#123;&#35;",  # Jinja Comments
        r"#}": "&#35;&#125;",
    }

    return re.sub(
        "|".join(rf"{re.escape(mapping)}" for mapping in mappings),
        lambda match: mappings[match.group(0)],
        template_text,
    )


def replace_placeholders(template_text: str) -> str:
    """Replace placeholders in the template text with the appropriate jinja tags
    Attribution: https://stackoverflow.com/a/17730939

    Args:
        template_text (str): The source text

    Returns:
        str: The `template_text` with placeholders replaced
    """
    mappings = {
        "__APP_HEAD_PRE__": "{{ APP_HEAD_PRE }}",
        "__APP_HEAD_POST__": "<style> .env-marker { color: red; font-weight: bold; }</style>{% block head_extra %}{% endblock %}",
        "__PAGE_TITLE__": "{{ PAGE_TITLE | wrap_env }}",
        "__APP_TITLE__": "{{ APP_TITLE | wrap_env_css }}",
        "__APP_URL__": "{{ APP_URL }}",
        "__APP_LOGIN__": '{% if current_user.is_authenticated is true %}<span style="color: grey;">Logged in as {{g.user.upn}}</span> | <a href="/logout">Logout</a>{% else %}<a href="/login">Login</a>{% endif %}',
        "__APP_MENU__": '{% include "appmenu.html" ignore missing %}<ul id="udm" class="udm">{% block app_menu %}{% endblock %}</ul>',
        "__APP_CONTENT__": "{% block content %}{% endblock %}<br>",
        "__ERROR_CONTENT__": "{{ error_content }}",
        "__CONTACT_LABEL__": "{{ CONTACT_LABEL }}",
        "__CONTACT_URL__": "{{ CONTACT_URL }}",
        "__ELAPSED_TIME__": "{{ g.request_time() }}",
        "__APP_EXTRA_LOWER_LEFT__": "{% block app_extra_lower_left %}{% endblock %}",
        "__APP_EXTRA_LOWER_RIGHT__": "{% block app_extra_lower_right %}{% endblock %}",
        "__APP_EXTRA_UPPER_RIGHT__": "{% block app_extra_upper_right %}{% endblock %}",
    }

    return re.sub(
        "|".join(rf"{re.escape(mapping)}" for mapping in mappings),
        lambda match: mappings[match.group(0)],
        template_text,
    )


def update_apptemplate(template_url="https://apptemplate.mst.edu/v3-jinja-safe/"):
    """Downloads latest apptemplate to base.html if base.html does not already exist.
    Includes steps to sanitize existing jinja tags and replaces certain placeholders with corresponding jinja tags.

    Args:
        template_url (str, optional): What URL to pull the template from. Defaults to "https://apptemplate.mst.edu/v3-jinja-safe/".

    Raises:
        RuntimeError: Response from `template_url` not OK
    """
    template_dir = Path(Path(__file__).parent.resolve(), "templates")
    base_location = Path(template_dir, "base.html")

    if os.path.isfile(base_location):
        return

    try:
        template_request = requests.get(template_url, timeout=5)
        template_request.raise_for_status()
        template_text = sanitize_jinja(template_request.text.expandtabs(4))
        template_text = replace_placeholders(template_text)
        with open(base_location, mode="w", encoding="utf8") as fh:
            fh.write(template_text)
    except Exception:
        default_location = Path(Path(template_dir, "default.html"))
        shutil.copyfile(default_location, base_location)
        logging.warning(f"Could not load new app template from url '{template_url}'!")
