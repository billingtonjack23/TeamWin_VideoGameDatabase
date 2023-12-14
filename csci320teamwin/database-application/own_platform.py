# own_platform.py

import psycopg2
import time

"""
"""
def own_platform_start(conn, cur, user_id):
    try:
        # SQL query to retrieve platforms associated with a user, ordered by name
        sql = "SELECT platformID, platform_Name FROM platform ORDER BY platform_Name ASC;"
        val = ([user_id])
        cur.execute(sql, val)
        conn.commit()
        results = cur.fetchall()
        
        # Displaying the user's platforms
        print("------ Available Platforms ------")
        print("Platform ID:\t|\tPlatform Name:")
        for row in results:
            print(row[0], "\t\t-\t", row[1])
        
        print()

        # Prompt the user to select a platform by ID to add games to it
        platform_id = int(input("Please enter the ID of the platform you own:\t> "))

        # Get the platform's name to display it for the User
        sql = "SELECT platform_name FROM platform WHERE platformID = %s;"
        val = ([platform_id])
        cur.execute(sql, val)
        conn.commit()
        results = cur.fetchall()
        platform_name = results[0][0]

        sql = "INSERT INTO owns (userID, platformID) VALUES (%s, %s)"
        val = (user_id, platform_id)
        cur.execute(sql, val)
        conn.commit()

        print("Congratulations on owning '" + platform_name + "'!")
        print()
        time.sleep(1)
    
    except (Exception, psycopg2.Error) as error:
        print("Error: ", error)