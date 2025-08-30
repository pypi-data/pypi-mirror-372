#!/bin/bash

echo "...syncing timestamps"

PASSWORD=$( grep DATABASE_PASSWORD settings.py | cut -f2 -d\' )

mysql -u piprints -p$PASSWORD piprints <<EOF
update main_log     set creation_time     = o_creation_time;
update main_person  set creation_time     = o_creation_date;
update main_person  set modification_time = o_modification_date;
update main_paper   set creation_time     = o_creation_date;
update main_paper   set modification_time = o_modification_date;
update main_news    set creation_time     = o_creation_date;
update main_news    set modification_time = o_modification_date;
update main_event   set creation_time     = o_creation_date;
update main_event   set modification_time = o_modification_date;
update main_seminar set creation_time     = o_creation_date;
update main_seminar set modification_time = o_modification_date;
EOF

