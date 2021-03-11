#common:
#	psql -d demo -U tahweela -w -f ./core/database/teardown.sql
#	psql -d demo -U tahweela -w -f ./core/database/schema.sql
#	psql -d demo -U tahweela -w -f ./core/database/initialize.sql
#frontend:
#	psql -d demo_client -U tahweela_client -w -f ./database/client_teardown.sql
#	psql -d demo_client -U tahweela_client -w -f ./database/client_schema.sql
#	psql -d demo_client -U tahweela_client -w -f ./database/client_initialize.sql
#restart:
#	sudo /etc/init.d/postgresql restart

USER=tahweela
install: 
	python3 ./setup.py build
	python3 ./setup.py install
backend:
	psql -d demo -U tahweela -w -f ./core/database/server_teardown.sql
	psql -d demo -U tahweela -w -f ./core/database/server_schema.sql
	psql -d demo -U tahweela -w -f ./core/database/server_initialize.sql

test:
	sudo -u tahweela python3 ./core/tests/database.py
	sudo -u tahweela python3 ./core/tests/core_test.py


docgen:
	doxygen ./docs/Doxyfile WORKING_DIRECTORY ../docs
	make WORKING_DIRECTORY ./docs/latex

#all: test docgen
#	sudo adduser --disabled-password --gecos "" $(USER)
#craete new role
#	sudo -u postgres createrole tahweela
#create database
#	sudo -u postgres psql -U postgres -c "CREATE DATABASE tahweela;"
#	sudo -u postgres psql -U postgres -c "CREATE USER tahweela;"
#	sudo -u tahweela  python3 core/server/server.py
