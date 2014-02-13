#!/bin/bash
sfdisk /dev/sdb << EOF
0,,8e
EOF

pvcreate /dev/sdb1
vgcreate -s 128M db2vg /dev/sdb1
lvcreate -L 15G   -n backuplv     -p rw db2vg
lvcreate -L 5G    -n db2execlv    -p rw db2vg
lvcreate -L 100G  -n db2lv        -p rw db2vg
lvcreate -L 30G   -n appslv       -p rw db2vg	

mkfs.ext3 /dev/mapper/db2vg-backuplv
mkfs.ext3 /dev/mapper/db2vg-db2execlv  
mkfs.ext3 /dev/mapper/db2vg-db2lv      
mkfs.ext3 /dev/mapper/db2vg-appslv

mkdir /backup
mkdir /db2
mkdir /db2_exec
mkdir /apps

mount -t ext3 /dev/mapper/db2vg-db2lv /db2

#mkdir /db2/dasusr1 
mkdir /db2/log_dir 
mkdir /db2/db2logs 
#mkdir /db2/db2u001
mkdir /db2/temp
mkdir /db2/db2data1
mkdir /db2/db2data2
mkdir /db2/db2data3
mkdir /db2/db2data4
mkdir /db2/db2data5
mkdir /db2/db2data6

echo "/dev/mapper/db2vg-backuplv      /backup       ext3    defaults        1 3" >> /etc/fstab
echo "/dev/mapper/db2vg-db2lv         /db2          ext3    defaults        1 3" >> /etc/fstab
echo "/dev/mapper/db2vg-db2execlv     /db2_exec     ext3    defaults        1 3" >> /etc/fstab
echo "/dev/mapper/db2vg-appslv        /apps         ext3    defaults        1 3" >> /etc/fstab
