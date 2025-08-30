#!/bin/bash

PASSWORD=$( grep DATABASE_PASSWORD settings.py | cut -f2 -d\' )

tables=$(echo "show tables" | mysql -u piprints -p$PASSWORD piprints | grep "^main")

tables="$tables south_migrationhistory"

commands=$(for table in $tables; do echo drop table $table ";" ; done )

echo "$commands" | mysql -u piprints -p$PASSWORD piprints

hg rm -f main/migrations/0*.py
rm main/migrations/0*.py
rm main/migrations/0*.pyc
make syncdb
make init-migration
make apply-migration
