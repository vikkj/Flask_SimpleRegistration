from flask import Flask, redirect,url_for,session,render_template,flash,request,Markup
import os
from datetime import timedelta
import json
from authlib.integrations.flask_client import OAuth
from flask_sqlalchemy import SQLAlchemy
import base64
from functools import wraps


app = Flask(__name__)

db = SQLAlchemy(app)
global client_id
global client_secret

client_id = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
client_secret = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"


app.secret_key="something secret"
app.config['SESSION_COOKIE_NAME']='google-login-session'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site1.db'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20),nullable=False)
    email = db.Column(db.String(120),unique=True,nullable=False)
    gender = db.Column(db.String(20),nullable=False)
    skill = db.Column(db.String(20),nullable=False)
    certification = db.Column(db.String(20),nullable=False)
    phoneno = db.Column(db.String(20),nullable=False)
    address = db.Column(db.String(20),nullable=False)
    education = db.Column(db.String(20),nullable=False)
    specialization = db.Column(db.String(20),nullable=False)
    profile_img = db.Column(db.BLOB)

    def __repr__(self):
        return f"User('{self.username}','{self.email}','{self.gender}','{self.phoneno}','{self.address}','{self.skill}','{self.education}','{self.specialization}','{self.certification}','{self.profile_img}')"

class RegisteredUsers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uname = db.Column(db.String(20),unique=True,nullable=False)
    password = db.Column(db.String(20),nullable=False)

    def __repr__(self):
        return f"RegisteredUsers('{self.uname}','{self.password}')"
db.create_all()

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=client_id,
    client_secret=client_secret,
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    client_kwargs={'scope':'openid email profile'},
)

def databasefilteration(obj,query):
    return obj.query.filter_by(**query)

def isLoggedIn(func):
    @wraps(func)
    def wrapper():
        user = dict(session).get('profile',None)
        if user:
            return func(True, user)
        else:
            return func(False, {})
    return wrapper
    


@app.route('/')
def home():
    return render_template('Login1.html')

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == 'POST':
        existence = databasefilteration(RegisteredUsers,{'uname':request.form['uname']}).all()#[]
        if existence!=[]:
            login = databasefilteration(RegisteredUsers,{'uname':request.form['uname']}).first()#Nonetype
            if request.form['uname'] == login.uname and request.form['pass'] == login.password:
                session['profile'] = request.form['uname']
                session.permanent = True
                return redirect('/data_entry')
            else:
                flash(Markup(f"No login data for {request.form['uname']} found! Please click <a href='/authorize_email'>here</a>"),"failed")
                return redirect('/')
        else:
            flash(Markup(f"No login data for {request.form['uname']} found! Please click <a href='/authorize_email'>here</a>"),"failed")
            return redirect('/')
    else:
        flash('No GET method allowed!')
        return redirect('/')


@app.route('/glogin')
def glogin():
    google = oauth.create_client('google')
    redirect_uri = url_for('authorize',_external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/authorize_email',methods=['POST','GET'])
def authorize_email():
    if request.method=='POST':
        if databasefilteration(RegisteredUsers,{'uname':request.form['email']}).all()==[]:
            regUser = RegisteredUsers(uname=request.form['email'],password=request.form['pass'])
            db.session.add(regUser)
            db.session.commit()
            flash('User Registration Successful')
            return redirect('/')
        else:
            flash('Oops! Sorry but this email is taken')
            return redirect('/authorize_email')
    return render_template('Register_email.html')
    
@app.route('/authorize')
def authorize():
    try:
        google = oauth.create_client('google')
        token = google.authorize_access_token()
        resp = google.get('userinfo')
        user_info = resp.json()
        user = oauth.google.userinfo()
        session['profile'] = user_info['email']
        if databasefilteration(RegisteredUsers,{'uname':user_info['email']}).all()==[]:
            regUser = RegisteredUsers(uname=user_info['email'],password=user_info['given_name'])
            db.session.add(regUser)
            db.session.commit()
        session.permanent = True
        
        return redirect('/data_entry')
    except Exception as e:
        flash(f"Bad Request! Try Logging in from your registered email address")
        return redirect('/')

@app.route('/data_entry',methods=['POST','GET'])
@isLoggedIn
def data_entry(flag,user):
    if flag:
        if request.method=='POST' and databasefilteration(RegisteredUsers,{'uname':user}).count()==1 and flag:
            flash(f'Account created for {request.form["name"]}!', "success")
            user_1 = User(username=request.form['name'],email=user,gender=request.form['gender'],skill=request.form['skill'],certification=request.form['cert'],phoneno=request.form['ph'],address=request.form['add'],education=request.form['edu'],specialization=request.form['special'],profile_img=request.files['file'].read())
            db.session.add(user_1)
            db.session.commit()
        elif request.method=='POST' and User.query.count()!=0 and flag:
            mod = User.query.first()
            flash(f'Account details updated for {mod.username}!','success')
            mod.skill = request.form['skill']
            mod.certification = request.form['cert']
            mod.phoneno = request.form['ph']
            mod.address = request.form['add']
            mod.education = request.form['edu']
            mod.specialization = request.form['special']
            db.session.commit()  
        if databasefilteration(User,{'email':user}).first()!=None:
            img =  base64.b64encode( databasefilteration(User,{'email':user}).first().profile_img).decode('ascii')
        else:
            img = b'ZGF0YSB0byBiZSBlbmNvZGVk'
        return render_template('Registration.html', flag=flag, user=user, loginc=databasefilteration(User,{'email':user}).count(), Userdata=databasefilteration(User,{'email':user}).first(), Image=img)
    else:
        flash("Please Login!")
        return redirect('/')

@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    flash(f"Successfully Logged Out","success")
    return redirect('/')



if __name__=='__main__':
    app.run(debug=True) 