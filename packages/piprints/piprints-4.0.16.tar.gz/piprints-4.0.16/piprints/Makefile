shell:
	python manage.py shell

runserver:
	python manage.py runserver

syncdb:
	python manage.py syncdb

create-migration:
	python manage.py schemamigration main --auto
	hg add main/migrations/*.py

init-migration:
	python manage.py schemamigration main --initial
	hg add main/migrations/*.py

apply-migration:
	python manage.py migrate main

apache:
	sudo /etc/init.d/apache2 restart

clear_db:
	./clear_database.sh

import_data: clear_db
	./import_data.py
	./import_sync_timestamps.sh
	./import_set_passwords.sh

backup::
	./backup.sh
