#!/usr/bin/python
'''
Created on Jan 25, 2013

@author: vpejovski

Script will check which version of kernel is currently running, store results
if not present or compare with previous version.

If newer kernel version is detected it will invoke vmware-tools-config.pl
to compile modules for current kernel and will start the vmwaretoold
process.
'''
import os
import subprocess


def tool_config_required():
    kernel_version = os.uname()[2]

    if os.path.exists('/etc/vmware-tools/'):
        if os.path.exists('/etc/vmware-tools/kernel_version'):
            current_version = ''
            with open('/etc/vmware-tools/kernel_version', 'r') as status_file:
                current_version = status_file.readline().strip()

            if kernel_version == current_version:
                return False
            else:
                with open('/etc/vmware-tools/kernel_version', 'w') as status_file:
                    status_file.write(kernel_version)
                return True
        else:
            with open('/etc/vmware-tools/kernel_version', 'w') as status_file:
                status_file.write(kernel_version)
                return True

    return False


if __name__ == '__main__':

    if tool_config_required():
        subprocess.Popen(['/usr/bin/vmware-config-tools.pl', '-d']).wait()
