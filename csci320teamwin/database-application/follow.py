# follow.py

import psycopg2

# Import the existing SSH tunnel and database connection parameters from your main file


def follow_user(conn, cur, user_id):
    try:

        # Call the looping portion for following users
        user_follow_loop(conn, cur, user_id)

        display_user_follows(conn, cur, user_id)
        return
    except (Exception, psycopg2.Error) as error:
        print("Error: ", error)


"""
TODO: Tell the user they are already following that user.
"""
def user_follow_loop(conn, cur, user_id):
    print()

    try:
        while True:
             print("**To exit this feature enter 'STOP'**")
             follow_email = input("Enter the email of the user you would like to follow: ")
             if follow_email == "STOP":
                 break
             else:
                # SQL query to retrieve all users from the database, ordered ascending by userid
                sql = "SELECT u.userid, u.username, u.email FROM PLAYER u WHERE email ILIKE %s ORDER BY u.userid ASC;"
                cur.execute(sql, [f"%{follow_email}"])
                results = cur.fetchall()
                # Displaying all the users in the database
                for row in results:
                    print("User ID: ", row[0], "\t Username: ", row[1], "\t Email: ", row[2])
                print()

                follow_request = input("Do you wish to follow this user (Y/N): ")
                if follow_request == "Y":
                    follow_id = row[0]
                    sql = "INSERT INTO follows (userID, followsID) VALUES (%s, %s)"
                    val = (user_id, follow_id)
                    cur.execute(sql, val)
                    conn.commit()
                     # Get the username to display it for the User
                    sql = "SELECT username FROM PLAYER WHERE userid = %s"
                    val = ([follow_id])
                    cur.execute(sql, val)
                    conn.commit()
                    results = cur.fetchall()
                    follow_username = results[0][0]
                    print("Now following '" + follow_username)
                    print()
                elif follow_request == "N":
                    continue

    except (Exception, psycopg2.Error) as error:
        print("Error: ", error)


def unfollow_user(conn, cur, user_id):

    try:
        # function to retrieve the users that the user follows
        display_user_follows(conn, cur, user_id)
        
        # Call the looping portion for adding games to the collection
        unfollow_user_loop(conn, cur, user_id)
    
    except (Exception, psycopg2.Error) as error:
        print("Error: ", error)


"""
TODO: handle if the user does not follow a certain user.
"""
def unfollow_user_loop(conn, cur, user_id):

    try:
        while True:
             print("**To exit this feature enter '-1'**")
             follow_id = int(input("Please enter the ID of the user you'd like to unfollow: "))
             if follow_id < 0:
                 print()
                 break
            
            # Get the username to display it for the User
             sql = "SELECT username FROM PLAYER WHERE userid = %s"
             val = ([follow_id])
             cur.execute(sql, val)
             conn.commit()
             results = cur.fetchall()
             follow_username = results[0][0]

             sql = "DELETE FROM follows WHERE userId = %s AND followsID = %s"
             val = (user_id, follow_id)
             cur.execute(sql, val)
             conn.commit()

             print("Unfollowed '" + follow_username)
             print()
    
    except (Exception, psycopg2.Error) as error:
        print("Error: ", error)


def display_user_follows(conn, cur, user_id):
    try:            

        sql = "SELECT followsID FROM follows WHERE userid = %s"
        val = (user_id)
        cur.execute(sql, val)
        conn.commit()
        results = cur.fetchall()

        # Displaying the user's following
        print("Following: ", len(results), " users")
        for row in results:
            print("\tUser ID: ", row[0])
            # print("\tUser ID: ", row[1], "\t Username: ", row[2])
    except (Exception, psycopg2.Error) as error:
        print("Error: ", error)
