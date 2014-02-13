from fabric.api import *
from fabric.colors import *
import StringIO
import json
import common
import tempfile

IDM_USERS = '''
{
    "user1":
        {
            "uid": 33333,
            "gid": 1000,
            "home_dir": "/home1/user1"
        },
    "user2":
        {
            "uid": 33334,
            "gid": 1000,
            "home_dir": "/home1/user2"
        },
    "user3":
        {
            "uid": 33335,
            "gid": 1000,
            "home_dir": "/home1/user3"
        },
    "user4":
        {
            "uid": 33336,
            "gid": 1000,
            "home_dir": "/home1/user4"
        }
}
'''

WEBSEAL_ALIASES = { 'webseal01': 'wsaliasp300x',
                    'webseal02': 'wsalias4p300x',
                    'webseal03': 'wsalias5p300x',
                    'webseal04': 'wsalias6p300x',
                    'webseal05': 'wsalias7p300x',
                    'webseal06': 'wsalias8p300x',
                    'webseal07': 'wsalias9p300x'
                    }

@task()
def user_add_extended(login_name, uid=None, gid=None,
                      home_dir=None, shell=None):
    """Adds user with additional parameters"""

    if not login_name:
        print "Please supply at least login_name."

    basic_command = ['useradd -m']

    if uid:
        basic_command.append('--uid {uid}'.format(uid=uid))

    if gid:
        basic_command.append('--gid {gid}'.format(gid=gid))

    if home_dir:
        basic_command.append('--home-dir {home_dir}'.format(home_dir=home_dir))

    if shell:
        basic_command.append('-s {shell}'.format(shell=shell))

    basic_command.append(login_name)

    run(' '.join(basic_command))

    run('echo -e "default_password\ndefault_password" | passwd \
        {login_name}'.format(login_name=login_name))


@task()
def add_idm_users(username=None):
    """
    Adding IDM users.
    """
    add_all_users = True
    idm_users = json.load(StringIO.StringIO(IDM_USERS))

    if username:
        add_all_users = False

    if add_all_users:
        for user_name in idm_users.keys():
            user = idm_users.get(user_name)

            user_add_extended(login_name=user_name,
                              uid=user.get('uid', None),
                              gid=user.get('gid', None),
                              home_dir=user.get('home_dir',
                                                '/home1/{user_name}'.format(
                                                user_name=user_name)),
                              shell=user.get('shell', '/bin/bash'))

        common.sudo_add(','.join(idm_users.keys()))
    else:
        user = idm_users.get(username)

        user_add_extended(login_name=username,
                          uid=user.get('uid', None),
                          gid=user.get('gid', None),
                          home_dir=user.get('home_dir',
                                            '/home1/{user_name}'.format(
                                            user_name=user_name)),
                          shell=user.get('shell', '/bin/bash'))

        common.sudo_add(username)


@task(default=True)
def prepare_server():
    '''runs the following functions in sequence partition_server();common.add_master_users();common.add_was_users();common.install_telnet();common.install_screen()'''
    partition_server()
    common.install_telnet()
    common.install_screen()


@task()
def partition_server():
    '''Partition Server'''
    strfbase = 'tools/'
    strihspart = 'was_parted.sh'
    put(strfbase + strihspart, strihspart, mode=0755)
    run('/root/' + strihspart)
    run('mount -a')
    run('lvextend /dev/mapper/rootvg-optlv -L+2G')
    run('resize2fs /dev/mapper/rootvg-optlv')
    run('rm /root/' + strihspart)

@task()
def complete_webseal():
    '''Execute all steps required for WebSEAL installation.'''
    install_webseal_prereqs()
    install_webseal()
    post_install_webseal()
    configure_webseal()
    stop_webseal()
    upload_webseal_files()
    upload_webseal_config('PROD')
    start_webseal()


@task()
def complete_webseal_syst():
    '''Execute all steps required for WebSEAL installation.'''
    install_webseal_prereqs()
    install_webseal()
    post_install_webseal()
    configure_webseal()
    stop_webseal()
    upload_webseal_files_syst()
    upload_webseal_config('ST')
    start_webseal()


@task()
def upload_apple_images():
    """
    Upload missing images that Apple devices request
    """
    run('rm -f /home1/{0}/apple-*'.format(env.user))
    put('idm/images/apple-touch-icon-114x114.png', '/home1/{0}'.format(env.user), mode=0444)
    put('idm/images/apple-touch-icon-114x114-precomposed.png', '/home1/{0}'.format(env.user), mode=0444)
    put('idm/images/apple-touch-icon-120x120.png', '/home1/{0}'.format(env.user), mode=0444)
    put('idm/images/apple-touch-icon-120x120-precomposed.png', '/home1/{0}'.format(env.user), mode=0444)
    put('idm/images/apple-touch-icon-144x144.png', '/home1/{0}'.format(env.user), mode=0444)
    put('idm/images/apple-touch-icon-144x144-precomposed.png', '/home1/{0}'.format(env.user), mode=0444)
    put('idm/images/apple-touch-icon-57x57.png', '/home1/{0}'.format(env.user), mode=0444)
    put('idm/images/apple-touch-icon-57x57-precomposed.png', '/home1/{0}'.format(env.user), mode=0444)
    put('idm/images/apple-touch-icon-72x72.png', '/home1/{0}'.format(env.user), mode=0444)
    put('idm/images/apple-touch-icon-72x72-precomposed.png', '/home1/{0}'.format(env.user), mode=0444)
    put('idm/images/apple-touch-icon.png', '/home1/{0}'.format(env.user), mode=0444)
    put('idm/images/apple-touch-icon-precomposed.png', '/home1/{0}'.format(env.user), mode=0444)

    sudo('mv /home1/{0}/apple-* /opt/pdweb/www-default/docs/'.format(env.user))
    sudo('chown ivmgr:ivmgr /opt/pdweb/www-default/docs/apple-*')

@task()
def install_webseal_prereqs():
    sudo('yum -q -y install libXp')
    sudo('yum -q -y install libXp.i686')
    sudo('yum -q -y install gtk2.i686 libXtst.i686 gtk2-engines.i686 \
                            libcanberra-gtk2.i686 PackageKit-gtk-module.i686')
    sudo('yum -q -y install gdb.x86_64 telnet')

@task()
def install_webseal():
    # install_webseal_prereqs()

    # WebSEAL dependancies
    with cd('/apps/install/WebSEAL611/linux_i386/'):
        sudo('yum localinstall -y ibm-java2-i386-sdk-5.0-5.0.i386.rpm')
        sudo('yum localinstall -y gsk7bas-7.0-4.28.i386.rpm')
        sudo('yum localinstall -y idsldap-cltbase61-6.1.0-6.i386.rpm')
        sudo('yum localinstall -y idsldap-clt32bit61-6.1.0-6.i386.rpm')
        sudo('yum localinstall -y idsldap-cltjava61-6.1.0-6.i386.rpm')

    # WebSEAL install

        sudo('yum localinstall -y PDlic-PD-6.1.1-0.i386.rpm')
        sudo('yum localinstall -y TivSecUtl-TivSec-6.1.1-0.i386.rpm')
        sudo('yum localinstall -y PDRTE-PD-6.1.1-0.i386.rpm')
        sudo('yum localinstall -y PDWebRTE-PD-6.1.1-0.i386.rpm')
        sudo('yum localinstall -y PDWeb-PD-6.1.1-0.i386.rpm')

    with cd('/apps/install/WebSEAL_FP4'):
        sudo('yum localinstall -y PDRTE-PD-6.1.1-4.i386.rpm')
        sudo('yum localinstall -y PDWebRTE-PD-6.1.1-4.i386.rpm')
        sudo('yum localinstall -y PDWeb-PD-6.1.1-4.i386.rpm')


@task()
def post_install_webseal():
    sudo('mkdir -p /apps/logs/www-default/log/')
    sudo('mkdir -p /apps/certs/')

    sudo('chown -R ivmgr:ivmgr /apps/logs')
    sudo('chown -R ivmgr:ivmgr /apps/certs/')


@task()
def configure_webseal():

    sudo('/opt/PolicyDirector/sbin/PDRTE_config')
    hostname = sudo('hostname')
    sec_master_pass = raw_input('Please enter sec_master password: ')

    new_hostname = WEBSEAL_ALIASES[hostname]
    #print hostname, new_hostname

    am_web_cfg = ['amwebcfg', '-action', 'config', '-inst_name', 'default',
                  '-host', new_hostname, '-listening_port', '7234', '-admin_id',
                  'sec_master', '-admin_pwd', sec_master_pass.strip(), '-ssl_yn no',
                  '-cert_label', 'ibm_cert', '-ssl_port', '636', '-http_yn',
                  'yes', '-http_port', '80', '-https_yn', 'yes', '-https_port',
                  '443', '-doc_root', '/opt/pdweb/www-default/docs',
                  '-nw_interface_yn', 'no', '-domain', 'Default']

    am_web_cfg_line = (' ').join(am_web_cfg)

    sudo(am_web_cfg_line)


@task()
def get_webseal_files_prod():
    '''Gather files to transfer to other server.'''

    local('rm -f idm/webseal/webseal_*.tar.gz')

    with cd('/home1/{0}'.format(env.user)):
        sudo('rm -f webseal_*.tar.gz')

    with cd('/opt/pdweb/www-default/lib'):
        sudo('tar czf /home1/{0}/webseal_lib.tar.gz *'.format(env.user))

    with cd('/opt/pdweb/www-default/docs'):
        sudo('tar czf /home1/{0}/webseal_docs.tar.gz *'.format(env.user))

    with cd('/apps/certs'):
        sudo('tar czf /home1/{0}/webseal_certs.tar.gz *'.format(env.user))

    with cd('/opt/pdweb/www-default/jct'):
        sudo('tar czf /home1/{0}/webseal_jct.tar.gz *'.format(env.user))

    with cd('/var/pdweb/www-default/certs'):
        sudo('tar czf /home1/{0}/webseal_failover.tar.gz *'.format(env.user))

    with cd('/opt/pdweb/bin'):
        sudo('cp pdweb_start /home1/{0}/pdweb_start'.format(env.user))

    sudo('chown {0}:staff /home1/{0}/*'.format(env.user))

    get('/home1/{0}/webseal_lib.tar.gz'.format(env.user), 'idm/webseal/')
    get('/home1/{0}/webseal_docs.tar.gz'.format(env.user), 'idm/webseal/')
    get('/home1/{0}/webseal_certs.tar.gz'.format(env.user), 'idm/webseal/')
    get('/home1/{0}/webseal_jct.tar.gz'.format(env.user), 'idm/webseal/')
    get('/home1/{0}/webseal_failover.tar.gz'.format(env.user), 'idm/webseal/')
    get('/home1/{0}/pdweb_start'.format(env.user), 'idm/webseal/')


@task()
def upload_webseal_files():
    '''Gather files to transfer to other server.'''
    remote_home_dir = '/home1/{0}/'.format(env.user)
    run('rm -f {0}webseal_*.tar.gz'.format(remote_home_dir))
    run('rm -f {0}pdweb_start'.format(remote_home_dir))
    run('rm -f {0}ldap.conf'.format(remote_home_dir))

    put('idm/webseal/webseal_lib.tar.gz', remote_home_dir)
    put('idm/webseal/webseal_docs.tar.gz', remote_home_dir)
    put('idm/webseal/webseal_certs.tar.gz', remote_home_dir)
    put('idm/webseal/webseal_jct.tar.gz', remote_home_dir)
    put('idm/webseal/webseal_failover.tar.gz', remote_home_dir)
    put('idm/webseal/pdweb_start', remote_home_dir)
    put('idm/webseal/ldap.conf', remote_home_dir)

    with cd('/apps/certs'):
        sudo('tar xf {0}webseal_certs.tar.gz'.format(remote_home_dir))

    with cd('/opt/pdweb/www-default/lib'):
        sudo('tar xf {0}webseal_lib.tar.gz'.format(remote_home_dir))

    with cd('/opt/pdweb/www-default/docs'):
        sudo('tar xf {0}webseal_docs.tar.gz'.format(remote_home_dir))

    with cd('/opt/pdweb/www-default/jct'):
        sudo('tar xf {0}webseal_jct.tar.gz'.format(remote_home_dir))

    with cd('/var/pdweb/www-default/certs'):
        sudo('tar xf {0}webseal_failover.tar.gz'.format(remote_home_dir))

    # pdweb_start
    sudo('mv {0}pdweb_start /opt/pdweb/bin'.format(remote_home_dir))
    sudo('chown ivmgr:ivmgr /opt/pdweb/bin/pdweb_start')
    sudo('chmod 550 /opt/pdweb/bin/pdweb_start')

    # ldap.conf
    sudo('mv {0}ldap.conf /opt/PolicyDirector/etc'.format(remote_home_dir))
    sudo('chown ivmgr:ivmgr /opt/PolicyDirector/etc/ldap.conf')
    sudo('chmod 644 /opt/PolicyDirector/etc/ldap.conf')


@task()
def get_webseal_files_syst():
    '''Gather files to transfer to other server.'''

    local('rm -f idm/webseal/st/webseal_*.tar.gz')

    with cd('/home1/{0}'.format(env.user)):
        sudo('rm -f webseal_*.tar.gz')

    with cd('/opt/pdweb/www-default/lib'):
        sudo('tar czf /home1/{0}/webseal_lib.tar.gz *'.format(env.user))

    with cd('/opt/pdweb/www-default/docs'):
        sudo('tar czf /home1/{0}/webseal_docs.tar.gz *'.format(env.user))

    with cd('/apps/certs'):
        sudo('tar czf /home1/{0}/webseal_certs.tar.gz *'.format(env.user))

    with cd('/opt/pdweb/www-default/jct'):
        sudo('tar czf /home1/{0}/webseal_jct.tar.gz *'.format(env.user))

    with cd('/var/pdweb/www-default/certs'):
        sudo('tar czf /home1/{0}/webseal_failover.tar.gz *'.format(env.user))

    with cd('/opt/pdweb/bin'):
        sudo('cp pdweb_start /home1/{0}/pdweb_start'.format(env.user))

    sudo('chown {0}:staff /home1/{0}/*'.format(env.user))

    get('/home1/{0}/webseal_lib.tar.gz'.format(env.user), 'idm/webseal/st/')
    get('/home1/{0}/webseal_docs.tar.gz'.format(env.user), 'idm/webseal/st/')
    get('/home1/{0}/webseal_certs.tar.gz'.format(env.user), 'idm/webseal/st/')
    get('/home1/{0}/webseal_jct.tar.gz'.format(env.user), 'idm/webseal/st/')
    get('/home1/{0}/webseal_failover.tar.gz'.format(env.user), 'idm/webseal/st/')
    get('/home1/{0}/pdweb_start'.format(env.user), 'idm/webseal/st/')

@task()
def upload_webseal_files_syst():
    '''Gather files to transfer to other server.'''
    remote_home_dir = '/home1/{0}/'.format(env.user)
    run('rm -f {0}webseal_*.tar.gz'.format(remote_home_dir))
    run('rm -f {0}pdweb_start'.format(remote_home_dir))
    run('rm -f {0}ldap.conf'.format(remote_home_dir))

    put('idm/webseal/st/webseal_lib.tar.gz', remote_home_dir)
    put('idm/webseal/st/webseal_docs.tar.gz', remote_home_dir)
    put('idm/webseal/st/webseal_certs.tar.gz', remote_home_dir)
    put('idm/webseal/st/webseal_jct.tar.gz', remote_home_dir)
    put('idm/webseal/st/webseal_failover.tar.gz', remote_home_dir)
    put('idm/webseal/st/pdweb_start', remote_home_dir)
    put('idm/webseal/st/ldap.conf', remote_home_dir)

    with cd('/apps/certs'):
        sudo('tar xf {0}webseal_certs.tar.gz'.format(remote_home_dir))

    with cd('/opt/pdweb/www-default/lib'):
        sudo('tar xf {0}webseal_lib.tar.gz'.format(remote_home_dir))

    with cd('/opt/pdweb/www-default/docs'):
        sudo('tar xf {0}webseal_docs.tar.gz'.format(remote_home_dir))

    with cd('/opt/pdweb/www-default/jct'):
        sudo('tar xf {0}webseal_jct.tar.gz'.format(remote_home_dir))

    with cd('/var/pdweb/www-default/certs'):
        sudo('tar xf {0}webseal_failover.tar.gz'.format(remote_home_dir))

    # pdweb_start
    sudo('mv {0}pdweb_start /opt/pdweb/bin'.format(remote_home_dir))
    sudo('chown ivmgr:ivmgr /opt/pdweb/bin/pdweb_start')
    sudo('chmod 550 /opt/pdweb/bin/pdweb_start')

    # ldap.conf
    sudo('mv {0}ldap.conf /opt/PolicyDirector/etc'.format(remote_home_dir))
    sudo('chown ivmgr:ivmgr /opt/PolicyDirector/etc/ldap.conf')
    sudo('chmod 644 /opt/PolicyDirector/etc/ldap.conf')


@task()
def upload_webseal_config(environment=None):
    '''Upload webseald-default.conf'''
    if environment is None:
        print "Please specify environment ST or PROD"
        return

    hostname = sudo('hostname')
    if hostname in WEBSEAL_ALIASES.keys():
        webseal_hostname = WEBSEAL_ALIASES[hostname]
    else:
        print "Host name is not defined", hostname
        return

    wsd_conf = tempfile.NamedTemporaryFile(mode="w", prefix="xyz", dir='/tmp', delete=False)

    if environment.lower() == 'prod':
        with open('idm/webseal/prod-webseald-default.conf') as wsd_conf_template:
            wsd_conf_content = wsd_conf_template.read()
    elif environment.lower() == 'st':
        with open('idm/webseal/st/st-webseald-default.conf') as wsd_conf_template:
            wsd_conf_content = wsd_conf_template.read()
    else:
        print "Please specify environment ST or PROD"
        return

    wsd_conf_content = wsd_conf_content.replace('{{WEBSEAL_NAME}}', webseal_hostname)
    wsd_conf.write(wsd_conf_content)
    wsd_conf.close()

    put(wsd_conf.name, '/opt/pdweb/etc/webseald-default.conf', use_sudo=True, mode=0640)
    sudo('chown ivmgr:ivmgr /opt/pdweb/etc/webseald-default.conf')

    with cd('/opt/pdweb/etc'):
        sudo('pdadmin -l config modify keyvalue set -obfuscate webseald-default.conf junction basicauth-dummy-passwd some_dummy_password)

@task()
def stop_webseal():
    sudo('/usr/bin/pdweb stop')

@task()
def start_webseal():
    sudo('/usr/bin/pdweb start')

@task()
def push_file():
    # ldap.conf
    remote_home_dir = '/home1/{0}/'.format(env.user)
    put('idm/webseal/ldap.conf', remote_home_dir)
    sudo('mv {0}ldap.conf /opt/PolicyDirector/etc'.format(remote_home_dir))
    sudo('chown ivmgr:ivmgr /opt/PolicyDirector/etc/ldap.conf')
    sudo('chmod 644 /opt/PolicyDirector/etc/ldap.conf')

@task()
def prepare_install_filesl():

    sudo('cp webseal_install_files.tar.gz /apps')
    with cd('/apps'):
        sudo('tar xf webseal_install_files.tar.gz')
        sudo('chown user:staff webseal_install_files.tar.gz')

    with cd('/apps/install'):
        sudo('chmod -R o+rwx .')

    with cd('/home1/{0}/'.format(env.user)):
        sudo('rm webseal_install_files.tar.gz')