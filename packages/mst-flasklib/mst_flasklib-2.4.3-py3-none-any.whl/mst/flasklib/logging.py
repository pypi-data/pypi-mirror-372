import logging
from flask import Flask
from flask.logging import default_handler


def configure_logging(app: Flask):
    """Configures the logger for the provided Flask app

    Args:
        app (Flask): The flask app to configure logging on
    """
    logging.captureWarnings(True)
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s] %(levelname)s in %(name)s:%(module)s:%(filename)s:%(funcName)s - %(lineno)d: %(message)s ",
                }
            },
            "handlers": {
                "console": {
                    "level": app.config["LOG_LEVEL"],
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "stream": "ext://sys.stdout",
                },
            },
            "loggers": {
                "defaultapp": {
                    "handlers": ["console"],
                    "level": app.config["LOG_LEVEL"],
                    "propagate": False,
                }
            },
            "root": {
                "level": app.config["LOG_LEVEL"],
                "handlers": ["console"],
            },
        }
    )

    # Remove the default handler
    app.logger.removeHandler(default_handler)
