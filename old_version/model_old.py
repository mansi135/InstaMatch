"""This is tables file for all"""

from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy.dialects import postgresql

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User Registration form data."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(64), nullable=False)
    fname = db.Column(db.String(64), nullable=False)
    lname = db.Column(db.String(64), nullable=False)
    

class PersonalDetails(db.Model):
    """Personal details"""

    dob = db.Column(db.DateTime, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    ethnicity = db.Column(db.String(64), nullable=False)
    religion = db.Column(db.String(64), nullable=False)
    #age = db.Column(db.Integer, nullable=False) # Remove this

    
    # Contact info                                           
    address = db.Column(db.String(80), nullable=True)
    city = db.Column(db.String(64), nullable=False)
    zipcode = db.Column(db.Integer, nullable=False)
    phone = db.Column(db.String(64), nullable=False)

    # Professional details
    employer = db.Column(db.String(64), nullable=True)
    occupation = db.Column(db.String(64), nullable=True)
    education = db.Column(db.String(64), nullable=True)

    aboutme = db.Column(db.String(100), nullable=True) # See how to change it to min characters required

    

    def __repr__(self):
        """Provide helpful representation when printed"""

        return "<User user_id={} Name ={} {} email={}>".format(self.user_id, self.fname, self.lname, self.email)


class Interest(db.Model):

    __tablename__ = "interests"

    interest_id = db.Column(db.Integer, autoincrement=True, primary_key=True)   # Every time user adds an interest,
    interest_name = db.Column(db.String(64), nullable=False)                    # a row will be created

    # We define the relationship here because we don wanna define it in association table
    users = db.relationship("User", secondary="users_interests", backref="interests")



# A user can have many interests , and one interest can belong to many users
# Hence there is many-to-many relation here, so we need an association table
class UserInterest(db.Model):

    __tablename__ = "users_interests"

    user_interest_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.user_id'), nullable=False)
    interest_id = db.Column(db.Integer,db.ForeignKey('interests.interest_id'), nullable=False)


# One user can have many pictures
class Picture(db.Model):

    __tablename__ = "pictures"

    picture_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.user_id'))
    picture_location = db.Column(db.String(80), nullable=False) 

    user = db.relationship("User", backref="pictures")


# middle table between two users (think of users as a duplicate)
class RelationsManager(db.Model):

    __tablename__ = "relations_manager"


    management_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    source_userid = db.Column(db.Integer, nullable=False)  # make it FK
    target_userid = db.Column(db.Integer, nullable=False) # make it FK
    timestamp = db.Column(db.String(64), nullable=False) # make this Datetime
    status = db.Column(db.String(20), nullable=False)



##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///datings'
    app.config['SQLALCHEMY_ECHO'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
    db.create_all()