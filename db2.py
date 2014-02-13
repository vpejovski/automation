"""
DB2 Fabric installation and configuration module.
"""

from fabric.api import *
import common


@task()
def db2engine_update_fixpack():
    '''Installs latest fixpack to db2 engine'''

    common.mountshare()
    instance_name = raw_input('Please enter instance name: ')

    db2engine_stop(instance_name)
    db2admin_stop()

    with cd('/apps/tmp/commerce/install/db2dscfp8'):
        run('./installFixPack -n -b /db2_exec/db2/V9.7')
        run('cd /')
        db2engine_db2update()
        db2engine_db2dasupdate()
        common.unmount_share()

    db2engine_start(instance_name)


def db2engine_db2update():
    '''Runs db2update command'''
    with cd('/db2_exec/db2/V9.7/instance'):
        run('./db2iupdt -k -e')


def db2engine_db2dasupdate():
    '''Runs das update command'''
    with cd('/db2_exec/db2/V9.7/instance'):
        run('./dasupdt')


def db2admin_stop():
    '''Stops the db2admin dasur1'''
    sudo('db2admin stop', user='dasusr1')


@task()
def db2engine_start(name=None):
    '''Starts DB2 engine, must be run as instance owner'''
    sudo('db2start', user=name)


def db2engine_stop(name=None):
    '''Stops db2 engine, must be run as instance owner'''
    sudo('db2stop force', user=name)


@task()
def create_portaldbs():
    '''Creates Portal Databases'''
    db2_bin_path = '/opt/ibm/db2/V9.7/bin'
    database_names = ['fdbkdb', 'lmdb', 'reldb', 'comdb', 'cusdb', 'jcrdb']
    db_path_list = ['db2data1', 'db2data2', 'db2data3', 'db2data4', 'db2data5', 'db2data6']

    for db_name in database_names:
        for db_path in db_path_list:
            with cd(db2_bin_path):
                run('./db2 "CREATE DATABASE ' + db_name + ' AUTOMATIC STORAGE YES ON /db2/' + db_path + 'USING CODESET UTF-8 territory us PAGESIZE 8192"')
                run('./db2 "UPDATE DB CFG for ' + db_name + ' USING applheapsz 4096;"')
                run('./db2 "UPDATE DB CFG for ' + db_name + ' USING app_ctl_heap_sz 1024;"')
                run('./db2 "UPDATE DB CFG for ' + db_name + ' USING stmtheap 32768;"')
                run('./db2 "UPDATE DB CFG for ' + db_name + ' USING dbheap 2400;"')
                run('./db2 "UPDATE DB CFG for ' + db_name + ' USING locklist 1000;"')
                run('./db2 "UPDATE DB CFG for ' + db_name + ' USING logfilsiz 4000;"')
                run('./db2 "UPDATE DB CFG for ' + db_name + ' USING logprimary 12;"')
                run('./db2 "UPDATE DB CFG for ' + db_name + ' USING logsecond 20;"')
                run('./db2 "UPDATE DB CFG for ' + db_name + ' USING logbufsz 32;"')
                run('./db2 "UPDATE DB CFG for ' + db_name + ' USING avg_appls 5;"')
                run('./db2 "UPDATE DB CFG for ' + db_name + ' USING locktimeout 30;"')
                run('./db2 "UPDATE DB CFG for ' + db_name + ' USING AUTO_MAINT off;"')


@task()
def grantportaldbaccess(user_name=None):
    '''Grants access to all Portal databases'''
    if user_name is None:
        print ("Provide a valid a userid")
        return

    db_list = ['fdbkdb', 'lmdb', 'reldb', 'comdb', 'cusdb', 'jcrdb']

    for db_name in db_list:
        with cd('/opt/ibm/db2/V9.7/bin'):
            run('./db2 "CONNECT TO ' + db_name + '"')
            run('./db2 "GRANT CREATE_EXTERNAL_ROUTINE ON DATABASE TO USER ' + user_name + '"')
            run('./db2 "GRANT DATAACCESS ON DATABASE TO USER ' + user_name + '"')
            run('./db2 "GRANT CREATE_NOT_FENCED_ROUTINE ON DATABASE TO USER ' + user_name + '"')
            run('./db2 "GRANT EXPLAIN ON DATABASE TO USER ' + user_name + '"')
            run('./db2 "GRANT IMPLICIT_SCHEMA ON DATABASE TO USER ' + user_name + '"')
            run('./db2 "GRANT SQLADM ON DATABASE TO USER ' + user_name + '"')
            run('./db2 "GRANT DBADM ON DATABASE TO USER ' + user_name + '"')
            run('./db2 "GRANT WLMADM ON DATABASE TO USER ' + user_name + '"')
            run('./db2 "GRANT LOAD ON DATABASE TO USER ' + user_name + '"')
            run('./db2 "GRANT QUIESCE_CONNECT ON DATABASE TO USER ' + user_name + '"')
            run('./db2 "GRANT CONNECT ON DATABASE TO USER ' + user_name + '"')
            run('./db2 "GRANT SECADM ON DATABASE TO USER ' + user_name + '"')
            run('./db2 "GRANT ACCESSCTRL ON DATABASE TO USER ' + user_name + '"')
            run('./db2 "GRANT BINDADD ON DATABASE TO USER ' + user_name + '"')
            run('./db2 "GRANT CREATETAB ON DATABASE TO USER ' + user_name + '"')
            run('./db2 "GRANT USE OF TABLESPACE TAB8K TO USER ' + user_name + '"')
            run('./db2 "GRANT USE OF TABLESPACE TAB16K TO USER ' + user_name + '"')
            run('./db2 "DISCONNECT ' + db_name + '"')
            run('./db2 "TERMINATE"')


@task()
def grantcommdbaccess(user_name=None):
    '''Grants access to all commerce dbs'''

    if user_name is None:
        print ("Provide a valid a userid")
        return

    db_list = ['sc3clive', 'sc3cstg']

    for db_name in db_list:
        run('db2 "CONNECT TO ' + db_name + '"')
        run('db2 "GRANT CREATE_EXTERNAL_ROUTINE ON DATABASE TO USER ' + user_name + '"')
        run('db2 "GRANT DATAACCESS ON DATABASE TO USER ' + user_name + '"')
        run('db2 "GRANT CREATE_NOT_FENCED_ROUTINE ON DATABASE TO USER ' + user_name + '"')
        run('db2 "GRANT EXPLAIN ON DATABASE TO USER ' + user_name + '"')
        run('db2 "GRANT IMPLICIT_SCHEMA ON DATABASE TO USER ' + user_name + '"')
        run('db2 "GRANT SQLADM ON DATABASE TO USER ' + user_name + '"')
        run('db2 "GRANT DBADM ON DATABASE TO USER ' + user_name + '"')
        run('db2 "GRANT WLMADM ON DATABASE TO USER ' + user_name + '"')
        run('db2 "GRANT LOAD ON DATABASE TO USER ' + user_name + '"')
        run('db2 "GRANT QUIESCE_CONNECT ON DATABASE TO USER ' + user_name + '"')
        run('db2 "GRANT CONNECT ON DATABASE TO USER ' + user_name + '"')
        run('db2 "GRANT SECADM ON DATABASE TO USER ' + user_name + '"')
        run('db2 "GRANT ACCESSCTRL ON DATABASE TO USER ' + user_name + '"')
        run('db2 "GRANT BINDADD ON DATABASE TO USER ' + user_name + '"')
        run('db2 "GRANT CREATETAB ON DATABASE TO USER ' + user_name + '"')
        run('db2 "GRANT USE OF TABLESPACE TAB8K TO USER ' + user_name + '"')
        run('db2 "GRANT USE OF TABLESPACE TAB16K TO USER ' + user_name + '"')
        run('db2 "DISCONNECT ' + db_name + '"')
        run('db2 "TERMINATE"')


@task(default=True)
def prepare_server():
    '''Runs full server preparation script'''
    common.install_telnet()
    common.install_screen()

    instance_name = raw_input('Please enter instance name: ')
    if instance_name is None:
        print 'Please enter instantce name!'
        return

    db2_prepare(instance_name)


def db2_prepare(instance_name=None, system_type='P'):
    """
    Prepares host for DB2 installation.
    """
    if instance_name is None:
        print('provide a valid instance name')

    db2_instance_user = instance_name.lower()
    db2_partition_script = 'db2_parted.sh'
    put('tools/' + db2_partition_script, db2_partition_script, mode=0755)
    run('/root/' + db2_partition_script)
    db2_create_db2ids(instance_name.lower(), system_type)
    run('mount -a')
    run('chown -R %s:db2admin1 /db2/db2data1' % db2_instance_user)
    run('chown -R %s:db2admin1 /db2/db2data2' % db2_instance_user)
    run('chown -R %s:db2admin1 /db2/db2data3' % db2_instance_user)
    run('chown -R %s:db2admin1 /db2/db2data4' % db2_instance_user)
    run('chown -R %s:db2admin1 /db2/db2data5' % db2_instance_user)
    run('chown -R %s:db2admin1 /db2/db2data6' % db2_instance_user)
    run('chown -R %s:db2admin1 /db2/db2logs' % db2_instance_user)
    run('chown -R %s:db2admin1 /db2/log_dir' % db2_instance_user)
    run('chown -R %s:db2admin1 /db2/temp' % db2_instance_user)
    run('lvextend /dev/mapper/rootvg-optlv -L+2G')
    run('resize2fs /dev/mapper/rootvg-optlv')
    db2_create_responsefile(db2_instance_user)
    run('rm /root/' + db2_partition_script)


def db2_create_responsefile(instance_name=None):
    '''Creates DB2 response file'''

    if instance_name is None:
        print('Need a valid instance name')

    source_path = 'tools/'
    response_filename = 'db2responsefile.rsp'
    strresponsefn = source_path + '/' + response_filename
    response_file = open(strresponsefn, 'w')
    response_file.write('LIC_AGREEMENT       = ACCEPT\n')
    response_file.write('PROD       = ADVANCED_ENTERPRISE_SERVER_EDITION\n')
    response_file.write('FILE       = /db2_exec/db2/V9.7\n')
    response_file.write('INSTALL_TYPE       = CUSTOM\n')
    response_file.write('COMP       = DB2_UPDATE_SERVICE\n')
    response_file.write('COMP       = COMMUNICATION_SUPPORT_TCPIP\n')
    response_file.write('COMP       = JDK\n')
    response_file.write('COMP       = JAVA_SUPPORT\n')
    response_file.write('COMP       = CONTROL_CENTER\n')
    response_file.write('COMP       = FIRST_STEPS\n')
    response_file.write('COMP       = BASE_DB2_ENGINE\n')
    response_file.write('COMP       = REPL_CLIENT\n')
    response_file.write('COMP       = LDAP_EXPLOITATION\n')
    response_file.write('COMP       = INSTANCE_SETUP_SUPPORT\n')
    response_file.write('COMP       = DB2_SAMPLE_DATABASE\n')
    response_file.write('COMP       = ACS\n')
    response_file.write('COMP       = SQL_PROCEDURES\n')
    response_file.write('COMP       = DB2_DATA_SOURCE_SUPPORT\n')
    response_file.write('COMP       = BASE_CLIENT\n')
    response_file.write('COMP       = CONNECT_SUPPORT\n')
    response_file.write('DAS_CONTACT_LIST       = LOCAL\n')
    response_file.write('DAS_USERNAME       = dasusr1\n')
    response_file.write('DAS_UID       = 90001\n')
    response_file.write('DAS_GROUP_NAME       = db2admin3\n')
    response_file.write('DAS_HOME_DIRECTORY       = /db2/dasusr1\n')
    response_file.write('INSTANCE       = inst1\n')
    response_file.write('inst1.TYPE       = ese\n')
    response_file.write('inst1.NAME       = ' + instance_name.lower() + '\n')
    response_file.write('inst1.UID       = 90002\n')
    response_file.write('inst1.GROUP_NAME       = db2admin1\n')
    response_file.write('inst1.HOME_DIRECTORY       = /db2/' + instance_name.lower() + '\n')
    response_file.write('inst1.AUTOSTART       = YES\n')
    response_file.write('inst1.SVCENAME       = db2c_' + instance_name.lower() + '\n')
    response_file.write('inst1.PORT_NUMBER       = 50004\n')
    response_file.write('inst1.FCM_PORT_NUMBER       = 60000\n')
    response_file.write('inst1.MAX_LOGICAL_NODES       = 4\n')
    response_file.write('inst1.CONFIGURE_TEXT_SEARCH       = NO\n')
    response_file.write('inst1.FENCED_USERNAME       = db2fenc1\n')
    response_file.write('inst1.FENCED_UID       = 90003\n')
    response_file.write('inst1.FENCED_GROUP_NAME       = db2admin2\n')
    response_file.write('inst1.FENCED_HOME_DIRECTORY       = /db2/' + instance_name.lower() + '\n')
    response_file.write('LANG       = EN\n')
    response_file.write('INSTALL_TSAMP = NO\n')
    response_file.close()
    put(strresponsefn, response_filename, mode=0755)


def db2_create_db2ids(username=None, system_type='p'):
    '''Creates instance id in the OS'''

    if username is None:
        print('Needs a valid username.')

    # User for portal or commerce db connection
    if system_type.lower() == 'p':
        was_db_user = 'was2db'

    elif system_type.lower() == 'c':
        was_db_user = 'com2db'

    else:
        print 'Please specify correct system type (P-Portal, C-Commerce).'
        return

    run('groupadd --gid 777 db2admin1')
    run('groupadd --gid 778 db2admin2')
    run('groupadd --gid 779 db2admin3')
    run('useradd --gid 779 -m --home /db2/dasusr1 dasusr1')
    run('useradd --gid 777 -m --home /db2/{0} {0}'.format(username.lower()))
    run('useradd --gid 778 -m --home /db2/{0} {1}'.format(username.lower(), 'db2fenc1'))
    run('chage -M 99999 db2fenc1')
    run('chage -M 99999 dasusr1')
    run('chage -M 99999 {0}'.format(username.lower()))
    run('echo -e "provide_otp\nprovide_otp" | passwd {0}'.format(username.lower()))

    run('groupadd --gid 501 websphereadmin')
    run('useradd --gid 501 -m {0}'.format(was_db_user))
    run('chage -M 99999 {0}'.format(was_db_user))
    run('echo -e "provide_otp\nprovide_otp" | passwd {0}'.format(was_db_user))


@task()
def db2_install_step_1():
    '''Runs db2 installation script base on a response file'''

    strresfile = 'db2responsefile.rsp'
    out = run('ls -a /apps')
    if not ('tmp' in out):
        run('mkdir /apps/tmp')
    run('mount -t nfs vclx00927:/apps/nfs_export /apps/tmp')
    with cd('/apps/tmp/db2_v9_7_installation/aese'):
        run('./db2setup -r /root/' + strresfile)
    run('umount /apps/tmp')
