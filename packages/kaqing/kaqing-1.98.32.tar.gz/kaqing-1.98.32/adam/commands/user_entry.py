from functools import partial
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import re
import subprocess
import time
import psutil
import signal
import threading
import traceback

from adam.commands.frontend.code_utils import get_available_port
from adam.config import Config
from adam.sso.idp import Idp
from adam.app_session import AppSession, IdpLogin
from adam.apps import Apps
from adam.commands.command import Command
from adam.repl_state import ReplState
from adam.utils import log2

class TokenHandler(BaseHTTPRequestHandler):
    def __init__(self, user: str, idp_token: str, *args, **kwargs):
        self.user = user
        self.idp_token = idp_token
        super().__init__(*args, **kwargs)

    def log_request(self, code='-', size='-'):
        pass

    def do_GET(self):
        Config().debug(f'Token request from cient: {self.client_address}\r')
        ports = self.get_ports()
        Config().debug(f'ports: {ports}\r')
        if os.getenv('CHECK_CLIENT_PORT', 'true').lower() != 'true' or self.client_address[1] in ports:
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(self.idp_token.encode('utf8'))
        else:
            # TODO cannot get the ports as we get permission denined on Docker
            # for debugging
            # time.sleep(120)
            self.send_response(403)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f'Port: {self.client_address[1]} has not been opened by you.\n'.encode('utf8'))

    def get_ports(self):
        ports = []

        # curl       627299            sahn    5u  IPv4 542049941      0t0  TCP localhost:39524->localhost:8001 (ESTABLISHED)
        command = ['bash', '-c', f"lsof -i -P 2> /dev/null | grep {self.user} | grep localhost" + " | awk '{print $9}'"]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        for line in result.stdout.split('\n'):
            groups = re.match(r'localhost:(.*?)->localhost:(.*)$', line)
            if groups:
                ports.append(int(groups[1]))

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

    def run_token_server(port: int, user: str, idp_token: str):
        server_address = ('localhost', port)
        handler = partial(TokenHandler, user, idp_token)
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

        server_port = get_available_port()
        server_thread = threading.Thread(target=UserEntry.run_token_server, args=(server_port, login.shell_user(), login.ser()), daemon=True)
        server_thread.start()

        sh = f'{os.getcwd()}/login.sh'
        if not os.path.exists(sh):
            sh = f'{os.getcwd()}/docker/login.sh'

        if os.getenv('PASS_DOWN_IDP_TOKEN', "false").lower() == "true":
            os.system(f'{sh} {login.shell_user()} {server_port} {login.ser()}')
        else:
            os.system(f'{sh} {login.shell_user()} {server_port}')

        return state

    def completion(self, _: ReplState):
        return {}

    def help(self, _: ReplState):
        return f'{UserEntry.COMMAND}\t ttyd user entry'