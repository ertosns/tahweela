#FROM python:3
FROM ubuntu:20.04.1

# set a directory for the app
WORKDIR /usr/src/app

# copy all the files to the container
COPY . .

#TODO some commands require sudo

RUN apt-get install python3
RUN docker pull postgres
#make new tahweela user
RUN audo adduser --disabled-password --gecos "" tahweela
#craete new role
RUN sudo -u postgres createrole tahweela
#create database
RUN sudo -u postgres  psql -U postgres -c "CREATE DATABASE tahweela;"
RUN sudo -u postgres psql -U postgres -c "CREATE USER tahweela;"

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# define the port number the container should expose
EXPOSE 5000

# run the command
CMD ["python3", "server/server.py"]
