#!/usr/bin/env python

'''
Runs as a cron task. It will check if sudoers file have include
statement in and add one if none present. This will allow us
to have a machine specific sudoers file after provisioning.

Master sudoers file will still be updated and cron will make sure
we check every 15 minutes.
'''

import subprocess
import logging
import ConfigParser

CONFIG_FILE='/usr/local/etc/make_sudo_work.conf'

class Config(object):

    def __init__(self, config_file):
        self.config_file = config_file
        self.config = ConfigParser.ConfigParser()
        self.config.read(self.config_file)

    def get_log_level(self):
        return self.config.get('logging', 'log_level')

    def get_log_file(self):
        return self.config.get('logging', 'log_file')


def main():
    with open('/etc/sudoers', 'rb') as sudoers_file:
        file_content = sudoers_file.read()

    # print file_content

    if not '#includedir /etc/sudoers.d' in file_content:
        logging.info('Sudoers file does not contain #includedir directive. Fixing...')

        subprocess.Popen(['chmod', '0540', '/etc/sudoers']).wait()

        file_content += '\n#includedir /etc/sudoers.d\n'

        with open('/etc/sudoers', 'wb') as sudoers_file:
            sudoers_file.write(file_content)

        subprocess.Popen(['chmod', '0440', '/etc/sudoers']).wait()

if __name__ == '__main__':
    logging.basicConfig(filename='/var/log/make_sudo_work.log', level=logging.INFO, format='%(asctime)-15s %(message)s')
    logging.info('Running check of sudoers file...')
    main()