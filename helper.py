
def get_latest_messages(db, user_id):
    """Given a GitHub account name, print info about the matching student."""

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
