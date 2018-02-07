"""Utility file to seed ratings database from data in seed_data/"""

from sqlalchemy import func
from model import *


# from model import connect_to_db, db
from server import app

from datetime import datetime, date 


def load_ethnicitys():
    """Pre-load ethnicity"""

    Ethnicity.query.delete()

    for row in open("seed_data/ethnicity.txt"):
        row = row.rstrip()
        db.session.add(Ethnicity(ethnicity_name=row))
    
    db.session.commit()


def load_religions():
    """Pre-load religion"""

    Religion.query.delete()

    for row in open("seed_data/religion.txt"):
        row = row.rstrip()
        db.session.add(Religion(religion_name=row))
    
    db.session.commit()

def load_interests():
    """Pre-load interests"""

    Interest.query.delete()

    for row in open("seed_data/interest.txt"):
        row = row.rstrip()
        db.session.add(Interest(interest_name=row))
    
    db.session.commit()


def load_users():
    """Load users from user.txt into database."""

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    User.query.delete()
    PersonalInfo.query.delete()
    ContactInfo.query.delete()
    ProfessionalInfo.query.delete()


    # Read user file and insert data
    for row in open("seed_data/user.txt"):
        row = row.rstrip()
        uid, email, password, fname, lname, dob, height, gender, ethnicity, religion,\
        address, city, zipcode, phone, emp, _, __, aboutme  = row.split("|")

        dob_t = datetime.strptime(dob, '%Y-%m-%d') # convert this to datetime.date , not datetime.datetime 

        # user = User(user_id=uid, email=email, password=password, fname=fname, lname=lname,
        #             dob=dob_t, height=height, gender=gender, ethnicity=ethnicity,religion=religion,
        #             age=age, address=address, city=city, zipcode=zipcode, phone=phone,
        #             employer=emp, aboutme=aboutme)

        user = User(user_id=uid, email=email, password=password, fname=fname, lname=lname)

        personal = PersonalInfo(user_id=uid, dob=dob_t, height=height, gender=gender, 
                                ethnicity_id=ethnicity, religion_id=religion, aboutme=aboutme)

        contact = ContactInfo(user_id=uid, street_address=address, city=city, zipcode=zipcode, phone=phone)

        professional = ProfessionalInfo(user_id=uid, employer=emp)


        # We need to add to the session or it won't ever be stored
        db.session.add(user)
        db.session.add(personal)
        db.session.add(contact)
        db.session.add(professional)

    # Once we're done, we should commit our work
    db.session.commit()



def set_val_user_id():
    """Set value for the next user_id after seeding database"""

    # Get the Max user_id in the database
    result = db.session.query(func.max(User.user_id)).one()
    max_id = int(result[0])

    # We dont need it for movies here bcoz we are not adding new movies
    # We dont need it for ratings because we are not over-writing the PK there

    # Set the value for the next user_id to be max_id + 1
    query = "SELECT setval('users_user_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    #load_ethnicitys()
    #load_religions()
    load_interests()
   # load_users()
    set_val_user_id()
