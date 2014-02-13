"""
Fabric script related to Splunk deployment.
"""

from fabric.api import *
from fabric.colors import *
import datetime
import common


@task
def check():
    """
    Checks if splunk has been installed and is running
    """
    common.disable_output()

    out = sudo('ls /apps/')

    if "splunkforwarder" in out:
        print(green(env.host + " Splunk is installed"))
    else:
        print(red(env.host + " Splunk is not installed"))

@task
def install(install_type=None, system_role=None, environment=None, db2_instance_name=None, sec=None):
    """
    Installs splunk
    type: Universal FOrwarder or Full (uf or f)
    system_role: Actual role of system (webseal,ldap...)
    environment=Envrionment. Production or test (p or s)
    db2_instance_name=Db2 instance name. This is used to build the inputs.conf for db2 systems
    sec=This is use to either use nfs mount or a put to get the splunk agent uploaaded to server. (n:means server can mount the nfs export, y:means server cant mount therefore use a put)
    """
    if install_type is None:
        print "Please enter a valid splunk software to upload, either F for full or UF for universal forwarder"
        return

    if install_type.lower() == "uf":
        install_fwd(system_role.lower(), environment.lower(), db2_instance_name, sec)

    elif install_type.lower() == "f":
        install_full()


def install_fwd(system=None, strenv=None, db2instname=None, sec=None):
    """
    Install splunk forwarder.
    """
    if system is None or env is None:
        print "Please supply system to monitor: ihs8,ihs7, ws7, ws8, tfim, ldap"
        return

    if strenv == 'p':
        list_of_indexers = ['SLSPINDEX01.domain.com:9997', 'SLSPINDEX02.domain.com:9997']
    elif strenv == 's':
        list_of_indexers = ['SLSSINDEX02.domain.com:9997', 'SLSSINDEX03.domain.com:9997']

    if sec == 'n':
        common.mountshare()
        sudo('rpm -i --prefix=/apps /apps/tmp/splunk/forwarder/x/splunkforwarder-6.0-182037-linux-2.6-x86_64.rpm')
    elif sec == 'y':
        put('splunk/splunkforwarder-6.0-182037-linux-2.6-x86_64.rpm', '/root/splunkforwarder-6.0-182037-linux-2.6-x86_64.rpm', use_sudo=True, mode=0755)
        sudo('rpm -i --prefix=/apps ~/splunkforwarder-6.0-182037-linux-2.6-x86_64.rpm')

    sudo('/apps/splunkforwarder/bin/splunk start --accept-license')
    sudo('/apps/splunkforwarder/bin/splunk enable boot-start')

    for indexer in list_of_indexers:
        sudo('/apps/splunkforwarder/bin/splunk add forward-server {0} -auth admin:changeme'.format(indexer))

    sudo('/apps/splunkforwarder/bin/splunk stop')
    sudo('mkdir /apps/splunkforwarder/etc/apps/search/local')

    source_path = '../fabric/'

    if system == "default":
        put(source_path + 'inputs.conf', '/apps/splunkforwarder/etc/apps/search/local/inputs.conf', use_sudo=True, mode=0644)

    elif system == "ldap":
        put(source_path + 'ldap.conf', '/apps/splunkforwarder/etc/apps/search/local/inputs.conf', use_sudo=True, mode=0644)

    elif system == "tfim":
        put(source_path + 'tfim.conf', '/apps/splunkforwarder/etc/apps/search/local/inputs.conf', use_sudo=True, mode=0644)

    elif system == "ihs8":
        put(source_path + 'ihs8.conf', '/apps/splunkforwarder/etc/apps/search/local/inputs.conf', use_sudo=True, mode=0644)

    elif system == "tameb":
        put(source_path + 'tameb.conf', '/apps/splunkforwarder/etc/apps/search/local/inputs.conf', use_sudo=True, mode=0644)

    elif system == "webseal":
        put(source_path + 'webseal.conf', '/apps/splunkforwarder/etc/apps/search/local/inputs.conf', use_sudo=True, mode=0644)

    elif system == "ws8":
        put(source_path + 'was.conf', '/apps/splunkforwarder/etc/apps/search/local/inputs.conf', use_sudo=True, mode=0644)

    elif system == "search":
        put(source_path + 'search.conf', '/apps/splunkforwarder/etc/apps/search/local/inputs.conf', use_sudo=True, mode=0644)

    elif system == "db2":
        db2inputs(db2instname)

    elif system == "wesb":
        put(source_path + 'wesb.conf', '/apps/splunkforwarder/etc/apps/search/local/inputs.conf', use_sudo=True, mode=0644)

    elif system == "syslog":
        put(source_path + 'syslog.conf', '/apps/splunkforwarder/etc/apps/search/local/inputs.conf', use_sudo=True, mode=0644)

    elif system == "commerce":
        put(source_path + 'commerce/inputs.conf', '/apps/splunkforwarder/etc/apps/search/local/inputs.conf', use_sudo=True, mode=0644)

    elif system == "search":
        put(source_path + 'search.conf', '/apps/splunkforwarder/etc/apps/search/local/inputs.conf', use_sudo=True, mode=0644)

    elif system == "nagios":
        put(source_path + 'nagios.conf', '/apps/splunkforwarder/etc/apps/search/local/inputs.conf', use_sudo=True, mode=0644)

    set_splunk_perms()
    sudo('/apps/splunkforwarder/bin/splunk start')
    remove_remote_file('~/splunkforwarder*')
    common.unmount_share()


@task
def db2inputs(db2instname):
    '''Creates the db2 inputs.conf file'''

    config_file_name = 'splunk/db2inputs.conf'
    config_file = open(config_file_name, 'w')
    config_file.write('[monitor:///db2/' + db2instname + '/sqllib/log]' + "\n")
    config_file.write('followTail = 0' + "\n")
    config_file.write('disabled = false' + "\n")
    config_file.write('sourcetype = DB2:ProjectName' + "\n")
    config_file.write('ignoreOlderThan = 2d' + "\n")
    config_file.write('' + "\n")
    config_file.write('[monitor:///db2/' + db2instname + '/sqllib/db2dump/*.log]' + "\n")
    config_file.write('followTail = 0' + "\n")
    config_file.write('disabled = false' + "\n")
    config_file.write('sourcetype = DB2:SUP' + "\n")
    config_file.write('ignoreOlderThan = 2d' + "\n")
    config_file.close()
    put(config_file_name, '/apps/splunkforwarder/etc/apps/search/local/inputs.conf', use_sudo=True, mode=0644)


@task
def set_splunk_perms():
    """Reset ownership and permissions for splunk installation."""
    sudo('chown -R splunk:splunk /apps/splunk*')
    sudo('chmod -R 777 /apps/splunk*')

def remove_remote_file(file_spec):
    """
    This will remove the specified file only if exists on remote system.
    """
    run('if [ -f ' + file_spec + ' ]; then rm -f ' + file_spec + '; fi')

def install_full():
    """
    Plain vanilla install for splunk
    """
    sudo('rpm -i --prefix=/apps splunk-5.0-140868-linux-2.6-x86_64.rpm')
    sudo('/apps/splunk/bin/splunk start --accept-license')
    sudo('/apps/splunk/bin/splunk enable boot-start')

@task
def restart(install_type=None):
    '''Restarts the splunk daemon'''

    if install_type.lower() == 'uf':
        splunk_path = '/apps/splunkforwarder/bin/'

    elif install_type.lower() == 'f':
        splunk_path = '/apps/splunk/bin/'

    sudo(splunk_path + 'splunk restart')

@task
def start(install_type):
    '''Starts splunk'''

    if install_type.lower() == 'f':
        sudo('/apps/splunk/bin/splunk start')

    elif install_type.lower() == 'uf':
        sudo('/apps/splunkforwarder/bin/splunk start')

@task
def stop(install_type):
    '''
    Starts splunk
    '''

    if install_type.lower() == 'f':
        sudo('/apps/splunk/bin/splunk stop')

    elif install_type.lower() == 'uf':
        sudo('/apps/splunkforwarder/bin/splunk stop')

@task
def setarchivethreshold():
    '''Sets up splunk to discard data olders than 30 days. Only for indexers'''

    remote_path = '/apps/splunk/etc/system/local/'
    source_filename = 'indexes.conf'
    put('splunk/' + source_filename, remote_path + source_filename, use_sudo=True, mode=0755)
    sudo('/apps/splunk/bin/splunk restart')

@task
def updateinputs(system_role=None):
    '''
    Updates WAS servers with new inputs.conf that has new sourcetypes
    '''

    if system_role == "None":
        print("Enter a valid system role")
        return

    remote_path = '/apps/splunkforwarder/etc/apps/'
    splunk_base = '../fabric/'
    source_file = ''

    if system_role == 'was':
        source_file = splunk_base + 'was.conf'

    elif system_role == 'tameb':
        source_file = splunk_base + 'tameb.conf'

    elif system_role == 'ihs8':
        source_file = splunk_base + 'ihs8.conf'

    elif system_role == 'web':
        source_file = splunk_base + 'webseal.conf'

    elif system_role == 'wesb':
        source_file = splunk_base + 'wesb.conf'

    elif system_role == 'ldap':
        source_file = splunk_base + 'ldap.conf'

    put(source_file, remote_path + 'search/local/inputs.conf', use_sudo=True, mode=0755)
    set_splunk_perms()
    restart('uf')

@task
def cleanup():
    """Remove inputs.conf file."""
    sudo('rm -f /apps/splunkforwarder/etc/apps/inputs.conf')


@task
def upgrade_uf(sec=None):
    '''
    Upgrades Universal Forwarder in  Linux Deployments
    '''
    # Make sure you are upgrading at least from 4.2 to 5.0. Versions before 4.2 do not support direct upgrade.
    splunk_package = 'splunkforwarder-6.0-182037-linux-2.6-x86_64.rpm'

    if sec == None:
        print("Please confirm that server can mount network share.")
        return

    #I'm adding the step below because I had some issues while upgrading splunk in some systems

    if sec == 'n':
        put('splunk/' + splunk_package, '/tmp/' + splunk_package, use_sudo=True, mode=0755)
        stop('uf')
        sudo('tar cvzf /apps/splunk-upgrade-backup.tar.gz /apps/splunkforwarder')
        sudo('rpm -U --prefix=/apps /tmp/' + splunk_package)
        sudo('/apps/splunkforwarder/bin/splunk start --accept-license --answer-yes')
        remove_remote_file('~/splunkforwarder*')

    elif sec == 'y':
        common.mountshare()
        stop('uf')
        sudo('rpm -U --prefix=/apps /apps/tmp/splunk/forwarder/x/' + splunk_package)
        sudo('/apps/splunkforwarder/bin/splunk start --accept-license --answer-yes')
        common.unmount_share()


@task
def upgrade_full():
    '''
    Upgrades Full Splunk in  Linux Deployments
    '''
    # Make sure you are upgrading at least from 4.2 to 5.0. Versions before 4.2 do not support direct upgrade.
    splunk_package = 'splunk-6.0-182037-linux-2.6-x86_64.rpm'

    #I'm adding the step below because I had some issues while upgrading splunk in some systems
    common.mountshare()
    stop('f')
    sudo('rpm -U --prefix=/apps /apps/tmp/splunk/full/x/' + splunk_package)
    sudo('/apps/splunk/bin/splunk start --accept-license --answer-yes')
    common.unmount_share()

@task
def move_olddispatchjobs():
    '''
    Moves around old dispatch jobs
    '''
    strcmd = '/apps/splunk/bin/splunk'
    out = sudo('ls -a /apps/splunk')
    if not ('old-dispatch-jobs' in out):
        sudo('mkdir /apps/splunk/old-dispatch-jobs')

    sudo(strcmd + ' cmd splunkd clean-dispatch /apps/splunk/old-dispatch-jobs/ -3d@d')

@task
def indexes_update():
    '''
    updates indexes.conf on splunk indexers
    '''
    put('splunk/indexes.conf', '/apps/splunk/etc/system/local/indexes.conf', use_sudo=True, mode=0755)
    set_splunk_perms()
    restart('f')

@task
def deploy_splunk_nix_addon():
    """
    Deploys splunk app for collecting machine stats like
    cpu, memory, disk usage...
    This is to be deploy on Universal forwarders only
    """
    put('nix_addon/Splunk_TA_nix-4.7.0-156739.tgz', '/tmp/Splunk_TA_nix-4.7.0-156739.tgz', use_sudo=True, mode=0755 )

    with cd('/apps/splunkforwarder/etc/apps/'):
        sudo('tar xf /tmp/Splunk_TA_nix-4.7.0-156739.tgz')

    with cd('/apps/splunkforwarder/etc/apps/Splunk_TA_nix/'):
        sudo('mkdir local')

    put('nix_addon/inputs.conf', '/apps/splunkforwarder/etc/apps/Splunk_TA_nix/local/inputs.conf', use_sudo=True, mode=0755 )

    set_splunk_perms()

    with cd('/apps/splunkforwarder/bin'):
        sudo('./splunk restart')

    sudo('rm -f /tmp/Splunk_TA_nix-4.7.0-156739.tgz')

@task
def deploy_filesystem_check():
    '''
    *nix systems only
    Depends on splunk nix add on, so make sure the add on has been deploy before
    It copies detec_ro_fs.py to destination server
    updates the inputs.conf for the nix add on
    restarts the universal forwarder
    '''
    stop('uf')
    put('tools/wrapper.sh', '/apps/splunkforwarder/etc/apps/Splunk_TA_nix/bin/wrapper.sh', use_sudo=True, mode=0755)
    put('tools/detect_ro_fs.py', '/apps/splunkforwarder/etc/apps/Splunk_TA_nix/bin/detect_ro_fs.py', use_sudo=True, mode=0755)
    put('nix_addon/inputs.conf', '/apps/splunkforwarder/etc/apps/Splunk_TA_nix/local/inputs.conf', use_sudo=True, mode=0755 )
    set_splunk_perms()
    start('uf')

@task
def deploy_unix_linux_app(sec=None):
    '''
    Deploys the full version app of the Unix linux app for Splunk.
    This app is meant to be deploy only on indexers, search head, and heavy forwarders not on universal forwarders
    '''
    if sec == None:
        print('Confirm if server can mount NFS export, if not then enter n')
        return

    if sec == 'n':
        put('splunk/splunk_app_for_nix-5.0.0-182057.zip', 'splunk_app_for_nix-5.0.0-182057.zip', use_sudo=True, mode=0755 )
        sudo('unzip splunk_app_for_nix.zip -d /apps/splunk/')
        restart('f')
        remove_remote_file('splunk_app_for_nix-5.0.0-182057.zip')

    elif sec == 'y':
        common.mountshare()
        sudo('unzip /apps/tmp/splunk/Apps/nix_apps/splunk_app_for_nix-5.0.0-182057.zip -d /apps/splunk/')
        restart('f')

@task
def deploy_unix_app():
    """
    deploys the Splunk Unix app to indexers
    Tool to collect stardard hotst metrics
    """
    local('tar cvfz unix.tar.gz unix/')
    put('unix.tar.gz', '/tmp/unix.tar.gz', use_sudo=True, mode=0755)
    stop('f')

    with cd('/apps/splunk/etc/apps/'):
        sudo('tar xvf /tmp/unix.tar.gz')
        local('rm -f unix.tar.gz')
        set_splunk_perms()
        start('f')


@task
def update_transforms(environment=None):
    """
    Updates transforms.conf on indexers
    p = production
    s = system test
    d = DataPower guys
    """
    if environment == None:
        print("Enter a valid environment")
        return

    if environment == 'p':
        strfile = 'splunk/conf/transforms.conf'
    elif environment == 's':
        strfile = 'splunk/conf/transforms_test.conf'
    elif environment == 'd':
        strfile = 'splunk/DP/transforms.conf'

    put(strfile, '/apps/splunk/etc/system/local/transforms.conf', use_sudo=True, mode=0755)
    set_splunk_perms()
    restart('f')


@task
def deploy_dpmgmt():
    """
    Deploys the DP management application for splunk
    """

    local('tar cvfz dpmgmt.tar.gz dpmgmt/')
    put('dpmgmt.tar.gz', '/tmp/dpmgmt.tar.gz', use_sudo=True, mode=0755)
    with cd('/apps/splunk/etc/apps/'):
        sudo('tar xvf /tmp/dpmgmt.tar.gz')
        set_splunk_perms()
        restart('f')
        local('rm -f dpmgmt.tar.gz')

@task
def deploy_dm_app():
    """
    deploys the Splunk Deployment monitor app
    """
    common.mountshare()
    with cd('/apps/splunk'):
        stop('f')
        sudo('tar xvf /apps/tmp/splunk/Apps/splunk_app_deploymentmonitor-5.0.3-181055.tgz')
        set_splunk_perms()
        restart('f')

@task
def update_limits():
    '''
    Updates the limits.conf within splunk to allow more concurrent searches
    '''

    put('splunk/conf/limits.conf', '/apps/splunk/etc/system/local/limits.conf', use_sudo=True, mode=0755)
    stop('f')
    set_splunk_perms()
    start('f')