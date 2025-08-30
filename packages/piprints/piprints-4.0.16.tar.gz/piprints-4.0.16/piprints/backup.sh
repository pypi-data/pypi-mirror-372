#!/bin/bash

stamp=$(date +"%Y-%m-%d")
out=backup/piprints-${stamp}.sql.gz
if [ -f $out ]; then
  echo file already exists... abort
  exit 1
else
    mysqldump piprints | gzip > $out
fi