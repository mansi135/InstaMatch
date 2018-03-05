from flask import Flask, redirect, url_for, session, request, render_template, flash, g, jsonify, send_from_directory
from flask_oauth import OAuth
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined, Template

from model import *
from helper import *

import facebook, googlemaps
import requests, shutil
import json, os

from datetime import datetime, date, timedelta
from pprint import pprint

from functools import wraps

import relations

from sqlalchemy import desc, case




SECRET_KEY = 'development key'
DEBUG = True

app = Flask(__name__)
app.debug = DEBUG
app.secret_key = SECRET_KEY

app.jinja_env.undefined = StrictUndefined


GOOGLE_MAPS_API_KEY = os.environ['GOOGLE_MAPS_API_KEY']
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

FACEBOOK_APP_ID = os.environ['FACEBOOK_APP_ID']
FACEBOOK_APP_SECRET = os.environ['FACEBOOK_APP_SECRET']


# I added the following config otherwise, everytime the redirect was giving warning
# Dont put this in app.config in model.py (db connect) because that has sql alchemy related params only
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# These are for file uploading
UPLOAD_FOLDER = 'static/profile_pictures/'  #dont use /static, otherwise it will take to root
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif']) # took out 'txt', 'pdf'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



# Note- url is the route name and url_for is the view func name . html page name is never seen directly
#Helper functions

def allowed_file(filename):
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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


# Not needed since i made modal window
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
        # flash('User already exists. Please register with another email address.')
        # return redirect(request.url)
        return jsonify({'msg': "User already exists. Please register with another email address.", 'status': "notOK"})

    else:
        new_user = User(email=email, password=password, fname=fname, lname=lname)
        db.session.add(new_user)
        db.session.commit()
        
        #flash('WELCOME! You are successfully added to the database.')
        uid = User.query.filter_by(email=email).one().user_id  # should we immediately query the userid?
        session['user_id'] = uid
        #session['logged_in'] = True

        # return redirect('/continue-register')

        return jsonify({'msg': "You are successfully added to the database.", 'status': "OK"})
        

# This route should not be visible until initial registrtion has started
@app.route('/continue-register')
def display_continue_registration_form():
    """Complete Registration"""

    # It should not extend from base ...
    ethnicities = Ethnicity.query.all()
    religions = Religion.query.all()
    interests = Interest.query.all()

    session['img'] = None # Initially there will be no session , so just make it null (its a hacky way!!)
    session['fname'] = None
    return render_template("continue-register.html", ethnicities=ethnicities, 
                                        religions=religions, interests=interests)



@app.route('/continue-register', methods=["POST"])
def handle_continue_registration_form():

    user_id = g.user_id
    dob = request.form.get('dob')
    height = request.form.get('height')
    gender = request.form.get('gender')
    ethnicity_id = request.form.get('ethnicity')
    religion_id = request.form.get('religion')
    aboutme = request.form.get('aboutme')
    smoke = request.form.get('smoke')
    drink = request.form.get('drink')
    current_rel = request.form.get('current_rel')
    kids = request.form.get('kids')


    address = request.form.get('address')
    city = request.form.get('city')
    state = request.form.get('state')
    zipcode = request.form.get('zipcode')
    phone = request.form.get('phone')

    employer = request.form.get('employer')
    occupation = request.form.get('occupation')
    education = request.form.get('education')
    
    interest_ids =request.form.getlist('interests')

    personal = PersonalInfo(user_id=user_id, dob=dob, height=height, gender=gender,
                 ethnicity_id=ethnicity_id, religion_id=religion_id, aboutme=aboutme,
                 drink=drink, smoke=smoke, current_rel_status=current_rel, kids=kids)
    contact = ContactInfo(user_id=user_id, street_address=address, city=city, state=state, zipcode=zipcode, phone=phone)
    professional = ProfessionalInfo(user_id=user_id, employer=employer, occupation=occupation, education=education)


    if 'pic' not in request.files:
        flash('No picture uploaded')
        return redirect(request.url)  #request.url takes us back to requesting url, but we loose typed data ...how to save that ?
        #return redirect(url_for())
    files = request.files.getlist('pic')
    print files
        # if user does not select file, browser also
        # submit a empty part without filename
        
    for file in files:
        print file
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        pic_id = db.session.query(db.func.max(Picture.picture_id)).one()[0]

        if file and allowed_file(file.filename):
            #filename = secure_filename(file.filename)  # Might not be needed

            if pic_id is None:
                filename = "MyDbPics"     # remove My_pic here
            else:
                filename = "MyDbPics" + str(pic_id+1) + ".jpg"

            file_url = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            file.save(file_url)

            picture = Picture(user_id=user_id, picture_url=str(filename))
            db.session.add(picture)
    flash('Photo saved')
        #return redirect(url_for('zip'))  # url_for takes the name of function of route
        #return redirect(url_for('uploaded_file', filename=filename))

        #user_id = session.get('user_id')
    
    # picture = Picture(user_id=user_id, picture_url=str(filename))

    for interest_id in interest_ids:
        idi = UserInterest(user_id=user_id, interest_id=interest_id)
        db.session.add(idi)

    db.session.add(personal)
    db.session.add(contact)
    db.session.add(professional)
    # db.session.add(picture)

    db.session.commit()
    session.clear()
    flash("ThankYou for completing the registration. Please continue to Login")

    
    return redirect('/')



@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)



@app.route('/login', methods=['POST'])
def login_check():
    """Login check"""

    email = request.form.get('email')
    password = request.form.get('password')

    try:
        existing_user = User.query.filter_by(email=email, password=password).one()
    except:
      #  flash("The email or password you have entered did not match our records. Please try again.", "danger")
      #  return redirect(request.url)
        return jsonify({'msg': "Email or Password is incorrect. Please try again!",'status': "NotOK"})

    flash("Welcome {} You are successfully logged in.".format(existing_user.fname))
    session['user_id'] = existing_user.user_id
    session['logged_in'] = True
    session['fname'] = existing_user.fname # Not-needed..remove it ?
    return jsonify({'msg': "Welcome {} You are successfully logged in.".format(existing_user.fname), 'status': "OK"})
    # return redirect('/my-homepage')


# check if he exists in db, login and => show his homepage !
# if he does not exists => add to db , show continue register

@app.route('/fb-login', methods=['POST'])
def facebook_login():
    """Check if the fb-email is present in my database"""

    token = request.form.get('token')
    session['token'] = token

    facebook_id = request.form.get('fb_id')
    email = request.form.get('email')


    # This is a working code for getting bytes of facebook photo : do it later
    # url = """https://graph.facebook.com/v2.11/me?fields=picture.type(large)&access_token={}""".format(token)
    # r = requests.get(url)
    # response = r.json()

    # print response
    # a = requests.get(response['picture']['data']['url'], stream=True)
    # if a.status_code == 200:
    #     with open('test.jpg', 'wb') as f:
    #         a.raw.decode_content = True
    #         shutil.copyfileobj(a.raw, f)
            


    try:
        existing_user = User.query.filter_by(email=email, password=facebook_id).one()
        session['user_id'] = existing_user.user_id
        session['logged_in'] = True
        session['fname'] = existing_user.fname 
        return "Existing_User"
    except:
        return "New_User"

    
@app.route('/fb-register', methods=['POST'])
def facebook_register():
    """Register New Facebook-User"""

    token = session['token']
    url = """https://graph.facebook.com/v2.11/me?fields=id,name,gender,email,locale,
            updated_time,verified,friends,picture.type(large),location,hometown,birthday,timezone&access_token={}""".format(token)
    r = requests.get(url)
    response = r.json()

    print response

    # url1 = """https://graph.facebook.com/v2.11/me/picture?type=normal&access_token={}""".format(token)

    # print requests.get(url1)

    facebook_id = response['id']
    fname = response['name'].split()[0]
    lname = response['name'].split()[1]
    gender = response['gender'][0].upper()
    email = response['email']
    pic_url = response['picture']['data']['url']
    # city = response['location']['name'].split(',')[0]
    # state = response['location']['name'].split(',')[1]
    # birthday = response['birthday']


    # session['user_id'] = 500

    new_user = User(email=email, password=facebook_id, fname=fname, lname=lname)
    db.session.add(new_user)
    db.session.commit()
    
    uid = User.query.filter_by(email=email).one().user_id  # should we immediately query the userid?
    session['user_id'] = uid

    return "ok"

    


@app.route('/my-homepage/')
@login_required
def individual_home_page():
    """Display user home page"""

    ethnicities = Ethnicity.query.all()
    religions = Religion.query.all()

    # Possible function - get new notifications
    new_requests = RelationManager.query.filter_by(target_userid=g.user_id, seen_by_target='not-seen').count()
    new_responses = RelationManager.query.filter_by(source_userid=g.user_id, seen_by_source='not-seen').count()
    new_messages = Message.query.filter_by(to_id=g.user_id,seen=False).count()

    session['new_requests'] = new_requests
    session['new_responses'] = new_responses
    session['new_messages'] = new_messages

    session['img'] = UPLOAD_FOLDER + g.current_user.pictures[0].picture_url

    my_age = calc_age(g.current_user.personal.dob)
    my_height = g.current_user.personal.height
    my_gender = g.current_user.personal.gender


    filter_criteria_for_female = {'min_age': my_age - 3,
                        'max_age': my_age + 15,
                        'min_height': my_height,
                        'max_height': my_height + 80,
                        'gender': 'M' }

    filter_criteria_for_male = {'min_age': my_age - 30,
                        'max_age': my_age + 5,
                        'min_height': my_height - 50,
                        'max_height': my_height + 10,
                        'gender': 'F' }

    if my_gender == 'F':
        filter_criteria = filter_criteria_for_female
    else:
        filter_criteria = filter_criteria_for_male
  
    return render_template("my-homepage.html", ethnicities=ethnicities, religions=religions,
                                               new_requests=new_requests, new_responses=new_responses,
                                               new_messages=new_messages, filter_criteria=filter_criteria)





@app.route('/potential-matches.json')
@login_required
def match():


    age = request.args.get('age')
    height = request.args.get('height')
    distance = request.args.get('distance')
    gender = request.args.get('gender')
    ethnicity_id = request.args.get('ethnicity')
    religion_id = request.args.get('religion')

    min_age, max_age = map(int, age.split('-'))
    min_height, max_height = map(int, height.split('-'))

    max_dob, min_dob = get_dob_range_from_age(min_age, max_age)

    z = get_zip_near_me(g.current_user.contact.zipcode, distance) 

    received_ids = db.session.query(RelationManager.source_userid).filter_by(target_userid=g.user_id).all()
    sent_ids = db.session.query(RelationManager.target_userid).filter_by(source_userid=g.user_id).all()
    
    #, db.func.concat(UPLOAD_FOLDER,Picture.picture_url)
    # A potentially harmless bug here ? Since User can have many pictures, we get repeated output with differnt pics
    # in helper function, this causes overwriting the same userid info till the last pic is reached
    # Hence we see differnt picture in home-page and differnt pic in profile page

    # Fix - Change the query to make Pictures as a list of all pictures...using groupby
    #db.func.array_agg(Picture.picture_url)
    # But then we cant use db.joinedload since grou_by errors, then we have to join all tables...we can do that ..
    # But somehow i was getting error with joining Favorite table
    matching_users = (db.session.query(User, PersonalInfo, ContactInfo, Picture)
                                   # .options(db.joinedload('personal'))
                                   # .options(db.joinedload('contact')) 
                                  .options(db.joinedload('professional'))        
                                  .options(db.joinedload('interests'))           
                                  .options(db.joinedload('favorites_t'))
                                  # .options(db.joinedload('ethnicity'))
                                  # .options(db.joinedload('religion'))
                                   # .options(db.joinedload('pictures'))
                                   .join(ContactInfo)
                                   .join(Picture)
                                   .join(PersonalInfo)
                                   .filter( ContactInfo.zipcode.in_(z),    
                                            User.user_id != g.user_id,
                                            ~User.user_id.in_(sent_ids),
                                            ~User.user_id.in_(received_ids))
                                   .filter(PersonalInfo.height > min_height, PersonalInfo.height < max_height,
                                            PersonalInfo.dob > min_dob, PersonalInfo.dob < max_dob,
                                            PersonalInfo.gender == gender)
                                   # .group_by(User, PersonalInfo, ContactInfo) # commented for demonstration purpose only
                          .all())

   

    # we pass the current user here to see if current user has favorited any of these users
    matched_users = get_users_info(matching_users, UPLOAD_FOLDER, g.user_id)
    # matched_users = get_users_info(matching_users, UPLOAD_FOLDER)

    return jsonify(matched_users)

    
@app.route('/users/<int:user_id>')
@login_required
def show_profile_page(user_id):
    """Show user-profile page"""
    

    ethnicities = Ethnicity.query.all()
    religions = Religion.query.all()
    interests = Interest.query.all()

    contact_type = request.args.get('type')  # type is not needed if status is not pending
    status = request.args.get('status')

    if user_id == g.user_id:
        status = 'self'

    user = User.query.options(db.joinedload('personal')) \
                  .options(db.joinedload('contact')) \
                  .options(db.joinedload('professional')) \
                  .options(db.joinedload('interests')) \
                  .options(db.joinedload('pictures')).get(user_id)

    # When we make function to get each user info, may be calculate age here itself?
    # Not possible because storing that is a pain
    # user.personal.dob = user.personal.dob.strftime('%Y-%m-%d')

    # BOZO - make this loop when user has more than one picture 
    #pic_url = os.path.join(app.config['UPLOAD_FOLDER'],user.pictures[0].picture_url)

    return render_template("profile-page.html", user=user, UPLOAD_FOLDER=UPLOAD_FOLDER, contacttype=contact_type, status=status,
                                                ethnicities=ethnicities, religions=religions, interests=interests)





# not needed ?
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

    # session['new_requests'] = new_requests

    for new_request in new_requests:
        new_request.seen_by_target = 'seen'
    db.session.commit()

    received_from_list = RelationManager.query.filter_by(target_userid=g.user_id).order_by(desc('timestamp')).all()
    
    # fix for pic loop ? May be not- coz in results I show only 1-pic. Only when the user clicks in profile , he can see all pics

    # return render_template("requests-received.html", received_from_list=received_from_list, UPLOAD_FOLDER=UPLOAD_FOLDER)
    return render_template("requests.html", list_to_render=received_from_list, UPLOAD_FOLDER=UPLOAD_FOLDER, method='received')


@app.route('/my-homepage/requests-sent')
@login_required
def show_sent_requests_and_update_source_seen():
    """Show sent requests"""
    
    new_responses = RelationManager.query.filter_by(source_userid=g.user_id, seen_by_source='not-seen').all()

    # session['new_responses'] = new_responses

    for new_response in new_responses:
        new_response.seen_by_source = 'seen'
    db.session.commit()


    sent_to_list = RelationManager.query.filter_by(source_userid=g.user_id).order_by(desc('timestamp')).all()
      
   
    # return render_template("requests-sent.html", sent_to_list=sent_to_list, UPLOAD_FOLDER=UPLOAD_FOLDER)
    return render_template("requests.html", list_to_render=sent_to_list, UPLOAD_FOLDER=UPLOAD_FOLDER, method='sent')


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
                                    UPLOAD_FOLDER=UPLOAD_FOLDER, sent_accepted=sent_accepted, 
                                    received_accepted=received_accepted, current_user=g.current_user)

# Leslie's suggestion to join received/accepted

# @app.route('/received')
# def show_received():

#     # ...
#     # call helper function for received

#     render_template("requests.html", info=info)

# @app.route('/sent')
# def show_sent():

#     # ...
#     # call helper function for sent

#     render_template("requests.html", info=info)




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

     
    return render_template("messages.html", user_list=user_list, UPLOAD_FOLDER=UPLOAD_FOLDER)


@app.route('/retrieve-messages.json')
@login_required
def retrieve_msg_history():

    uid = request.args.get('uid')
    fname = request.args.get('fname')

    # In chat style, we want to show latest at the bottom , hence order by descending
    history = (db.session.query(case([(Message.from_id == g.user_id, 'You')], else_=fname), Message.message, Message.timestamp)
                .filter(((Message.from_id == g.user_id) & (Message.to_id == uid)) |((Message.to_id == g.user_id) & (Message.from_id == uid)))
                .order_by(Message.timestamp).all())

    string = []

    for sender, msg, time in history:
        string.append(sender)
        string.append(msg)
        string.append(str(time))  # otherwise jsonify converts datetime to http format datetime

    return jsonify(string)


#AJAX route
@app.route('/mark-fav', methods=['POST'])
@login_required
def mark_fav_unfav():

    target_id = request.form.get('target_id')
    action = request.form.get('action')
    # timestamp = request.form.get('timestamp')
    timestamp = datetime.now()

    if action == 'fav':
        new_fav = Favorite(source_userid=g.user_id, target_userid=target_id, timestamp=timestamp)
        db.session.add(new_fav)

    if action == 'un-fav':
        remove_fav = Favorite.query.filter_by(source_userid=g.user_id, target_userid=target_id).one()
        db.session.delete(remove_fav)

    db.session.commit()

    return "OK"


@app.route('/my-homepage/favorites', methods=['GET'])
@login_required
def get_favorites():

    fav_list = Favorite.query.filter_by(source_userid=g.user_id).order_by(desc('timestamp')).all()

    return render_template("requests.html", list_to_render=fav_list, UPLOAD_FOLDER=UPLOAD_FOLDER, method='favorite')


@app.route('/edit-profile', methods=['POST'])
@login_required
def edit_user_profile():
    """ Lets logged-in user the ability to edit his/her profile"""

    # note - 'g' is not truly global

    g.current_user.personal.dob = request.form.get('dob')
    g.current_user.personal.height = request.form.get('height')
    g.current_user.personal.ethnicity_id = request.form.get('ethnicity')
    g.current_user.personal.religion_id = request.form.get('religion')
    g.current_user.personal.smoke = request.form.get('smoke')
    g.current_user.personal.drink = request.form.get('drink')
    g.current_user.personal.current_rel_status = request.form.get('current_rel')
    g.current_user.personal.kids = request.form.get('kids')
    g.current_user.professional.employer = request.form.get('employer')
    g.current_user.professional.education = request.form.get('education')
    g.current_user.professional.occupation = request.form.get('occupation')

    db.session.commit()

    return "OK"


@app.route('/logout')
def logout():
    """Logout User"""

    #del session['user_id']
    session.clear()
    #flash("You were logged out.")

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

