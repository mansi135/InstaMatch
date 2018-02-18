from flask import Flask, redirect, url_for, session, request, render_template, flash, g, jsonify, send_from_directory
from flask_oauth import OAuth
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined

from model import *

import facebook
import requests
import json, os

from pyzipcode import ZipCodeDatabase
from datetime import datetime, date, timedelta
from pprint import pprint

from pytz import timezone

from functools import wraps

import relations

from sqlalchemy import desc, case

import googlemaps

from helper import *

SECRET_KEY = 'development key'
DEBUG = True

app = Flask(__name__)
app.debug = DEBUG
app.secret_key = SECRET_KEY

app.jinja_env.undefined = StrictUndefined


GOOGLE_MAPS_API_KEY = os.environ['GOOGLE_MAPS_API_KEY']
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

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





# Using login-decorator - for login authentication
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first')
            return redirect(url_for('show_login_form'))
    return wrap


@app.before_request
def do_this_before_every_request():
    """Get info about currently logged-in user"""

    g.user_id = session.get('user_id')

    if g.user_id != None:
        g.current_user = (User.query.options(db.joinedload('personal'))
                  .options(db.joinedload('contact')) 
                  .options(db.joinedload('professional')) 
                  .options(db.joinedload('interests')) 
                  .options(db.joinedload('pictures')).get(g.user_id))
    else:
        g.current_user = None



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
        #session['logged_in'] = True

        return redirect('/continue-register')
        
# This route should not be visible until initial registrtion has started
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
            filename = "MyDbPics" + str(pic_id+1) + ".jpg"

        file_url = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        # file_url = os.path.join(app.config['UPLOAD_FOLDER'])

        file.save(file_url)
        flash('Photo saved')
        #return redirect(url_for('zip'))  # url_for takes the name of function of route
        #return redirect(url_for('uploaded_file', filename=filename))

        #user_id = session.get('user_id')
        user_id = g.user_id
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
        picture = Picture(user_id=user_id, picture_url=str(filename))

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

    try:
        existing_user = User.query.filter_by(email=email, password=password).one()
    except:
        flash("The email or password you have entered did not match our records. Please try again.", "danger")
        return redirect(request.url)

    flash("Welcome {} You are successfully logged in.".format(existing_user.fname))
    session['user_id'] = existing_user.user_id
    session['logged_in'] = True
    session['fname'] = existing_user.fname # Not-needed..remove it ?
    return redirect('/my-homepage')



@app.route('/my-homepage/')
@login_required
def individual_home_page():
    """Display user home page"""

    ethnicities = Ethnicity.query.all()
    religions = Religion.query.all()
    new_requests = RelationManager.query.filter_by(target_userid=g.user_id, seen_by_target='not-seen').count()
    new_responses = RelationManager.query.filter_by(source_userid=g.user_id, seen_by_source='not-seen').count()
    new_messages = Message.query.filter_by(to_id=g.user_id,seen=False).count()

    return render_template("my-homepage.html", ethnicities=ethnicities, religions=religions,
                                               new_requests=new_requests, new_responses=new_responses,
                                               new_messages=new_messages)


    
@app.route('/users/<int:user_id>')
@login_required
def show_profile_page(user_id):
    """Show user-profile page"""

    contact_type = request.args.get('type')
    status = request.args.get('status')

    if user_id == g.user_id:
        status = None

    user = User.query.options(db.joinedload('personal')) \
                  .options(db.joinedload('contact')) \
                  .options(db.joinedload('professional')) \
                  .options(db.joinedload('interests')) \
                  .options(db.joinedload('pictures')).get(user_id)

    user.personal.dob = user.personal.dob.strftime('%Y-%m-%d')

    # BOZO - make this loop when user has more than one picture 
    pic_url = os.path.join(app.config['UPLOAD_FOLDER'],user.pictures[0].picture_url)

    return render_template("profile-page.html", user=user, pic_url=pic_url, contacttype=contact_type, status=status)


@app.route('/search')
@login_required
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

    # Age 
    # matching_users = (db.session.query(User).join(PersonalInfo)
    #                 .filter(PersonalInfo.dob > min_dob, 
    #                         PersonalInfo.dob < max_dob, 
    #                         PersonalInfo.religion_id==religion_id, 
    #                         PersonalInfo.ethnicity_id==ethnicity_id, 
    #                         PersonalInfo.gender==gender) 
    #                 .all())

    # Height
    # matching_users = (db.session.query(User).options(db.joinedload('personal'))
    #                            .options(db.joinedload('contact')) 
    #                            .options(db.joinedload('professional')) 
    #                            .options(db.joinedload('interests')) 
    #                            .options(db.joinedload('pictures'))
    #                            .join(PersonalInfo)
    #                            .filter(PersonalInfo.height > min_height,
    #                                     PersonalInfo.height < max_height)
    #                   .all())

    # search by location

    #u = User.query.get(session.get('user_id'))

    z = get_zip_near_me(g.current_user.contact.zipcode, int(distance.split(" ")[0]))

    received_ids = db.session.query(RelationManager.source_userid).filter_by(target_userid=g.user_id).all()
    sent_ids = db.session.query(RelationManager.target_userid).filter_by(source_userid=g.user_id).all()
    
    matching_users = (db.session.query(User, db.func.concat(UPLOAD_FOLDER,Picture.picture_url))
                                   .options(db.joinedload('personal'))
                                   .options(db.joinedload('contact')) 
                                   .options(db.joinedload('professional')) 
                                   .options(db.joinedload('interests')) 
                                   .options(db.joinedload('pictures'))
                                   .join(ContactInfo)
                                   .join(Picture)
                                   .filter(ContactInfo.zipcode.in_(z), 
                                            User.user_id != g.user_id,
                                            ~User.user_id.in_(sent_ids),
                                            ~User.user_id.in_(received_ids))
                          .all())

    # Attach real path to all pictures
    # for user in matching_users:
    #     for pic in user.pictures:
    #         pic.picture_url = os.path.join(app.config['UPLOAD_FOLDER'],pic.picture_url)

    


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

# Ajax route
@app.route('/send-request.json', methods=['POST'])
@login_required
def send_request():

    target_userid = request.form.get('target_userid')
    timestamp = request.form.get('timestamp')
    timestamp = datetime.strptime(timestamp.split("-")[0], "%a %b %d %Y %H:%M:%S %Z")
    new_connection = RelationManager(source_userid=g.user_id, target_userid=target_userid, 
                                    timestamp=timestamp, status="Pending", seen_by_target='not-seen')
    db.session.add(new_connection)
    db.session.commit()

    return jsonify({'response': 'Requested', 'uid': target_userid})



@app.route('/my-homepage/requests-received')
@login_required
def show_received_requests_and_update_target_seen():
    """Show received requests"""

    # Update target_seen in database
    new_requests = RelationManager.query.filter_by(target_userid=g.user_id, seen_by_target='not-seen').all()

    for new_request in new_requests:
        new_request.seen_by_target = 'seen'
    db.session.commit()


    received_from_list = RelationManager.query.filter_by(target_userid=g.user_id).order_by(desc('timestamp')).all()
    
    # fix for pic loop ? May be not- coz in results I show only 1-pic

    return render_template("requests-received.html", received_from_list=received_from_list, UPLOAD_FOLDER=UPLOAD_FOLDER)


@app.route('/my-homepage/requests-sent')
@login_required
def show_sent_requests_and_update_source_seen():
    """Show sent requests"""
    
    new_responses = RelationManager.query.filter_by(source_userid=g.user_id, seen_by_source='not-seen').all()

    for new_response in new_responses:
        new_response.seen_by_source = 'seen'
    db.session.commit()


    sent_to_list = RelationManager.query.filter_by(source_userid=g.user_id).order_by(desc('timestamp')).all()
      
    # fix for pic loop
   
    return render_template("requests-sent.html", sent_to_list=sent_to_list, UPLOAD_FOLDER=UPLOAD_FOLDER)


# Ajax route
@app.route('/accept-pass-request.json', methods=['POST'])
@login_required
def accept_or_pass_request():

    source_userid = request.form.get('source_userid')
    timestamp = request.form.get('timestamp')
    timestamp = datetime.strptime(timestamp.split("-")[0], "%a %b %d %Y %H:%M:%S %Z")
    action = request.form.get('action')
    c = RelationManager.query.filter_by(source_userid=source_userid, target_userid=g.user_id).one()

    if action == 'accept':
        c.status = "Accepted"
        c.timestamp = timestamp
        c.seen_by_source = 'not-seen'
        db.session.commit()
        return jsonify({'response': "Congrats! You have accepted {}'s request".format(c.source_user.fname), 
                        'uid': source_userid, 'status': "Accepted"})

    elif action == 'pass':
        c.status = "Passed"
        c.timestamp = timestamp
        c.seen_by_source = 'not-seen'
        db.session.commit()
        return jsonify({'response': "You passed {}'s request..Continue searching..".format(c.source_user.fname), 
                        'uid': source_userid, 'status': "Passed"})


@app.route('/my-homepage/requests-accepted')
@login_required
def show_map():

    # geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')
    sent_accepted = (RelationManager.query.filter_by(source_userid=g.user_id, status='Accepted')
                                         .order_by(desc('timestamp')).all())
    received_accepted = (RelationManager.query.filter_by(target_userid=g.user_id, status='Accepted')
                                         .order_by(desc('timestamp')).all())
    
    # zip1 = []

    # for a in sent_accepted:
    #     zip1.append(a.target_user.contact.zipcode)

    # for a in received_accepted:
    #     zip1.append(a.source_user.contact.zipcode)

    # zip1.append(g.current_user.contact.zipcode)

    # lat_lng = []

    # for z in zip1:
    #     geocode_result = gmaps.geocode(z)
    #     lat_lng.append(geocode_result[0]['geometry']['location'])
    # pprint(geocode_result)

    return render_template("requests-accepted.html", GOOGLE_MAPS_API_KEY=GOOGLE_MAPS_API_KEY, 
                                    UPLOAD_FOLDER=UPLOAD_FOLDER, sent_accepted=sent_accepted, received_accepted=received_accepted,
                                    current_user=g.current_user)


#AJAX route
@app.route('/send-message', methods=['POST'])
@login_required
def send_message():

    
    to_id = request.form.get('to_id')
    message = request.form.get('text')
    timestamp = request.form.get('timestamp')

    timestamp = datetime.strptime(timestamp.split("-")[0], "%a %b %d %Y %H:%M:%S %Z")
    new_message = Message(from_id=g.user_id, to_id=to_id, message=message,
                                    timestamp=timestamp, seen=False)
    db.session.add(new_message)
    db.session.commit()

    return "OK"

@app.route('/my-homepage/messages')
@login_required
def show_messages():

    new_messages = Message.query.filter_by(to_id=g.user_id, seen=False).all()

    for new_message in new_messages:
        new_message.seen = True
    db.session.commit()


    latest_messages = get_latest_messages(db, g.user_id);
    user_list = []

    for message in latest_messages:     # returns a tuple of (id, msg, timestamp)
        user_list.append((User.query.get(message[0]), message))


    messages_list = Message.query.filter_by(to_id=g.user_id).order_by(desc('timestamp')).all()
      

    # fix for pic loop
   
    return render_template("messages.html", messages_list=messages_list, user_list=user_list, UPLOAD_FOLDER=UPLOAD_FOLDER)




@app.route('/logout')
def logout():
    """Logout User"""

    #del session['user_id']
    session.clear()
    flash("You were logged out.")

    return redirect("/")



if __name__ == '__main__':
    # app.run()
    app.debug = True

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    app.run(host="0.0.0.0")

