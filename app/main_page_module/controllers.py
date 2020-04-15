# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, jsonify
# Import the database object from the main app module
from app import db

# Import module forms
from app.main_page_module.forms import LoginForm, RegisterForm, EditUserForm

# Import module models (i.e. User)
from app.main_page_module.models import User, App, Language
#import os
import re
import os
from functools import wraps

from modules.argus import WSearch
import modules.op_app_gatherer as oag


# Define the blueprint: 'auth', set its url prefix: app.url/auth
main_page_module = Blueprint('main_page_module', __name__, url_prefix='/')


#login decorator
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' in session:
            return f(*args, **kwargs)
        
        else:
            flash("Please login to access the site.", "error")
            
            return redirect(url_for("main_page_module.login"))
    
    return wrapper


# Set the route and accepted methods
@main_page_module.route('/', methods=['GET'])
def index():

    return render_template("main_page_module/index.html")


# Set the route and accepted methods
@main_page_module.route('/all_apps', methods=['GET'])
def all_apps():
    apps = App.query.all()
    
    apps_n_languages = []
    for app in apps:
        app_bucket = []
        languages_ofapp = []
        
        for lang in Language.query.filter_by(app_id=app.app_id):
            languages_ofapp.append(lang.language)
        
        app_bucket.append(app)
        app_bucket.append(", ".join(languages_ofapp))
                          
        apps_n_languages.append(app_bucket)
    

    return render_template("main_page_module/all_apps.html", apps = apps_n_languages)

# Set the route and accepted methods
@main_page_module.route('/update_db', methods=['post'])

def update_db():
    apps = oag.get_app_details_All()
    print(len(apps))
    
    language = "Unknown"
    for app_details in apps:
        print(app_details["name"])
        
        if "github" in app_details["source"]:
            languages = oag.sort_languages(oag.get_github_languages(app_details["source"]))
            
        elif "gitlab" in app_details["source"]:
            languages = oag.sort_languages(oag.get_gitlab_languages(app_details["source"]))
        print(languages)
        
        for lang in languages:
            db_lang = Language(app_details["id"], lang)
            db.session.add(db_lang)
        
        app_db = App(app_details["id"], app_details["name"], app_details["author"], app_details["maintainer"], app_details["category"], 
                     app_details["license"], app_details["description"], app_details["source"])
        db.session.add(app_db)
    
    db.session.commit()

    flash('Database sucessfully updated!', 'success')
    
    return redirect(url_for("main_page_module.index"))


@main_page_module.route('/admin/all_users/')
@login_required
def all_users():    
    users = User.query.all()
   
    return render_template("main_page_module/admin/all_users.html", users=users)


@main_page_module.route('/admin/view_user/<user_id>')
@login_required
def view_user(user_id):    
    user = User.query.filter_by(id=user_id).first()
   
    if not user:
        flash('User does not exist.', 'error')
        
        return redirect(url_for("main_page_module.all_users"))     
    
    form = EditUserForm()
    form.process(obj=user)
    
   
    return render_template("main_page_module/admin/view_user.html", form=form, user=user)

@main_page_module.route('/admin/modify_user/', methods=['POST'])
@login_required
def modify_user():    
    form = EditUserForm(request.form)
    
    if form.validate_on_submit():
        user = User.query.filter_by(id=form.id.data).first()
        
        if not user:
            flash('User does not exist.', 'error')
        
            return redirect(url_for("main_page_module.all_users")) 
        
        else:
            user.name =  form.name.data
            user.email =  form.email.data
            if form.password.data != "":
                user.set_password(form.password.data)
    
            db.session.commit()   
        
        flash('User successfully Eddited!', 'success')
        
        return redirect(url_for("main_page_module.view_user", user_id=form.id.data, form=form))
    
    flash('Invalid data.', 'error')

    return redirect(url_for("main_page_module.all_users"))     
    

@main_page_module.route('/admin/delete/', methods=['POST'])
@login_required
def delete_user():
    user_id = request.form["id"]
    
    user = User.query.filter_by(id=user_id).first()
   
    if not user:
        flash('User does not exist.', 'error')
        
        return redirect(url_for("main_page_module.all_users")) 
    
    else:
        db.session.delete(user)
        db.session.commit()        
        
        flash(f'User {user.name} - {user.username} successfully deleted.', 'success')
        
        return redirect(url_for("main_page_module.all_users")) 
    

# Set the route and accepted methods
@main_page_module.route('/login/', methods=['GET', 'POST'])
def login():

    # If sign in form is submitted
    form = LoginForm(request.form)

    # Verify the sign in form
    if form.validate_on_submit():

        user = User.query.filter_by(username=form.username_or_email.data).first()
        if not user:
            user = User.query.filter_by(email=form.username_or_email.data).first()

        if user and user.check_password(form.password.data):

            session['user_id'] = user.id
            
            #set permanent login, if selected
            if form.remember.data == True:
                session.permanent = True

            flash('Welcome %s' % user.name, 'success')
            
            return redirect(url_for('main_page_module.index'))

        flash('Wrong email or password', 'error')
    
    try:
        if(session['user_id']):
            return redirect(url_for("main_page_module.index"))
    
    except:
        return render_template("main_page_module/auth/login.html", form=form)

@main_page_module.route('/logout/')
def logout():
    session.pop("user_id", None)
    session.permanent = False
    
    flash('You have been logged out. Have a nice day!', 'success')

    return redirect(url_for("main_page_module.login"))

# Set the route and accepted methods
@main_page_module.route('/register/', methods=['GET', 'POST'])
def register():
    #insert check, if the user is already logged in
    form = RegisterForm(request.form)

    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password = form.password.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        flash('Congratulations, you are now a registered user!', 'success')
        
        return redirect(url_for('main_page_module.login'))
    return render_template('main_page_module/auth/register.html', title='Register', form=form)