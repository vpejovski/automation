#!/usr/bin/python
'''
Created on   : Jan 25, 2013
Last updated : Feb 13, 2014

@author: vpejovski

Script will check which version of kernel is currently running, store results
if not present or compare with previous version.

If newer kernel version is detected it will invoke vmware-tools-config.pl
to compile modules for current kernel and will start the vmwaretoold
process.
'''

import os
import subprocess


def write_kernel_version(kernel_version):
    """Writes current kernel version to filesystem."""

    status_file = open('/etc/vmware-tools/kernel_version', 'w')
    status_file.write(kernel_version)
    status_file.close()


def read_kernel_version():
    """Reads current kernel version to filesystem."""
    status_file = open('/etc/vmware-tools/kernel_version', 'r')
    current_version = status_file.readline().strip()
    status_file.close()
    return current_version


def tool_config_required():
    """
    Compares last know (saved) kernel version with the one running.
    If different it will write and re-configure vmware tools on the host.
    """
    kernel_version = os.uname()[2]

    if os.path.exists('/etc/vmware-tools/'):
        if os.path.exists('/etc/vmware-tools/kernel_version'):
            current_version = read_kernel_version()

            if kernel_version == current_version:
                return False
            else:
                write_kernel_version(kernel_version)
                return True
        else:
            write_kernel_version(kernel_version)
            return True

    return False


if __name__ == '__main__':

    if tool_config_required():
        subprocess.Popen(['/usr/bin/vmware-config-tools.pl', '-d']).wait()
