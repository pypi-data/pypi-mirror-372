from functools import partial
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import psutil
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
        print('cient', self.client_address)
        print('ports', TokenHandler.get_ports())
        if self.client_address[1] in TokenHandler.get_ports():
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(self.idp_token.encode('utf8'))
        else:
            self.send_response(403)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f'Port: {self.client_address[1]} has not been opened by the process.'.encode('utf8'))

    def get_ports():
        ports = []

        for p in TokenHandler.get_all_child_processes():
            print('SEAN', p.pid)
            ports.extend(TokenHandler.get_open_ports_by_pid(p.pid))

        return ports

    def get_all_child_processes(parent_pid:int=None) -> list:
        """
        Retrieves all child processes of a given parent PID.
        If parent_pid is None, it gets children of the current process.
        """
        if parent_pid is None:
            parent_pid = os.getpid() # Get PID of the current Python script

        try:
            parent_process = psutil.Process(parent_pid)
            # children(recursive=True) gets all descendants, not just direct children
            children = parent_process.children(recursive=True)
            return children
        except psutil.NoSuchProcess:
            print(f"Process with PID {parent_pid} not found.")
            return []
        except psutil.AccessDenied:
            print(f"Access denied to process with PID {parent_pid}.")
            return []

    def get_open_ports_by_pid(pid):
        """
        Retrieves a list of open network ports associated with a given process ID.
        """
        try:
            process = psutil.Process(pid)
            connections = process.connections()
            open_ports = []
            for conn in connections:
                # Filter for listening or established connections on IPv4 or IPv6
                if conn.status in [psutil.CONN_LISTEN, psutil.CONN_ESTABLISHED]:
                    if conn.laddr and conn.laddr.port:
                        open_ports.append(conn.laddr.port)
            return list(set(open_ports)) # Return unique ports
        except psutil.NoSuchProcess:
            print(f"Error: No process found with PID {pid}")
            return []
        except psutil.AccessDenied:
            print(f"Error: Access denied to process with PID {pid}. Run as administrator/root.")
            return []

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