#!/usr/bin/env python

# Daemon component came from :
#http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/

"""
Provides a simple python daemon that will search for WebSphere processes
and kill them. Then restart the application.

Includes very basic web server that list all pids of running processes
and provides a button for restart.
"""

import sys
import os
import time
import atexit
from signal import SIGTERM, SIGKILL
import BaseHTTPServer
import SocketServer
import ConfigParser
import subprocess


class Daemon(object):
    """
    A generic daemon class.

    Usage: subclass the Daemon class and override the run() method
    """
    def __init__(self, pidfile, stdin='/dev/null',
                 stdout='/dev/null', stderr='/dev/null'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile

    def daemonize(self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        file(self.pidfile, 'w+').write("%s\n" % pid)

    def delpid(self):
        os.remove(self.pidfile)

    def start(self):
        """
        Start the daemon
        """

        # Check for a pidfile to see if the daemon already runs
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)

        # Start the daemon
        self.daemonize()
        self.run()

    def stop(self):
        """
        Stop the daemon
        """
        # Get the pid from the pidfile
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return  # not an error in a restart

        # Try killing the daemon process
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print str(err)
                sys.exit(1)

    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()

    def run(self):
        """
        You should override this method when you subclass Daemon.
        It will be called after the process has been daemonized
        by start() or restart().
        """


class ProcessServiceHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """Class that provides service management capabilities"""

    def do_GET(self):
        index_file = """<!DOCTYPE html>
        <head>
            <meta charset="utf-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
            <title>Hello Server!</title>
            <!-- Place favicon.ico and apple-touch-icon.png in the root directory -->
        </head>
        <body>
            <p>Search service restart</p>
            <form name="input" action="restart" method="post">
                <input type="submit" value="Restart service">
            </form>
            <p>%s</p>
        </body>
        </html>"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        # self.send_header('Content-Length', len('Hello World!\r\n'))
        self.end_headers()
        self.wfile.write(index_file % ' # '.join(self.get_pids()))

    def do_POST(self):
        if self.path == '/restart':
            my_pids = self.get_pids()

            for pid in my_pids:
                try:
                    while True:
                        os.kill(int(pid), SIGKILL)
                        time.sleep(0.1)
                except OSError, err:
                    err = str(err)
                    if not (err.find("No such process") > 0):
                        print str(err)

            subprocess.Popen(['/etc/init.d/wasd', 'start']).wait()

            index_file = """<!DOCTYPE html>
            <head>
                <meta charset="utf-8">
                <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
                <title>Restarting service</title>
                <!-- Place favicon.ico and apple-touch-icon.png in the root directory -->
            </head>
            <body>
                <p>Search service restart</p>
                <p>These pids were restarted: %s</p>
                <a href="/">Go back</a>
            </body>
            </html>"""
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            # self.send_header('Content-Length', len('Hello World!\r\n'))
            self.end_headers()
            self.wfile.write(index_file % ' # '.join(my_pids))

    def get_pids(self):
        pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
        search_app_pids = []

        for pid in pids:
            pid_file = open(os.path.join('/proc', pid, 'cmdline'), 'rb')
            cmdline = pid_file.read()
            pid_file.close()

            if cmdline.lower().startswith('/apps/websphere'):
                search_app_pids.append(pid)
                # print pid, cmdline
        return search_app_pids


class SearchRestarter(Daemon):
    """Class to provide service restarting"""

    def run(self):
        os.chdir(self.config.get_working_dir())

        while True:
            httpd = SocketServer.TCPServer(("", self.config.get_port()), ProcessServiceHandler)

            print "serving at port", self.config.get_port()
            httpd.serve_forever()

    def set_configuration(self, config):
        """Load a configuration from filesystem."""
        self.config = config


class RestarterConfig(object):
    """Class that contains Restarter configuration"""

    def __init__(self, path=None):
        self.config = ConfigParser.ConfigParser()
        file_name = 'restarter.conf'

        if path is not None:
            file_name = path + '/restarter.conf'

        self.config.read(file_name)
        # print self.config.sections()

    def get_working_dir(self):
        return self.config.get('configuration', 'working_dir')

    def get_log_dir(self):
        return self.config.get('configuration', 'log_dir')

    def get_port(self):
        return self.config.getint('configuration', 'port')


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "usage ./daemon start|stop|restart"
        sys.exit(2)

    # print sys.argv

    my_config = RestarterConfig(os.getcwd())
    # print my_config.get_working_dir()

    my_server = SearchRestarter(my_config.get_working_dir() +
                                '/daemon.pid', stdout=my_config.get_log_dir() +
                                '/out', stderr=my_config.get_log_dir() +
                                '/err')
    my_server.set_configuration(my_config)

    if sys.argv[1].lower().strip() == 'start':
        my_server.start()
    elif sys.argv[1].lower().strip() == 'stop':
        my_server.stop()
    elif sys.argv[1].lower().strip() == 'restart':
        my_server.stop()
        my_server.start()
