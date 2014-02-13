from fabric.api import *
from fabric.colors import *
import common

@task()
def check_vmware_tools():
    '''
    Check if the vmware tools are installed and running.
    '''
    common.disable_output()
    result = run('ps aux | grep -i vmtoolsd')
    if '/usr/sbin/vmtoolsd' in result:
        out = run('/usr/sbin/vmtoolsd -v')
        print env.host, green(' - VMWare tools running. ({0})'.format(out))
    else:
        print env.host, red(' - VMWare tools NOT running.')

@task()
def update_vmware_tools():
    """Install new version of VMWare tools."""
    put('/home/user/VMwareTools-9.0.0-782409.tar.gz',
        '/tmp/VMwareTools-9.0.0-782409.tar.gz',
        use_sudo=True,
        mode=0755)
    with cd('/tmp/'):
        sudo('tar xf /tmp/VMwareTools-9.0.0-782409.tar.gz')

    with cd('/tmp/vmware-tools-distrib'):
        sudo('./vmware-install.pl -d')

    with cd('/tmp/'):
        sudo('rm -rf VMwareTools-9.0.0-782409.tar.gz')
        sudo('rm -rf /tmp/vmware-tools-distrib')

@task()
def install_vmware_script():
    '''Installs vmware tools check script'''
    put('tools/vmware_tools_check.py',
    '/usr/bin/vmware_tools_check.py',
    use_sudo=True,
    mode=0755)
    sudo('echo "/usr/bin/vmware_tools_check.py" >> /etc/rc.local')
    sudo('/usr/bin/vmware_tools_check.py')

@task()
def update_vmware_script():
    '''uploads new copy of vmware tools check script'''
    put('tools/vmware_tools_check.py',
    '/usr/bin/vmware_tools_check.py',
    use_sudo=True,
    mode=0755)

@task()
def check_vmware_script():
    '''checks if the latest version is running'''
    # disable_output()
    version_match = False
    auto_start = False
    script_exists = False

    local_copy = local('md5sum tools/vmware_tools_check.py', capture=True).split(' ')[0].strip()
    out = sudo('md5sum /usr/bin/vmware_tools_check.py')

    if out.succeeded:
        script_exists = True
        remote_copy = out.split(' ')[0].strip()

        if local_copy == remote_copy:
            version_match = True

    out = sudo('cat /etc/rc.local')
    if ('/opt/ops/support/vmtool_upd' in out) or ('/usr/bin/vmware_tools_check.py' in out):
        auto_start = True

    if version_match and auto_start:
        print(env.host + green(' - Running latest version with autostart.'))

    elif version_match and not auto_start:
        print(env.host + magenta(' - Running latest version with no autostart.'))

    elif not version_match and not auto_start:
        if script_exists:
            print(env.host + red(' - Running old version with no autostart.'))
        else:
            print(env.host + red(' - No script or autostart info found.'))

    elif not version_match and auto_start:
        if script_exists:
            print(env.host + red(' - Autostart is present but script is old.'))
        else:
            print(env.host + red(' - Autostart is present but script is not.'))