from flask import render_template, url_for, flash, redirect
from blog.forms import RegistrationForm, LoginForm
from blog import app

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/login")
def login():

    form = LoginForm()
    return render_template('login.html',form=form)

@app.route("/register", methods=['GET' , 'POST'])
def register():
    form = RegistrationForm()
    
    return render_template('register.html',form=form)