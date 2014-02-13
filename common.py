"""
Common Fabric functions shared by other modules.
"""
from fabric.api import *
from fabric.colors import *
import datetime
import httplib2


def disable_output():
    """
    Disables all output from fabric or remote machine,
    it will display only print commands.
    """
    output['stdout'] = False
    output['running'] = False
    output['status'] = False
    output['warnings'] = False
    output['user'] = False
    output['stderr'] = False


@task()
def check_time():
    '''Check current date and time and if ntpd is running'''
    disable_output()
    date_string = run('date')
    ntp_status = sudo('service ntpd status')
    print("%s : %s" % (date_string, ntp_status))


@task()
def check_linux_version():
    '''Check linux patch level.'''
    disable_output()
    out = sudo('cat /etc/redhat-release')
    print '%s: %s' % (env.host, out)


@task()
def check_ports(host, port):
    '''Uploads port checking script and checks if the ports are open.'''
    disable_output()
    put('PortTester.py',
        '/tmp/PortTester.py',
        use_sudo=True,
        mode=0755)
    out = sudo('/usr/bin/python /tmp/PortTester.py %s %s' % (host, port))
    if 'not open!' in out:
        print red('%s: Port %s to host %s is not open.' % (env.host, port, host))
    else:
        print green('%s: Port %s to host %s is open.' % (env.host, port, host))


@task()
def change_user_password(username=None, password='Edison123'):
    """
    Change password for a user
    """
    if username is None:
        print "Please enter a valid username."
        return

    sudo("echo -e '" + password + "\n" + password + "'| passwd " + username)


@task()
def check_mem():
    """
    Displays memory amount and number of cores.
    """
    disable_output()
    memory = sudo('cat /proc/meminfo | grep -i MemTotal')
    cpus = sudo('cat /proc/cpuinfo | grep -i processor')
    memory = memory.replace('MemTotal:', '').replace('kB', '').strip()
    cpus = cpus.replace('\n', ',').split(',')
    print env.host, ":"
    print 'Total Memory: ' + str(int(memory) / (1024 * 1024)) + 'GB'
    print 'Total (v)Cores: ', len(cpus), '\n'


@task()
def check_limits():
    '''Checks the limits file.'''
    disable_output()

    # 131070 - file hash for this number of files
    hash_131070 = '18f0b5ce2fc171e55a390b38c16ecc76'
    hash_1019999 = 'e34b41b02c16c320cf1a9f301e23181b'

    # this is a value that comes with plain install
    hash_default = '667a77a9a360468f97d30f97eb775e47'
    out = run('md5sum /etc/security/limits.conf')
    # print out.split(' ')[0]
    if hash_default == out.split(' ')[0]:
        print env.host, blue('Unchanged limits file.')

    elif hash_131070 == out.split(' ')[0]:
        print env.host, blue('Limits file with 131070.')

    elif hash_1019999 == out.split(' ')[0]:
        print env.host, blue('Limits file with 1019999.')

    else:
        print env.host, red('Wrong hash!')

    print run('ls -l /etc/security/limits.conf')


@task()
def fix_limits_permissions():
    '''
    Fixes permissions on limits.conf file
    Incorrect permissions stopped creating new shell process.
    '''
    sudo('chmod 644 /etc/security/limits.conf')
    sudo('chown root:root /etc/security/limits.conf')
    run('ls -l /etc/security/limits.conf')


@task()
def upload_limits():
    """
    Uploads modified limits.conf file from local system.
    """
    put('security/limits.conf', '~/limits.conf', mode=0644)
    sudo('mv /etc/security/limits.conf /etc/security/limits.conf.old')
    cwd = run('pwd')
    sudo('mv ' + cwd + '/limits.conf /etc/security/limits.conf')
    sudo('chmod 644 /etc/security/limits.conf')
    sudo('chown root:root /etc/security/limits.conf')


@task()
def poweroff():
    """
    Multi host poweroff
    """
    sudo('poweroff')


@task()
def reboot_host():
    """
    Multi host reboot
    """
    sudo('reboot')


def create_sudoers_line(sysadmin_line, name):
    '''This function will create a add users to
       SYSADMIN user alias in sudoers file.'''
    sudoers_array = sysadmin_line.split('=')
    users_array = []

    # Append supplied user and then append rest of them
    users_array.append(name)
    users_array.append(sudoers_array[1])

    #Replace existing with new + old
    sudoers_array[1] = ','.join(users_array)
    # Apparently sed needs 4 \\\\ to interpret it correctly
    # http://stackoverflow.com/questions/1269788/help-with-sed-syntax-unterminated-s-command
    result = '='.join(sudoers_array).replace('\\', '\\\\\\\\')
    return result


@task()
def check_sudo(name=None):
    """
    Checks to see if user is already added to sudoers file.
    """
    disable_output()
    if name is None:
        return

    #command = r"grep -i '^User_Alias SYSADMIN=' /etc/sudoers | grep -i " + name
    command = r"grep -i '^User_Alias SYSADMIN=' /etc/sudoers"

    if env.user == 'root':
        out = run(command)
    else:
        out = sudo(command)

    if out.succeeded and (name in out):
        print(green(r'User {0} has sudo on {1}.'.format(
                                                        name.strip(),
                                                        env.host)
                                                        ))
    else:
        print(red(r'User {0} has no sudo on {1}.'.format(
                                                         name.strip(),
                                                         env.host)
                                                         ))


@task()
def check_user(name=None, sudo_check='Y'):
    """Check if user is added to the system and if it has sudo rights"""
    disable_output()
    if name is None:
        return

    out = run(r"grep -i '^{0}' /etc/passwd".format(name.strip()), warn_only=True, quiet=True)

    if out.succeeded:
        print(green(r"User {0} is added to {1}. [{2}]".format(name.strip(), env.host, out)))
    else:
        print(red("User {0} is not added to {1}.".format(name.strip(), env.host)))

    if sudo_check.strip().lower() == 'y':
        check_sudo(name=name)


@task()
def sudo_add(names=None):
    """
    Adds users to sudoers list. names parameter needs to be
    in form user1,user2,user3
    """
    name = names.replace('|', ',')

    if name is None:
        print "Please enter name."
        return

    command = r"grep -i '^User_Alias SYSADMIN=' /etc/sudoers"

    if env.user == 'root':
        out = run(command)
    else:
        out = sudo(command)

    result = create_sudoers_line(out, name)

    run("cp /etc/sudoers /etc/sudoers.bak")
    run("sed 's|User_Alias SYSADMIN=.*|%s|' </etc/sudoers.bak >/etc/sudoers" % result)


@task()
def user_mod(name=None, group=None):
    """
    Adds a user to a group; need to specify username and group name
    """
    if name is None:
        print "please enter name."
        return
    if group is None:
        print "please enter group name. "
        return
    run('usermod -G' + group + " " + name)


@task
def portal_iim_checkversion():
    '''Checks for what version of the IBM Installation Manager the server is running'''
    sudo('/apps/InstallationManager/eclipse/tools/imcl -version')


@task
def mountshare():
    '''Mounts our share'''
    out = run('ls -a /apps/tmp')
    if not ('portal' in out):
        sudo('mkdir -p /apps/tmp/')
        sudo('mount -t nfs nfshost.domain.com:/apps/nfs_export /apps/tmp')


@task
def unmount_share():
    '''Unmounts share'''
    sudo('umount /apps/tmp')


@task
def getdatetime_microseconds():
    '''it returns the date time with microseconds in a string format'''

    today = datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d%H%M%S%f')
    return today


@task
def getdate():
    '''Returns date'''
    today = datetime.datetime.strftime(datetime.datetime.now(), '%m%d%Y')
    return today


@task
def sublime_deploy():
    '''
    This deploys the sublime text editor and creates a desktop icon for it.
    Applies to Fedora only, not sure RedHat
    '''
    local('tar xvfz Sublime.2.0.1.tar.bz2 /apps/Sublime/')
    local('cp sublime.desktop /usr/share/applications/')


@task
def install_telnet():
    """Installs telnet"""
    sudo('yum -q -y install telnet')

@task
def install_x():
    """
    Installs x
    """
    sudo('yum -q -y groupinstall "X Window System"')
    sudo('yum -q -y install firefox')

@task
def install_libxp():
    '''
    Required for WebSEAL and other authentication components.
    Maybe only 32 bit required.
    Also required for WESB. in addition to X packages.
    '''
    sudo('yum -q -y install libXp')
    sudo('yum -q -y install libXp.i686')
    sudo('yum -q -y install gtk2.i686 libXtst.i686 gtk2-engines.i686 \
                            libcanberra-gtk2.i686 PackageKit-gtk-module.i686')
    sudo('yum -q -y install gdb.x86_64')


@task
def install_screen():
    '''Installs Screen'''
    sudo('yum -q -y install screen')


@task()
def restarter_install():
    """small daemon that helps restart search servers in prod."""
    sudo('mkdir -p /opt/restarter')
    sudo('mkdir -p /opt/restarter/log')

    put('restarter/daemon.py', '/tmp/', mode=0755)
    sudo('mv /tmp/daemon.py /opt/restarter/')
    put('restarter/restarter.conf', '/tmp/', mode=0644)
    sudo('mv /tmp/restarter.conf /opt/restarter/')

    sudo('chown -R root:staff /opt/restarter')

    with cd('/opt/restarter'):
        sudo('python daemon.py start')

@task()
def restarter_update():
    """small daemon that helps restart search servers in prod."""

    with cd('/opt/restarter'):
        sudo('python daemon.py stop')

    put('restarter/daemon.py', '/tmp/', mode=0755)
    sudo('mv /tmp/daemon.py /opt/restarter/')
    put('restarter/restarter.conf', '/tmp/', mode=0644)
    sudo('mv /tmp/restarter.conf /opt/restarter/')

    sudo('chown -R root:staff /opt/restarter')

    with cd('/opt/restarter'):
        sudo('python daemon.py start')

@task
def set_nonexpire_user(username=None):
    '''
    Set a linux user to not expire
    '''
    if username == "None":
        print('pls enter a valid user name')
        return

    sudo('chage -M 99999 ' + username)

@task()
def resize_tmp_fs():
    """
    Increase the size of tmp logical volume and filesystem.
    """
    sudo('lvextend -r -L+1G /dev/mapper/rootvg-tmplv')

@task()
def check_dns_setup():
    '''Check if correct DNS parameters are set.'''
    disable_output()

    hosts_file = sudo('cat /etc/hosts')

    if 'wrong.domain.' in hosts_file.lower():
        print red('Host {0} : wrong.domain. found in host file.'.format(env.host))

    network_file = sudo('cat /etc/sysconfig/network')

    if 'peerdns=no' in network_file.lower():
        print red('Host {0} : peerdns is no in /etc/sysconfig/network'.format(env.host))

    iface_name = sudo("ip addr | grep -i '192.168' | cut -d' ' -f11")
    iface_file = sudo('cat /etc/sysconfig/network-scripts/ifcfg-{0}'.format(iface_name))

    if 'dns' not in iface_file.lower():
        print red('Host {0} : DNS is not configured in /etc/sysconfig/network-scripts/ifcfg-{1}'.format(env.host, iface_name))

    ping_out = sudo('ping www.google.com -c 1 -W 2', warn_only=True, quiet=True)
    if 'unknown host' in ping_out.lower():
        print red('Host {0} : DNS problem detected.'.format(env.host))

@task()
def fix_dns_setup():
    '''
    Update DNS configuration on linux hosts.
    '''
    put('dns/dns_update.py', '/tmp/dns_update.py', use_sudo=True, mode=0700)

    sudo('/tmp/dns_update.py')
    sudo('service NetworkManager restart')
    sudo('rm -f /tmp/dns_update.py')

@task()
def upload_sudoers_checker():
    """
    Uploads suders script and creates cron entry under root.
    """
    put('tools/make_sudo_work.py', '/usr/local/bin/', use_sudo=True, mode=0555)
    sudo('echo "*/15 * * * * /usr/local/bin/make_sudo_work.py >/dev/null 2>&1" > /var/spool/cron/root')
    sudo('chmod 0600 /var/spool/cron/root')
