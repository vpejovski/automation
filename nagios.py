from fabric.api import *
from fabric.colors import *

CONFIG_LOCATION = 'nagios/'

# NOTE! you have to add config file to /etc/nagios/nagios.cfg
# You need to restore SELinux context of the new cfg files.

@task()
def update_ut():
    put(''.join([CONFIG_LOCATION, 'unit_test.cfg']), '/etc/nagios/objects/', use_sudo=True, mode=0664)

    # Restor SELinux context
    sudo('restorecon -Rv /etc/nagios/objects/')
    sudo('/etc/init.d/nagios restart')

@task()
def update_brkfx():
    put(''.join([CONFIG_LOCATION, 'break_fix.cfg']), '/etc/nagios/objects/', use_sudo=True, mode=0664)

    # Restor SELinux context
    sudo('restorecon -Rv /etc/nagios/objects/')
    sudo('/etc/init.d/nagios restart')

@task()
def update_int():
    put(''.join([CONFIG_LOCATION, 'integration.cfg']), '/etc/nagios/objects/', use_sudo=True, mode=0664)

    # Restor SELinux context
    sudo('restorecon -Rv /etc/nagios/objects/')
    sudo('/etc/init.d/nagios restart')

@task()
def update_sandbox():
    put(''.join([CONFIG_LOCATION, 'ibm_sandbox.cfg']), '/etc/nagios/objects/', use_sudo=True, mode=0664)

    # Restor SELinux context
    sudo('restorecon -Rv /etc/nagios/objects/')
    sudo('/etc/init.d/nagios restart')

@task()
def update_bizmodel():
    put(''.join([CONFIG_LOCATION, 'biz_mod.cfg']), '/etc/nagios/objects/', use_sudo=True, mode=0664)

    # Restor SELinux context
    sudo('restorecon -Rv /etc/nagios/objects/')
    sudo('/etc/init.d/nagios restart')

@task()
def update_misc():
    put(''.join([CONFIG_LOCATION, 'misc.cfg']), '/etc/nagios/objects/', use_sudo=True, mode=0664)

    # Restor SELinux context
    sudo('restorecon -Rv /etc/nagios/objects/')
    sudo('/etc/init.d/nagios restart')

@task()
def update_splunk():
    put(''.join([CONFIG_LOCATION, 'splunk.cfg']), '/etc/nagios/objects/', use_sudo=True, mode=0664)

    # Restor SELinux context
    sudo('restorecon -Rv /etc/nagios/objects/')
    sudo('/etc/init.d/nagios restart')


@task()
def update_training():
    put(''.join([CONFIG_LOCATION, 'training.cfg']), '/etc/nagios/objects/', use_sudo=True, mode=0664)

    # Restor SELinux context
    sudo('restorecon -Rv /etc/nagios/objects/')
    sudo('/etc/init.d/nagios restart')
