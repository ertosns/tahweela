FROM ubuntu:20.04


RUN apt-get update &&apt-get install -y gnupg
# Add the PostgreSQL PGP key to verify their Debian packages.
# It should be the same key as https://www.postgresql.org/media/keys/ACCC4CF8.asc
RUN apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8

# Add PostgreSQL's repository. It contains the most recent stable release
#  of PostgreSQL.
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ precise-pgdg main" > /etc/apt/sources.list.d/pgdg.list


# Note: The official Debian and Ubuntu images automatically ``apt-get clean``
# after each ``apt-get``
# Run the rest of the commands as the ``postgres`` user created by the ``postgres-9.3`` package when it was ``apt-get installed``


MAINTAINER Mohab Metwally
# set a directory for the app
#WORKDIR /usr/src/app

# copy all the files to the container
COPY . .

ARG DEBIAN_FRONTEND=noninteractive

#install postgres, and python
#postgresql-9.3 postgresql-client-9.3 postgresql-contrib-9.3
        #apt-get update &&
RUN   apt-get install -y   postgresql-server-dev-12  postgresql-server-dev-all postgresql-12  postgresql-client-12 postgresql-contrib  build-essential  python3  python3-pip python3-pandas python-pip-whl python-wheel-common   python3-wheel

#postgresql postgresql-contrib libpq-dev libpq5

USER root

RUN adduser --disabled-password --gecos "" tahweela
#craete new role
#RUN  su - postgres createrole tahweela
#create database


# initialize the database
USER postgres
#role tahweela already exists
#  psql  -c "CREATE ROLE tahweela;"
RUN /etc/init.d/postgresql start  && psql -c "CREATE DATABASE db;" &&  psql -c "CREATE USER tahweela;"
# Adjust PostgreSQL configuration so that remote connections to the
# database are possible.
RUN echo "host all  all    0.0.0.0/0  md5" >> /etc/postgresql/12/main/pg_hba.conf
# And add ``listen_addresses`` to ``/etc/postgresql/9.3/main/postgresql.conf``
RUN echo "listen_addresses='*'" >> /etc/postgresql/12/main/postgresql.conf
# Expose the PostgreSQL port
EXPOSE 5432
# Add VOLUMEs to allow backup of config, logs and databases
VOLUME  ["/etc/postgresql", "/var/log/postgresql", "/var/lib/postgresql"]

#RUN /etc/init.d/postgresql stop
#RUN chmod 777 -R /
#run postgresql as tahweela
#/etc/init.d/postgresql start &&

#USER tahweela

RUN /etc/init.d/postgresql start && psql -d db  -w -f ./core/database/server_teardown.sql

RUN /etc/init.d/postgresql start && psql -d db  -w -f ./core/database/server_schema.sql

RUN /etc/init.d/postgresql start && psql -d db  -w -f ./core/database/server_initialize.sql
#
USER root
#RUN chown tahweela.tahweela -R
#RUN echo "db_configs=\"dbname='db'  user='tahweela' password='tahweela'\"" > core/configs.py
RUN echo "db_configs=\"dbname='db'  user='postgres'\"" > core/configs.py

#############
# install dependencies
#pandas==1.2.0
#pandas-datareader==0.9.0
# pip3 install --upgrade pip #this is always buggy, as well as --upgrade pip3, never use it!!!

RUN pip3 install --upgrade setuptools && pip3 install --no-cache-dir -r requirements.txt


RUN python3 setup.py build
RUN python3 setup.py install

#RUN python3 core/server/server.py
# define the port number the container should expose
##############
EXPOSE 5000
# run the command
USER postgres
CMD  /etc/init.d/postgresql start && python3 ./core/server/server.py
