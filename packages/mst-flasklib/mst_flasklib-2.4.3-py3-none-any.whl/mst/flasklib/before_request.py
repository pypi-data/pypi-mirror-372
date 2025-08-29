import getpass
import inspect
import os
import re
import sys
import time

from flask import (
    g,
    current_app,
    session,
    request,
    Flask,
)
from mst.core.usage_logger import _SendUsagePacket


def register_before_request(app: Flask):
    """Registers before_request functions for the app.

    Current handlers:
        log-route: Sends info about the current request's route to apiusage
        time_taken_on_request: Adds request time taken to context for use in template

    Args:
        app (Flask): The flask app to register against
    """
    skip_decorators = (("ttl_cache.py", "fn_wrapped"),)

    @app.before_request
    def log_route():
        # If this fails, we don't have an endpoint or function there so no logging needed
        if request.endpoint is None or request.endpoint not in current_app.view_functions:
            return None

        end_func = current_app.view_functions[request.endpoint]
        end_func_file = inspect.getsourcefile(end_func)

        authuser = None
        try:
            authuser = session["user"]["upn"].split("@")[0]
        except AttributeError:
            pass
        except KeyError:
            pass

        caller_file = request.url
        caller_name = os.path.basename(sys.argv[0])

        if m := re.search(r"^/local/(.*?)/", sys.argv[0]):
            usage_logger_owner = m[1]

        _SendUsagePacket(
            msg="",
            user=getpass.getuser(),
            script=end_func_file,
            scriptowner=usage_logger_owner,
            cwd=os.getcwd(),
            authuser=authuser,
            server=request.host,
            function=end_func.__name__,
            function_file=end_func_file,
            caller=caller_name,
            caller_file=caller_file,
            language="python",
            type="flask",
        )

        return None

    # Adds request_time function to g for use in templates
    @app.before_request
    def time_taken_on_request():
        g.request_start_time = time.time()
        g.request_time = lambda: f"{time.time()-g.request_start_time:.2}"
