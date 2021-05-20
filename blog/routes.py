import secrets, os
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from blog.forms import RegistrationForm, LoginForm, UpdateProfileForm, PostForm
from blog import app, db, bcrypt
from blog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required

@app.route('/')
@app.route("/home")
def home():
    posts = Post.query.order_by(Post.date_posted.desc())
    return render_template('home.html',posts=posts)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user , remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:    
            flash('Incorrect email or password', 'danger')
    return render_template('login.html',title='Login',form=form)

def save_picture(form_picture):
    fname = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = fname + f_ext
    picture_path = os.path.join(app.root_path, 'static/resources/profile_pics', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/register", methods=['GET' , 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hash_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, email = form.email.data, password = hash_pass)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html',title='Register',form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))    

@app.route("/profile")
@login_required
def profile():
    image_file = url_for('static', filename='resources/profile_pics/' + current_user.image_file)
    user = User.query.filter_by(username=current_user.username).first_or_404()
    posts = Post.query.filter_by(author=current_user).order_by(Post.date_posted.desc())
    return render_template('profile.html',title='Profile',image_file=image_file,posts=posts,user=user)    


@app.route("/update", methods=['GET' , 'POST'])    
@login_required
def update():
    form = UpdateProfileForm()  
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data  
        current_user.email = form.email.data
        db.session.commit()
        flash(f'Account updated','success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('update.html',title='Update',form=form)  

def save_picture_post(form_picture):
    fname = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = fname + f_ext
    picture_path = os.path.join(app.root_path, 'static/resources/blog_pics', picture_fn)
    output_size = (500, 500)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn    

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post(): 
    form = PostForm()   
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture_post(form.picture.data)
            post = Post(title=form.title.data, content=form.content.data, author=current_user, image_post = picture_file)
        else:    
            post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Blog created','success')
        return redirect(url_for('home'))
    return render_template('post.html',title='New Post', form=form, legend='Create Post')

@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('blog.html', title=post.title, post=post)

@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture_post(form.picture.data)
            post.image_post = picture_file
        else:
            post.image_post = 'default_post.jpg'    
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('post.html', title='Update Post',form=form, legend='Update Post')    

@app.route("/post/<int:post_id>/delete")
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('profile'))    

@app.route("/user/<string:username>")
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    image_file = url_for('static', filename='resources/profile_pics/' + user.image_file)
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc())
    return render_template('profile.html', posts=posts, user=user,image_file=image_file)