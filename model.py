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

    # one-user-to-one-user
    personal = db.relationship("PersonalInfo", uselist=False, backref="user")
    contact = db.relationship("ContactInfo", uselist=False, backref="user")
    professional = db.relationship("ProfessionalInfo", uselist=False, backref="user")

    # many-users-to-many-interests
    # We define the relationship here because we don wanna define it in association table
    interests = db.relationship("Interest", secondary="users_interests", backref="users")

    #one-user-to-many-pictures
    pictures = db.relationship("Picture", backref="user")
   
    def __repr__(self):
        """Provide helpful representation when printed"""

        return "<User user_id={} Name ={} {} email={}>".format(self.user_id, self.fname, self.lname, self.email)


class PersonalInfo(db.Model):
    """Personal Details"""

    __tablename__ = "personal_infos"

    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True) #one-to-one
    dob = db.Column(db.DateTime, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    ethnicity_id = db.Column(db.Integer, db.ForeignKey('ethnicities.ethnicity_id'))
    religion_id = db.Column(db.Integer, db.ForeignKey('religions.religion_id'))
    aboutme = db.Column(db.String(100), nullable=True) # See how to change it to min characters required


    #many-users-to-one-ethnicity
    ethnicity = db.relationship("Ethnicity", backref="users")

    #many-users-to-one-religion
    religion = db.relationship("Religion", backref="users")


class ContactInfo(db.Model):  
    """Contact Information"""  

    __tablename__ = "contact_infos"

    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True) #one-to-one
    street_address = db.Column(db.String(80), nullable=True)
    city = db.Column(db.String(64), nullable=False)
    zipcode = db.Column(db.Integer, nullable=False)
    phone = db.Column(db.String(64), nullable=False)


class ProfessionalInfo(db.Model):
    """Professional details"""

    __tablename__ = "professional_infos"

    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True) #one-to-one
    employer = db.Column(db.String(64), nullable=True)
    occupation = db.Column(db.String(64), nullable=True)
    education = db.Column(db.String(64), nullable=True)
    

# One user can have many pictures one-to-many
class Picture(db.Model):

    __tablename__ = "pictures"

    picture_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.user_id'))
    picture_url = db.Column(db.String(100), nullable=False) 


# A user can have many interests , and one interest can belong to many users
# Hence there is many-to-many relation here, so we need an association table
class UserInterest(db.Model):

    __tablename__ = "users_interests"

    user_interest_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.user_id'), nullable=False)
    interest_id = db.Column(db.Integer,db.ForeignKey('interests.interest_id'), nullable=False)


class Interest(db.Model):
    """Pre-defined Interests"""

    __tablename__ = "interests"

    interest_id = db.Column(db.Integer, autoincrement=True, primary_key=True)   
    interest_name = db.Column(db.String(64), nullable=False) 


class Religion(db.Model):     
    """Pre-defined Religions"""  

    __tablename__ = "religions"       

    religion_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    religion_name = db.Column(db.String(64), nullable=False)    


class Ethnicity(db.Model):     
    """Pre-defined Ethnicities"""    

    __tablename__ = "ethnicities"       

    ethnicity_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    ethnicity_name = db.Column(db.String(64), nullable=False)   



# middle table between two users (think of users as a duplicate)
class RelationManager(db.Model):
    """Manage connection between two users"""

    __tablename__ = "relations"

    management_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    source_userid = db.Column(db.ForeignKey('users.user_id'), nullable=False)  
    target_userid = db.Column(db.ForeignKey('users.user_id'), nullable=False) 
    timestamp = db.Column(db.DateTime, nullable=False) 
    status = db.Column(db.String(20), nullable=False)

    source_user = db.relationship("User", backref="relations_s", 
                                   primaryjoin="RelationManager.source_userid==User.user_id") 
    target_user = db.relationship("User", backref="relations_t",
                                   primaryjoin="RelationManager.target_userid==User.user_id")


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