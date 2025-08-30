#!/bin/bash

echo "...importing passwords"

PASSWORD=$( grep DATABASE_PASSWORD settings.py | cut -f2 -d\' )

USERS=../../users

if [ ! -f "$USERS" ] ; then
    echo unable to open file "$USERS"
    exit
fi

for username in $( cat $USERS | grep -v '#' | cut -f1 -d: ) ; do
   pass=$( cat $USERS | grep "^$username:" | cut -f2 -d: )
   salt=${pass:0:2}
   crypt="crypt\$$salt\$$pass"
   echo update main_user set password=\"$crypt\" where username=\"$username\" ";"
done | mysql -u piprints -p$PASSWORD piprints

