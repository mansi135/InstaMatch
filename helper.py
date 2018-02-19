from pyzipcode import ZipCodeDatabase
from pytz import timezone


def get_latest_messages(db, user_id):
    """Given a user_id, return all messages to and from him to every-other user."""

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



#def some_function_for_timestamp():

    # Getting PST time-stamp, will be used later
        #ca = timezone('US/Pacific')

        #print datetime.now(ca).strftime('%Y-%m-%d %H:%M:%S')
        #print str(datetime.now(ca))

        # Select * from Users where zip_code IN (19125,19081,19107.........);

