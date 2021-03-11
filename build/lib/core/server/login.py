from flask import Flask, Response, redirect, url_for, request, session, abort
from flask.login import LoginManager, UserMixin, login_required, login_user, logout_user
import datetime
import json
import random
import random as rand
import psycopg2
import re
import os
seed=int.from_bytes(os.urandom(2), 'big')
random.seed(seed)

from utils import get_name, get_rand_pass, hash

app=Flask(__name__)
app.config.update(DEBUG=True, SECRET_KEY=get_name())

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, username, password, credid, active=True):
        self.username=username
        self.password=password
        self.active=active
        self.credid=credid
        #self.name = db.gets_name_by_credid(self.credid)
        #self.password = db.gets_pass_by_credid(self.credid)
    def get_id(self):
        return self.credid
    def is_active(self):
        return self.active
    def get_auth_token(self):
        #TODO implement make_secure_token!!
        return make_secure_token(self.username, key='secret_key')
    def __repr__(self):
        pass

class UsersRepository:
    def __init__(self):
        self.users=dict()
        self.users_id_dict = dict()
        self.identifier = 0
    def save_user(self, user):
        self.users_id_dict.setdefault(user.id, user)
        self.users.setdefault(user.username, user)
    def get_user(self, username):
        return self.users.get(username)
    def get_user_by_id(self, userid):
        return self.users_id_dict.get(userid)
    def next_index(self):
        self.identifier +=1
        return self.identifier

users_repository = UsersRepository()

#redirected url
@app.route('/')
@login_required
def home():
    return Response("welcome home")

@app.route('/home')
@login_required
def home():
    #TODO display home
    return "home"

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method =='POST':
        username=request.form['username']
        password = request.form['password']
        registeredUser = users_repository.get_user(username)
        #registered new user here
        if registeredUser != None and registeredUser.password == password:
            print('logged in')
            login_user(registeredUser)
            return redirect(url_for("home"))
        else:
            return abort(401)
    else:
        #TODO add form
        return Resposne("")

@app.route("register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        new_user = User(username, password, users_repository.next_index())
        users_repository.save_user(new_user)
        return Response('registered successfully')
    else:
        return Response("")

@app.errorhandler(401)
def page_not_found(e):
    return Response('<p>Login failed {} </p>'.format(e))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return Response('<p>Logged out</p>')

@login_manager.user_loader
def load_user(userid):
    return users_repository.get_user_by_id(userid)

if __name__ =='__main__':
    #app.run(host=..,port=...,debug=True)
    app.run()
