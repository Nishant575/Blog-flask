from flask import render_template, url_for, flash, redirect
from blog.forms import RegistrationForm, LoginForm
from blog import app, db, bcrypt
from blog.models import User, Post
from flask_login import login_user, current_user, logout_user

@app.route('/')
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user , remember=form.remember.data)
            return redirect(url_for('home'))
        else:    
            flash('Incorrect email or password', 'danger')
    return render_template('login.html',form=form)

@app.route("/register", methods=['GET' , 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hash_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, email = form.email.data, password = hash_pass, bio = form.bio.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html',form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))    