from functools import partial
import http
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import signal
import threading
import traceback

from adam.config import Config
from adam.sso.idp import Idp
from adam.app_session import AppSession, IdpLogin
from adam.apps import Apps
from adam.commands.command import Command
from adam.repl_state import ReplState
from adam.utils import log2

class TokenHandler(BaseHTTPRequestHandler):
    def __init__(self, idp_token: str, *args, **kwargs):
        self.idp_token = idp_token
        super().__init__(*args, **kwargs)

    def log_request(self, code='-', size='-'):
        pass

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(self.idp_token.encode('utf8'))

class UserEntry(Command):
    COMMAND = 'entry'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(UserEntry, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return UserEntry.COMMAND

    def run_token_server(port: int, idp_token: str):
        server_address = ('localhost', port)
        handler = partial(TokenHandler, idp_token)
        httpd = HTTPServer(server_address, handler)
        print(f"Serving on port {port}")
        httpd.serve_forever()

    def run(self, cmd: str, state: ReplState):
        def custom_handler(signum, frame):
            AppSession.ctrl_c_entered = True

        signal.signal(signal.SIGINT, custom_handler)

        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        state, args = self.apply_state(args, state)
        args, debug = Command.extract_options(args, 'd')
        if debug:
            Config().set('debug.show-out', True)

        username: str = None
        if len(args) > 0:
            username = args[0]

        login: IdpLogin = None
        while not login:
            try:
                if not(host := Apps.app_host('c3', 'c3', state.namespace)):
                    log2('Cannot locate ingress for app.')
                    username = None
                    continue

                if not (login := Idp.login(host, username=username, use_token_from_env=False)):
                    log2('Invalid username/password. Please try again.')
                    username = None
            except Exception as e:
                log2(e)

                Config().debug(traceback.format_exc())

        server_port = 8000
        server_thread = threading.Thread(target=UserEntry.run_token_server, args=(server_port, login.ser()), daemon=True)
        server_thread.start()

        sh = f'{os.getcwd()}/login.sh'
        if not os.path.exists(sh):
            sh = f'{os.getcwd()}/docker/login.sh'

        if os.getenv('PASS_DOWN_IDP_TOKEN', "true").lower() == "true":
            os.system(f'{sh} {login.shell_user()} {server_port} {login.ser()}')
        else:
            os.system(f'{sh} {login.shell_user()} {server_port}')

        return state

    def completion(self, _: ReplState):
        return {}

    def help(self, _: ReplState):
        return f'{UserEntry.COMMAND}\t ttyd user entry'