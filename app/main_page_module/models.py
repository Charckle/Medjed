# Import the database object (db) from the main application module
from app import db

# Import password / encryption helper tools
from werkzeug import check_password_hash, generate_password_hash

# Define a base model for other database tables to inherit
class Base(db.Model):

    __abstract__  = True

    id = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())

# Define a User model
class User(Base):

    __tablename__ = 'users_table'

    # User Name
    name    = db.Column(db.String(128),  nullable=False)
    
    # UserName
    username    = db.Column(db.String(128),  nullable=False,
                            unique=True)    

    # Identification Data: email & password
    email    = db.Column(db.String(128),  nullable=False,
                         unique=True)
    password = db.Column(db.String(192),  nullable=False)

    # Authorisation Data: role & status
    role     = db.Column(db.SmallInteger, nullable=False)
    status   = db.Column(db.SmallInteger, nullable=False)
    

    # New instance instantiation procedure
    def __init__(self, username, email, password):

        self.name     = username
        self.username = username
        self.email    = email
        self.password = password
        self.role = 0
        self.status = 1

    def __repr__(self):
        return '<User %r>' % (self.name)
    
    def set_password(self, password):
            self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password) 

# Define a User model
class App(Base):

    __tablename__ = 'application_table'

    # app id
    app_id    = db.Column(db.String(128),  nullable=False,
                            unique=True)
    # app name
    app_name    = db.Column(db.String(128),  nullable=False)     
    
    # app author
    app_author    = db.Column(db.String(128),  nullable=False)    

    # app maintainer
    app_maintainer    = db.Column(db.String(128),  nullable=True)
                                  
    # app category
    app_category    = db.Column(db.String(128),  nullable=False)
    
    # app license
    app_license    = db.Column(db.String(128),  nullable=False)
    
    # app description
    app_description    = db.Column(db.String(500),  nullable=False)
    
    # app source
    app_source    = db.Column(db.String(128),  nullable=True)    

    # New instance instantiation procedure
    def __init__(self, app_id, app_name, app_author, app_maintainer, app_category, app_license, app_description, app_source):

        self.app_id     = app_id
        self.app_name = app_name
        self.app_author    = app_author
        self.app_maintainer = app_maintainer
        self.app_category = app_category
        self.app_license = app_license
        self.app_description = app_description
        self.app_source = app_source     

    def __repr__(self):
        return '<User %r>' % (self.app_name)
    
    