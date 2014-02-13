#!/usr/bin/env python
# encoding: utf-8
'''
PortTester -- testing open ports after AO was completed.
PortTester is a port testing tool.

@author:     vpejovski
@deffield    updated: 11/01/2012
'''

import sys
import os
import socket

# from optparse import OptionParser
#from argparse import ArgumentParser

__all__ = []
__version__ = 0.1
__date__ = '2012-11-01'
__updated__ = '2012-11-01'

DEBUG = 0
TESTRUN = 0
PROFILE = 0


def main(host, ports):
    '''Command line options.'''

    try:
        for port in ports.split(','):
            s = socket.socket()
            s.settimeout(2)
            s.connect((host, int(port)))

            print host, ':', port, "open!"
            s.close()

    except socket.error as msg:
        print host, ':', port, "not open!"
        s.close()

    except Exception as e:
        print e
        sys.exit(2)

if __name__ == "__main__":
    ports = sys.argv[2]
    host = sys.argv[1]
    sys.exit(main(host, ports))
