from __future__ import absolute_import
from __future__ import print_function

import dash
import flask

import os
from random import randint

import quartzbio

from .quartzbio_auth import QuartzBioAuth


class QuartzBioDash(dash.Dash):
    APP_URL = os.environ.get("APP_URL", "http://127.0.0.1:8050")
    QUARTZBIO_URL = os.environ.get("QUARTZBIO_URL", "http://my.quartzbio.com")
    SECRET_KEY = os.environ.get("SECRET_KEY", str(randint(0, 1000000)))

    def __init__(self, name, *args, **kwargs):
        # Default HTML page title
        self.title = kwargs.pop("title", name)

        app_url = kwargs.pop("app_url", self.APP_URL)
        quartzbio_url = kwargs.pop("quartzbio_url", self.QUARTZBIO_URL)

        # OAuth2 credentials
        client_id = kwargs.pop("client_id", os.environ.get("CLIENT_ID"))
        client_secret = kwargs.pop("client_secret", os.environ.get("CLIENT_SECRET"))
        grant_type = kwargs.pop("grant_type", None)
        salt = kwargs.pop("salt", None) or name

        server = flask.Flask(name)
        server.secret_key = kwargs.pop("secret_key", self.SECRET_KEY)
        kwargs["server"] = server

        super(QuartzBioDash, self).__init__(name, *args, **kwargs)

        if client_id:
            self.auth = QuartzBioAuth(
                self,
                app_url,
                client_id,
                salt=salt,
                client_secret=client_secret,
                grant_type=grant_type,
                quartzbio_url=quartzbio_url,
            )
        else:
            self.auth = None
            print(
                "WARNING: No QuartzBio client ID found. "
                "Your app (but not your data) will be publicly accessible."
            )

        @server.before_request
        def set_quartzbio_client():
            oauth_token = flask.request.cookies.get(QuartzBioAuth.TOKEN_COOKIE_NAME)
            if oauth_token:
                flask.g.client = quartzbio.QuartzBioClient(
                    token=oauth_token, token_type="Bearer"
                )
            else:
                # Use global credentials (if any)
                flask.g.client = quartzbio.QuartzBioClient()
