import socket
import threading
from urllib.parse import urlparse

from flask import Flask, render_template_string, request
from flask_wtf.csrf import CSRFProtect
from werkzeug.serving import make_server
from werkzeug.utils import redirect

from ..exceptions import AuthenticationError
from ._logger import logger

ERROR_PAGE = "<!DOCTYPE html><html><head><meta charset=\"utf-8\"/><title>Login failed</title><style>body{font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;}</style></head><body><h3>Authentication failed</h3><p>$error: $error_description. ($error_uri)</p></body></html>"
SUCCESS_PAGE = "<!DOCTYPE html><html><head><meta charset=\"utf-8\" /><title>Login successfully</title><style>body{font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;}</style></head><body><h3>You successfully have logged in!</h3><p>You can now close this window.</p></body></html>"


class ServerThread(threading.Thread):
    def __init__(self, app, port):
        threading.Thread.__init__(self)
        self.srv = make_server("127.0.0.1", port, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        self.srv.serve_forever()

    def shutdown(self):
        self.srv.shutdown()


class LoopbackClient:
    def __init__(self, redirect_uri: str):
        self.redirect_uri = redirect_uri
        parsed_uri = urlparse(redirect_uri)
        self.port = parsed_uri.port if parsed_uri.port else 80

    @staticmethod
    def initialize(redirect_uri: str):
        loopback_client = LoopbackClient(redirect_uri)
        is_port_available = loopback_client.is_port_available()
        if is_port_available:
            return loopback_client
        else:
            msg = f"Unable to initialize localhost loopback client, the redirect_uri port {loopback_client.port} already in use."
            logger.error(msg)
            raise AuthenticationError(msg)

    def listen_for_auth_code(self):
        app = Flask(__name__)
        csrf = CSRFProtect()
        csrf.init_app(app)
        auth_code_event = threading.Event()
        auth_code_container = {}

        @app.route("/")
        def root():
            if not request.url:
                logger.error("Loopback server callback was invoked without a url.")
                # return Login failed page
                return render_template_string(ERROR_PAGE)
            elif request.query_string == b"":
                # return login success page
                auth_code_event.set()
                return render_template_string(SUCCESS_PAGE)

            code = request.args.get("code")
            if code:
                logger.info("Authorisation code extracted from url. Redirecting to root of redirect uri.")
            auth_code_container["auth_code"] = code
            return redirect(self.redirect_uri)

        # Start Flask app in a separate thread
        server = ServerThread(app, self.port)
        server.start()

        # Wait for the auth code to be set
        auth_code_event.wait(timeout=180)
        # Stop the Flask app
        server.shutdown()

        # Wait for the Flask thread to finish
        server.join()

        # get the auth code received from the route
        auth_code = auth_code_container.get("auth_code")
        if not auth_code:
            msg = "Timed out waiting for auth code listener to be registered."
            logger.error(msg)
            raise AuthenticationError(msg)

        return auth_code

    def is_port_available(self) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", self.port))
                return True  # Port is not in use
            except OSError:
                return False  # Port is in use
