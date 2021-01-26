#common:
#	psql -d demo -U tahweela -w -f ./database/teardown.sql
#	psql -d demo -U tahweela -w -f ./database/schema.sql
#	psql -d demo -U tahweela -w -f ./database/initialize.sql
backend:
	psql -d demo -U tahweela -w -f ./database/server_teardown.sql
	psql -d demo -U tahweela -w -f ./database/server_schema.sql
	psql -d demo -U tahweela -w -f ./database/server_initialize.sql
frontend:
	psql -d demo_client -U tahweela_client -w -f ./database/client_teardown.sql
	psql -d demo_client -U tahweela_client -w -f ./database/client_schema.sql
	psql -d demo_client -U tahweela_client -w -f ./database/client_initialize.sql
restart:
	sudo /etc/init.d/postgresql restart
install:
	python3 ../setup.py install
test: backend
	python3 tests/database.py
	python3 tests/core_test.py

build:
	python3 ../setup.py build
