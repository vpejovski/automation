#!/usr/bin/env python

import sys
import os
import datetime
import shutil
import subprocess

# Test files

HOSTS = '/etc/hosts'
NETWORK='/etc/sysconfig/network'
IFACE='/etc/sysconfig/network-scripts/ifcfg-{0}'

def get_interface_name():
    return subprocess.Popen(["/sbin/ip addr | grep -i '192.168' | cut -d' ' -f11"],shell=True, stdout=subprocess.PIPE).communicate()[0].strip()

def update_hosts_file():
    with open(HOSTS) as hosts_template:
        hosts_file = hosts_template.read()

    if 'wrong.domain.' in hosts_file:
        hosts_file_new = hosts_file.replace('.wrong.domain.com','.domain.com')
        print hosts_file
        print '---'
        print hosts_file_new
        update_config_files(HOSTS, hosts_file_new)



def update_network_file():
    with open(NETWORK) as network_template:
        network_file = network_template.read()

    if 'peerdns=no' in network_file.lower():
        network_file_new = network_file.replace('PEERDNS=no','PEERDNS=yes')
        print network_file
        print '---'
        print network_file_new
        update_config_files(NETWORK, network_file_new)

def update_iface_file():
    iface_name = get_interface_name()
    with open(IFACE.format(iface_name)) as iface_template:
        iface_file = iface_template.read()

    if 'dns' not in iface_file.lower():
        iface_file_new = iface_file + 'DNS1="8.8.8.8"\nDNS2="8.8.4.4"\nDOMAIN=domain.com\nSEARCH=domain.com\n'
        print iface_file
        print '---'
        print iface_file_new
        update_config_files(IFACE.format(iface_name), iface_file_new)

def update_config_files(file_name, file_content, path='/root/'):
    '''Update configuration files'''

    file_name_suffix = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    shutil.copyfile(file_name, '{0}{1}.{2}'.format(path, file_name, file_name_suffix))

    with open(file_name, 'wb') as configuration_file:
        configuration_file.write(file_content)

def main():
    update_hosts_file()
    update_network_file()
    update_iface_file()

if __name__ == '__main__':
    main()