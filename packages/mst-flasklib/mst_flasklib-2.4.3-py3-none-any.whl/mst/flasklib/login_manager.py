from typing import Dict
from flask_login import UserMixin, LoginManager, current_user
from flask import Flask, request, session, g

from mst.privsys.privsys import check_priv, check_priv_regex


class User(UserMixin):
    """User model for use with LoginManager"""

    def __init__(self, id_: str, email: str, upn: str):
        """Creates a new user object

        Args:
            id_ (str): The Azure ID given to a user
            email (str): The user's email address
            upn (str): The user's UPN
        """
        self.id = id_
        self.email = email
        self.upn = upn

    @property
    def username(self) -> str:
        """The user's username. Derived from the UPN.

        Returns:
            str: username
        """
        return self.upn.split("@")[0]

    def get_userinfo(self) -> Dict[str, str]:
        """Collects the user's info into a dictionary

        Returns:
            Dict[str, str]: Dict containing the user's id, email, username, and upn.
        """
        userinfo = {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "upn": self.upn,
        }
        return userinfo


def has_priv(priv_code: str, regex: bool = False) -> bool:
    """Checks to see if the user has the desired priv code or matches the priv code regex if `regex` is `True`
    Returns `False` if there is no user logged in

    Args:
        priv_code (_type_): the priv code to check against
        regex (bool, optional): indcates whether the provided priv_code should be processed as a regex pattern. Defaults to False.

    Returns:
        bool: Returns `True` if the user has the priv code, `False` otherwise or if there is no user
    """

    # Check to see if there is a logged in user
    if not current_user.is_authenticated:
        return False

    # Select which function to call based on regex parameter
    func = check_priv_regex if regex else check_priv
    return func(current_user.username, priv_code)


def init_login(app: Flask) -> LoginManager:
    """Initalizes the LoginManager for the app

    Args:
        app (Flask): the flask app

    Returns:
        LoginManager: the initalized LoginManager
    """
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "oauth.login"
    login_manager.USE_SESSION_FOR_NEXT = True
    login_manager.SESSION_COOKIE_SECURE = True
    login_manager.REMEMBER_COOKIE_SECURE = True

    @login_manager.user_loader
    def load_user(user_id):
        app.logger.debug(f"load_user: {user_id}")

        user = User(
            id_=user_id,
            email=(session["user"]["email"] if session["user"].get("email") is not None else ""),
            upn=session["user"]["upn"],
        )

        impersonate_priv = app.config.get("IMPERSONATE_PRIV_CODE")

        if (
            impersonate_priv
            and request.cookies.get("REMOTE_USER_IMPERSONATE")
            and check_priv(user.username, impersonate_priv)
        ):
            fake_user = request.cookies["REMOTE_USER_IMPERSONATE"].lower()
            fake_email = f"{fake_user}@umsystem.edu"

            user = User(id_="FAKEUSER", email=fake_email, upn=fake_email)

        g.user = user.get_userinfo()

        return user

    return login_manager
