#!/bin/bash
sfdisk /dev/sdb << EOF
0,,8e
EOF

pvcreate /dev/sdb1
vgcreate -s 128M appsvg /dev/sdb1
lvcreate -l 100%VG -n appslv -p rw appsvg
mkfs.ext3 /dev/mapper/appsvg-appslv

mkdir /apps

diskuuid=`blkid /dev/mapper/appsvg-appslv | awk '{print $2}'`
echo "$diskuuid /apps ext3 defaults 1 2" >> /etc/fstab
