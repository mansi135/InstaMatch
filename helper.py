from pyzipcode import ZipCodeDatabase
from pytz import timezone
from datetime import datetime, date, timedelta

def get_latest_messages(db, user_id):
    """Given a user_id, return all messages to and from him to every-other user. Return id, message and timestamp"""

    QUERY = """
        WITH 
        all_my_messages AS (SELECT (CASE WHEN from_id = :user_id THEN to_id ELSE from_id END) id, 
            message, timestamp FROM messages WHERE from_id = :user_id OR to_id = :user_id), 
        max_timestamps AS (SELECT id, max(timestamp) max_ts FROM all_my_messages GROUP BY id)
        SELECT a.id id, a.message message, a.timestamp ts FROM all_my_messages a JOIN max_timestamps b ON a.timestamp = b.max_ts 
        ORDER BY ts DESC

        """
   

    db_cursor = db.session.execute(QUERY, {'user_id': user_id})

    row = db_cursor.fetchall()

    return row



def get_zip_near_me(myzip, miles):
    """Shows all zipcodes near you"""

    zcdb = ZipCodeDatabase()
    in_radius = [z.zip for z in zcdb.get_zipcodes_around_radius(myzip, miles)]
    return in_radius
    #return render_template("zip.html",zipcodes=in_radius)



def get_dob_range_from_age(min_age, max_age):
    """Get min and max dobs for DB query"""

    max_dob = datetime.now()-timedelta(days=min_age*365)
    min_dob = datetime.now()-timedelta(days=max_age*365)

    return max_dob, min_dob



def calc_age(dob):
    """ convert db dob to age"""

    today = date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return age
    # dob_t = datetime.strptime(dob, '%Y-%m-%d')


def get_users_info(users, folder, current_user):
    """ convert sql-alchemy User objects to python User objects"""

    matching_users = {}

    for user, personal, contact, picture in users:
        fav = False
        if user.favorites_t:
          fav = True if current_user in [obj.source_userid for obj in user.favorites_t] else False
          
        matching_users[user.user_id] = {'fname': user.fname, 
                                        'lname': user.lname,
                                         'dob': personal.dob,
                                         'age': calc_age(personal.dob),
                                         'height': personal.height,
                                         'gender': personal.gender,
                                         'ethnicity': personal.ethnicity.ethnicity_name,
                                         'religion': personal.religion.religion_name,
                                         'about me': personal.aboutme,
                                         'contact': {'email': user.email,
                                                     'city': contact.city,
                                                     'state': contact.state,
                                                     'zipcode': contact.zipcode,
                                                     'phone': contact.phone
                                                     },
                                          'professional': { 'employer': user.professional.employer,
                                                            'occupation': user.professional.occupation,
                                                            'education': user.professional.education,

                                                          },
                                          'pic_url': folder + picture.picture_url,
                                          'interests': [interest.interest_name for interest in user.interests],
                                          'fav': fav
                                        }

    return matching_users;




