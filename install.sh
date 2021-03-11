#!/bin/bash

#prepare environment
#sudo apt-get update
#sudo apt-get install -y gnupg
#sudo apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8
#sudo echo "deb http://apt.postgresql.org/pub/repos/apt/ precise-pgdg main" > /etc/apt/sources.list.d/pgdg.list

#sudo apt-get install -y  build-essential  python3  python3-pip python3-pandas python-pip-whl python-wheel-common   python3-wheel  postgresql-server-dev-12  postgresql-server-dev-all postgresql-12  postgresql-client-12 postgresql-contrib

#sudo pip3 install pandas  setuptools Faker==5.5.1 requests==2.22.0 requests-oauthlib==1.3.0 requests-unixsocket==0.2.0 Flask==1.1.2 Flask-HTTPAuth==4.2.0 psycopg2==2.8.4


USER="postgres"
DB="db"
sudo adduser --disabled-password --gecos "" ${USER} 2> /dev/null
#craete new role

#sudo -u postgres createrole ${USER} 2> /dev/null

#create database
#sudo -u postgres psql -U postgres -c "CREATE ROLE ${USER};"
sudo -u postgres psql -U postgres -c "CREATE DATABASE ${DB};"
sudo -u postgres psql -U postgres -c "CREATE USER ${USER};"
#
sudo -u postgres psql -d ${DB} -U ${USER} -w -f ./core/database/server_teardown.sql
sudo -u postgres psql -d ${DB} -U ${USER} -w -f ./core/database/server_schema.sql
sudo -u postgres psql -d ${DB} -U ${USER} -w -f ./core/database/server_initialize.sql

#chown "$USER.$USER" -R *
#sudo echo "db_configs=\"dbname='${DB}'  user='${USER}' password='${USER}'\"" > core/configs.py
sudo echo "db_configs=\"dbname='${DB}'  user='${USER}' \"" > core/configs.py

sudo python3 setup.py build
sudo python3 setup.py install
sudo -u ${USER}  python3 core/server/server.py
