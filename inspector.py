#!/usr/bin/env python
#===============================================================================
# Inspector is a re-implementation Inspect-Shell. The author of the original
# project and the idea is Andrew Moffat.
# URL: https://github.com/amoffat/Inspect-Shell
# The license notice from Inspect-Shell:
# 
# Copyright (C) 2011 by Andrew Moffat
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#===============================================================================
# Inspector, a Python server and shell for inspecting Python processes
# Copyright (C) 2012  Jure Ziberna
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#===============================================================================


# meta stuff
import inspect
import atexit
# server and sockets
import socket
import threading
# compiler
import codeop
# output
import io
import sys
import contextlib
import traceback
# shell history
import os
try:
    import readline
except ImportError:
    readline = None
# command-line arguments
import argparse


__version__ = '0.2.1'
__copyright__ = """Copyright (C) 2011 by Andrew Moffat
Copyright (C) 2012  Jure Ziberna"""
__license__ = 'GNU GPL 3'


# Python 2 and 3 support and other hacks
PY3 = sys.version_info[0] == 3
if not PY3:
    input = raw_input
    io.StringIO = io.BytesIO
compile = codeop.compile_command


HOST = 'localhost'
PORT = 2971  # first 4-digit fibonacci prime number
TIMEOUT_SERVER = 30.0  # in seconds
TIMEOUT_CLIENT = 0.5  # in seconds
CHUNK_SIZE = 1024  # in bytes
PASSPHRASE = 'something dirty'

SHELL_HISTORY_FILE = '~/.inspector_history'

__RED__ = '\033[31m%s\033[0m'
__YELLOW__ = '\033[33m%s\033[0m'
__GREEN__ = '\033[32m%s\033[0m'
__SYMBOL__ = '#'

STATUS_WAITING = '%s Waiting for inspector' % (__YELLOW__ % __SYMBOL__)
STATUS_CONNECTED = '%s Inspector has connected' % (__GREEN__ % __SYMBOL__)
STATUS_DISCONNECTED = '%s Inspector has disconnected' % (__YELLOW__ % __SYMBOL__)
STATUS_RECEIVED = '%s Inspector\'s message received' % (__GREEN__ % __SYMBOL__)
STATUS_STOPPED = '%s Inspector stopped running' % (__YELLOW__ % __SYMBOL__)
STATUS_SHUTDOWN = '%s Inspector server has shutdown' % (__RED__ % __SYMBOL__)

VERBOSE = 0

def status(string, verbose=1):
    """
    Prints a status based on verbose level. Change from the inspector or importer:
    >>> inspector.VERBOSE = 2
    """
    if VERBOSE >= verbose:
        print(string)

PROMPT_INIT = '>>> '
PROMPT_MORE = '... '


class Socket(object):
    """
    Socket wrapper.
    """
    def __init__(self, timeout=0.5, chunk_size=1024, socket=None, passphrase=PASSPHRASE):
        self.timeout = timeout
        self.chunk_size = chunk_size
        if socket:
            self.socket = socket
        else:
            self.initialize()
        self.header_separator = PASSPHRASE
        self.header_format = '%d' + self.header_separator
    
    def __getattr__(self, attribute_name):
        return getattr(self.socket, attribute_name)
    
    def initialize(self):
        """
        Creates a new socket with reusable address, so that you can reuse the
        port immediately after, say, a crash.
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(self.timeout)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    def send(self, message):
        """
        Combines a header with a message. The header contains message length.
        """
        header = self.header_format % len(message)
        message = header + message
        self.socket.sendall(message.encode())
    
    def receive(self):
        """
        Receives a message. Parses the first chunk to get the message length.
        """
        message = self.socket.recv(self.chunk_size)
        length, message_chunk = self.parse_header(message)
        if not message_chunk:
            return None
        length = int(length)
        message = message_chunk
        while len(message) < length:
            message += self.socket.recv(self.chunk_size)
        return message.decode()
    
    def parse_header(self, header):
        """
        Parses the header (the first message chunk) for message length. Returns
        the length and the left-over message chunk.
        """
        header_separator = self.header_separator.encode()
        length, separator, message_chunk = header.partition(header_separator)
        return length, message_chunk


class ImporterServer(object):
    """
    A simple socket server which executes any message it receives in given
    namespace.
    """
    def __init__(self, address, namespace):
        self.address = address
        self.namespace = namespace
        self.running = False
    
    def start(self, *args, **kwargs):
        """
        Creates a socket and starts, binds an address to it, and enables the
        listen mode.
        """
        self.socket = Socket(*args, **kwargs)
        self.socket.bind(self.address)
        self.socket.listen(1)
    
    def run(self):
        """
        Runs a server in a separate thread.
        """
        thread = threading.Thread(target=self.serve)
        thread.daemon = True
        thread.start()
    
    def serve(self):
        """
        Serves back the messages to the inspector.
        """
        # initialize variables
        self.running = True
        client_socket = None
        status(STATUS_WAITING)
        # loop until shutdown
        while self.running:
            if not client_socket:
                client_socket = self.client_socket()
            try:
                code = client_socket.receive()
                if code == None:
                    client_socket = None
                    status(STATUS_DISCONNECTED)
                    continue
                status(STATUS_RECEIVED, 2)
                output = self.code_output(code)
                client_socket.send(output)
            except socket.error as socket_error:
                print(socket_error)
                break
        client_socket.close()
        status(STATUS_STOPPED)
    
    def client_socket(self):
        """
        Waits for a client (read: inspector) socket to connect. Returns a socket
        that is connected to the client.
        """
        sock = None
        while not sock:
            try:
                sock, address = self.socket.accept()
                sock = Socket(socket=sock)
                status(STATUS_CONNECTED)
            except socket.timeout:
                pass
        return sock
    
    def code_output(self, code):
        """
        Compiles and executes the received code and returns the output.
        """
        compiled = compile(code, '<inspector-server>', 'single')
        # execute the compiled message and capture the output
        with self.output() as output:
            try:
                exec(compiled, self.namespace, self.namespace)
            except:
                return traceback.format_exc(0)  # only first entry in the stack
        return output.getvalue()
    
    @contextlib.contextmanager
    def output(self, output=None):
        """
        Context manager that puts the given output into the standard output,
        yields the output, then puts the previous output back.
        """
        clipboard = sys.stdout
        if output is None:
            output = io.StringIO()
        sys.stdout = output
        yield output
        sys.stdout = clipboard
    
    def shutdown(self):
        """
        Shuts down the server (closes the server socket) and deletes namespace.
        """
        if self.running:
            self.running = False
            self.socket.close()
            del self.namespace
            status(STATUS_SHUTDOWN)


def inspector(host, port, timeout, passphrase):
    """
    Opens a socket for communicating with the importer from the
    shell side. Runs a shell after connection is established.
    """
    sock = Socket(timeout=timeout, passphrase=passphrase)
    try:
        sock.connect((host, port))
        # get the file name that runs the server
        sock.send("globals()['__file__']")
        importer_file = sock.receive().strip().strip("'")
        # display some information about the connection
        print("<Inspector @ %s:%d (%s)>" % (host, port, importer_file))
        shell_history()
        while True:
            # get input from user
            code = code_input()
            if code == 'exit':
                break
            # send the input and receive the output
            sock.send(code)
            output = sock.receive()
            # print if the input has executed
            if output:
                sys.stdout.write(output)
    except (EOFError, KeyboardInterrupt):
        print('')
    except (socket.error, socket.timeout) as error:
        print(error)
    finally:
        sock.close()


def importer_server():
    """
    Runs a server on the importer's side.
    """
    # this behaves strangely for me, so I'm checking the whole stack to make it work for everybody
    importer_globals = None
    for frame in inspect.stack():
        if frame[0].f_globals['__name__'] == '__main__':
            importer_globals = frame[0].f_globals
            break
    if not importer_globals:
        print('From where are you importing?')
        return
    # server variables
    host = importer_globals.get('INSPECTOR_HOST', HOST)
    port = importer_globals.get('INSPECTOR_PORT', PORT)
    timeout = importer_globals.get('INSPECTOR_TIMEOUT', TIMEOUT_SERVER)
    passphrase = importer_globals.get('INSPECTOR_PASSPHRASE', PASSPHRASE)
    # server initialization
    server = ImporterServer((host, port), importer_globals)
    # server start-up
    server.start(timeout=timeout, passphrase=passphrase)
    server.run()
    # reassure server shutdown at exit
    atexit.register(server.shutdown)


def code_input():
    """
    This runs on the inspector's (shell) side. The compiler is used to perform
    multiline code input.
    """
    code = ''
    compiled = None
    while not compiled:
        prompt = PROMPT_INIT if not code else PROMPT_MORE
        line = input(prompt)
        code += line
        try:
            compiled = compile(code, '<inspector-shell>', 'single')
        except (SyntaxError, OverflowError, ValueError):
            traceback.print_exc(0)  # only first entry in the stack
            code = ''
        else:
            code += '\n'
    return code


def shell_history():
    if not readline:
        return
    history_file = os.path.expanduser(SHELL_HISTORY_FILE)
    try:
        readline.read_history_file(history_file)
    except IOError:
        pass
    atexit.register(readline.write_history_file, history_file)


def parse_args():
    """
    Parses command-line arguments. Displays usage when -h option is given.
    """
    parser = argparse.ArgumentParser(description='Inspector')
    parser.add_argument('-l', metavar='host', default=HOST)
    parser.add_argument('-p', metavar='port', type=int, default=PORT)
    parser.add_argument('-t', metavar='timeout', type=int, default=TIMEOUT_CLIENT)
    parser.add_argument('-s', metavar='passphrase', default=PASSPHRASE)
    args = parser.parse_args()
    return args.l, args.p, args.t, args.s


if __name__ == '__main__':
    # from the inspector's side (client)
    inspector(*parse_args())
else:
    # from the importer's side (server)
    importer_server()

