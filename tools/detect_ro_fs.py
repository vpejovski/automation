#!/usr/bin/env python

'''
Check if file system is in read-only mode.

reads /proc/mounts to see status of files systems.

Used for splunk integration.
'''

mounts = open('/proc/mounts', 'rb')

for line in mounts:
    parts = line.strip().split(' ')

    fs_options = parts[3].split(',')
    for item in fs_options:
        if 'ro' == item.strip().lower():
            print "File system {0} is in read-only mode.".format(parts[1])
        elif 'rw' == item.strip().lower():
        	print "File system {0} is in read-write mode.".format(parts[1])
