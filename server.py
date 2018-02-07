from flask import Flask, redirect, url_for, session, request, render_template, flash
from flask_oauth import OAuth
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined

from model import *

import facebook
import requests
import json

from pyzipcode import ZipCodeDatabase
from datetime import datetime, date

from werkzeug.utils import secure_filename
import os

from pytz import timezone


SECRET_KEY = 'development key'
DEBUG = True

app = Flask(__name__)
app.debug = DEBUG
app.secret_key = SECRET_KEY

app.jinja_env.undefined = StrictUndefined

# I added the following config otherwise, everytime the redirect was giving warning
# Dont put this in app.config in model.py (db connect) because that has sql alchemy related params only
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# These are for file uploading
UPLOAD_FOLDER = 'static/profile_pictures/'  #dont use /static, otherwise it will take to root
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif']) # took out 'txt', 'pdf'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# oauth = OAuth()
# FACEBOOK_APP_ID = '1616471035080729'
# FACEBOOK_APP_SECRET = 'c8361be5b9f39436dd6aa1442181fde6'


#Helper functions

def allowed_file(filename):
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def calc_age():

    today = date.today()
    age = today.year - dob_t.year - ((today.month, today.day) < (dob_t.month, dob_t.day))
    # dob_t = datetime.strptime(dob, '%Y-%m-%d')

#def some_function():

    # Getting PST time-stamp, will be used later
        #ca = timezone('US/Pacific')

        #print datetime.now(ca).strftime('%Y-%m-%d %H:%M:%S')
        #print str(datetime.now(ca))

        # Select * from Users where zip_code IN (19125,19081,19107.........);

# Routes 

@app.route('/')
def welcome():
    """Homepage."""

    return render_template("welcome-page.html")



@app.route('/register')
def display_registration_form():
    """Displays registartion form"""

    return render_template("registration-form.html")



@app.route('/register', methods=["POST"])
def handle_registration_form():
    """Registration form post handler"""

    email = request.form.get('email')
    password = request.form.get('password')
    fname = request.form.get('fname')
    lname = request.form.get('lname')

    user_exists = User.query.filter_by(email=email).first()
    if user_exists:
        flash('User already exists. Please register with another email address.')
        return redirect(request.url)
    else:
        new_user = User(email=email, password=password, fname=fname, lname=lname)
        db.session.add(new_user)
        db.session.commit()
        flash('WELCOME! You are successfully added to the database.')
        uid = User.query.filter_by(email=email).one().user_id  # should we immediately query the userid?
        ethnicities = Ethnicity.query.all()
        religions = Religion.query.all()
        interests = Interest.query.all()
        return render_template("continue-register.html", ethnicities=ethnicities, religions=religions, 
                                                          interests=interests, user_id=uid)


@app.route('/continue-register', methods=["POST"])
def display_continue_registration_form():


    if 'pic' not in request.files:
        flash('No picture uploaded')
        return redirect(request.url)  #request.url takes us back to requesting url
    file = request.files['pic']
        # if user does not select file, browser also
        # submit a empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_url = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        file.save(file_url)
        #return redirect(url_for('zip'))  # url_for takes the name of function of route

        user_id = request.form.get('user_id')

        dob = request.form.get('dob')
        height = request.form.get('height')
        gender = request.form.get('gender')
        ethnicity_id = request.form.get('ethnicity')
        religion_id = request.form.get('religion')
        aboutme = request.form.get('aboutme')

        address = request.form.get('address')
        city = request.form.get('city')
        zipcode = request.form.get('zipcode')
        phone = request.form.get('phone')

        employer = request.form.get('employer')
        occupation = request.form.get('occupation')
        education = request.form.get('education')
        
        interest_ids =request.form.getlist('interests')

        personal = PersonalInfo(user_id=user_id, dob=dob, height=height, gender=gender,
                     ethnicity_id=ethnicity_id, religion_id=religion_id, aboutme=aboutme)
        contact = ContactInfo(user_id=user_id, street_address=address, city=city, zipcode=zipcode, phone=phone)
        professional = ProfessionalInfo(user_id=user_id, employer=employer, occupation=occupation, education=education)
        picture = Picture(user_id=user_id, picture_url=str(file_url))

        for interest_id in interest_ids:
            idi = UserInterest(user_id=user_id, interest_id=interest_id)
            db.session.add(idi)

        db.session.add(personal)
        db.session.add(contact)
        db.session.add(professional)
        db.session.add(picture)

        db.session.commit()
        flash("ThankYou for completing the registraion. Please continue to Login")
        return redirect("/")


# @app.route('/login')
    

@app.route('/zip-codes')
def zip():
    """Shows all zipcodes near you"""

    zcdb = ZipCodeDatabase()
    in_radius = [z.zip for z in zcdb.get_zipcodes_around_radius('95134', 8)]
    return render_template("zip.html",zipcodes=in_radius)



if __name__ == '__main__':
    # app.run()
    app.debug = True

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    app.run(host="0.0.0.0")

