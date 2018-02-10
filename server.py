from flask import Flask, redirect, url_for, session, request, render_template, flash, g
from flask_oauth import OAuth
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined

from model import *

import facebook
import requests
import json

from pyzipcode import ZipCodeDatabase
from datetime import datetime, date, timedelta

from werkzeug.utils import secure_filename
import os

from pytz import timezone

from flask import send_from_directory



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

# Note- url is the route name and url_for is the view func name . html page name is never seen directly
#Helper functions

def allowed_file(filename):
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def calc_age(dob):

    today = date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return age
    # dob_t = datetime.strptime(dob, '%Y-%m-%d')


def get_zip_near_me(myzip, miles):
    """Shows all zipcodes near you"""

    zcdb = ZipCodeDatabase()
    in_radius = [z.zip for z in zcdb.get_zipcodes_around_radius(myzip, miles)]
    return in_radius
    #return render_template("zip.html",zipcodes=in_radius)



#def some_function_for_timestamp():

    # Getting PST time-stamp, will be used later
        #ca = timezone('US/Pacific')

        #print datetime.now(ca).strftime('%Y-%m-%d %H:%M:%S')
        #print str(datetime.now(ca))

        # Select * from Users where zip_code IN (19125,19081,19107.........);

@app.before_request
def do_this_before_every_request():
    """maybe do this"""

    # query for then user
    # if 'user_id' in session
    # g.current_user = User.query.get(session.get('user_id'))
    # emps = User.query.options(db.joinedload('personal')).all()

    # User.query.options(db.joinedload('personal'))
    #           .options(db.joinedload('contact'))
    #           .options(db.joinedload('professional')).all()



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
        session['user_id'] = uid

        return redirect('/continue-register')
        

@app.route('/continue-register')
def display_continue_registration_form():
    """Complete Registration"""

    ethnicities = Ethnicity.query.all()
    religions = Religion.query.all()
    interests = Interest.query.all()
    return render_template("continue-register.html", ethnicities=ethnicities, 
                                        religions=religions, interests=interests)



@app.route('/continue-register', methods=["POST"])
def handle_continue_registration_form():


    if 'pic' not in request.files:
        flash('No picture uploaded')
        return redirect(request.url)  #request.url takes us back to requesting url, but we loose typed data ...how to save that ?
        #return redirect(url_for())
    file = request.files['pic']
        # if user does not select file, browser also
        # submit a empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        #filename = secure_filename(file.filename)  # Might not be needed

        pic_id = db.session.query(db.func.max(Picture.picture_id)).one()[0]

        if pic_id is None:
            filename = "MyDbPics"     # remove My_pic here
        else:
            filename = "MyDbPics" + str(pic_id) + ".jpg"

        #file_url = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        # file_url = os.path.join(app.config['UPLOAD_FOLDER'])

        file.save(filename)
        flash('Photo saved')
        #return redirect(url_for('zip'))  # url_for takes the name of function of route
        #return redirect(url_for('uploaded_file', filename=filename))

        user_id = session.get('user_id')

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
        session.clear()
        flash("ThankYou for completing the registraion. Please continue to Login")

        
        return redirect('/')



@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)


@app.route('/login')
def show_login_form():
    """Show login form"""

    return render_template("login-form.html")


@app.route('/login', methods=['POST'])
def login_check():
    """Login check"""

    email = request.form.get('email')
    password = request.form.get('password')

    existing_user = User.query.filter_by(email=email).first()


    if not existing_user:
        flash('Email not found.')
        print request.url
        return redirect(request.url)
    elif existing_user.email == email and existing_user.password != password:
        flash('The password is incorrect. Please try again.')
        return redirect(request.url)
    elif existing_user.email == email and existing_user.password == password:
        flash("Welcome {} You are successfully logged in.".format(existing_user.fname))
        # probably bug here
        session['user_id'] = existing_user.user_id
        session['fname'] = existing_user.fname

        #return redirect("/{}".format(existing_user.user_id))
        return redirect('/my-homepage')
        #return redirect("/")



#@app.route('/<user_id>') #-dont do it, otherwise we will see things like /2, /3 in url
                         # hence its recommended to add a username

@app.route('/my-homepage/')
def individual_home_page():
    """Display user home page"""

    ethnicities = Ethnicity.query.all()
    religions = Religion.query.all()

    return render_template("my-homepage.html", ethnicities=ethnicities, religions=religions)


@app.route('/my-homepage/sent-requests')
def show_sent_requests():
    """Show sent requests"""

    return render_template("sent-requests.html")

@app.route('/my-homepage/received-requests')
def show_received_requests():
    """Show received requests"""

    return render_template("received-requests.html")

    
@app.route('/users/<user_id>')
def show_profile_page(user_id):
    """Show user-profile page"""

    user = User.query.options(db.joinedload('personal')) \
                  .options(db.joinedload('contact')) \
                  .options(db.joinedload('professional')) \
                  .options(db.joinedload('interests')) \
                  .options(db.joinedload('pictures')).get(user_id)

    user.personal.dob = user.personal.dob.strftime('%Y-%m-%d')

    # BOZO - make this loop when user has more than one picture 
    pic_url = os.path.join(app.config['UPLOAD_FOLDER'],user.pictures[0].picture_url)

    print pic_url
    return render_template("profile-page.html", user=user, pic_url=pic_url)


@app.route('/search')
def search():

    age = request.args.get('age')
    height = request.args.get('height')
    religion_id = request.args.get('religion')
    ethnicity_id = request.args.get('ethnicity')
    gender = request.args.get('gender')
    distance = request.args.get('distance')

    min_age, max_age = map(int, age.split('-'))
    min_height, max_height = map(int, height.split('-'))

    max_dob = datetime.now()-timedelta(days=min_age*365)
    min_dob = datetime.now()-timedelta(days=max_age*365)

    # Make different types of queries
    # matching_users = (db.session.query(User).join(PersonalInfo)
    #                 .filter(PersonalInfo.dob > min_dob, 
    #                         PersonalInfo.dob < max_dob, 
    #                         PersonalInfo.religion_id==religion_id, 
    #                         PersonalInfo.ethnicity_id==ethnicity_id, 
    #                         PersonalInfo.gender==gender) 
    #                 .all())

    matching_users = (db.session.query(User).options(db.joinedload('personal'))
                               .options(db.joinedload('contact')) 
                               .options(db.joinedload('professional')) 
                               .options(db.joinedload('interests')) 
                               .options(db.joinedload('pictures'))
                               .join(PersonalInfo)
                               .filter(PersonalInfo.height > min_height,
                                        PersonalInfo.height < max_height)
                      .all())

    for user in matching_users:
        for pic in user.pictures:
            pic.picture_url = os.path.join(app.config['UPLOAD_FOLDER'],pic.picture_url)

    u = User.query.get(session.get('user_id'))
    print get_zip_near_me(95134, int(distance.split(" ")[0]))

    # search by location

    # eagerly get all users
    # q = (db.session.query(User).options(db.joinedload('personal'))
    #                            .options(db.joinedload('contact')) 
    #                            .options(db.joinedload('professional')) 
    #                            .options(db.joinedload('interests')) 
    #                            .options(db.joinedload('pictures'))
    #                            .join(PersonalInfo)
    #                 .filter(PersonalInfo.dob > min_dob, 
    #                         PersonalInfo.dob < max_dob, 
    #                         PersonalInfo.religion_id==religion_id, 
    #                         PersonalInfo.ethnicity_id==ethnicity_id, 
    #                         PersonalInfo.gender==gender) 
    #                 .all())

    return render_template("show-search-results.html", matching_users=matching_users)





if __name__ == '__main__':
    # app.run()
    app.debug = True

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    app.run(host="0.0.0.0")
