#collectionsFeature.py

from dataclasses import dataclass
import psycopg2
import time

# Import the existing SSH tunnel and database connection parameters from your main file

"""
Create a new collection in the database for a specific user.

This function prompts the user to provide a name for the new collection and assigns
a unique collection ID. It then inserts the new collection record into the 'Collection'
table and establishes the association between the user and the collection in the 'Creates_Collection' table.
Args:
    conn (psycopg2.connection): The database connection.
    cur (psycopg2.cursor): The database cursor.
    user_id (int): The user's ID for whom the collection is being created.
Returns:
    None
Raises:
    psycopg2.Error: If there is an error during the database operations.
"""
def create_collection(conn, cur, user_id):

    try:
        # Get input from user for the new collection's name
        collection_name = str(input("Enter the name for your new Collection: "))

        # Set the new collection's ID to the current MAX(CollectionID) value plus 1
        sql = "SELECT max(CollectionID)+1 FROM Collection"
        cur.execute(sql)
        results = cur.fetchall()
        collection_id = results[0]

        # Add new row to the 'Collection' table
        sql = "INSERT INTO collection (collectionID, collection_name, userID) VALUES (%s, %s, %s)"
        val = (collection_id, collection_name, user_id)
        cur.execute(sql, val)
        conn.commit()

        # Add new row to the 'Creates_Collection' table
        sql = "INSERT INTO creates_collection (UserID, CollectionID) VALUES (%s, %s)"
        val = (user_id, collection_id)
        cur.execute(sql, val)
        conn.commit()

        # Confirmation message
        print("Collection " + collection_name + " successfully created!")

        # Ask the user if they want to immediately add games to their new collection
        yesNO = ""
        # while yesNO != "Y" || yesNO != "N":
        #     yesNO = str(input("Would you like to add games to your new collection? (Y/N) "))
        #     if 
        yesNO = str(input("Would you like to add games to your new collection right away?\t(Y/N)\t"))
        if yesNO == 'Y':
            add_to_collection_loop(conn, cur, user_id, collection_id, collection_name)
        else:
            print()
        return
    
    except (Exception, psycopg2.Error) as error:
        print("Error: ", error)


"""
Initiate the process of adding games to a user's collection in the database.

This function begins by retrieving and displaying the user's existing collections, ordered by name.
It then prompts the user to select a collection by its ID to which they want to add games.
After the user's selection, it obtains the name of the chosen collection and calls
the 'add_to_collection_loop' function, which allows the user to add games to the selected collection.
Args:
    conn (psycopg2.connection): The database connection.
    cur (psycopg2.cursor): The database cursor.
    user_id (int): The user's ID for whom games are being added to a collection.
Returns:
    None
Raises:
    psycopg2.Error: If there is an error during the database operations.
"""
def add_to_collection_start(conn, cur, user_id):
    try:
        # SQL query to retrieve collections associated with a user, ordered by name
        sql = "SELECT c.CollectionID, c.Collection_Name FROM COLLECTION c WHERE c.userID = %s ORDER BY c.Collection_Name ASC;"
        val = ([user_id])
        cur.execute(sql, val)
        conn.commit()
        results = cur.fetchall()
        
        # Displaying the user's collections
        print("\tYour collections:")
        for row in results:
            print("Collection ID: ", row[0], "\t Collection Name: ", row[1])
            print()

        # Prompt the user to select a collection by ID to add games to it
        collection_id = int(input("Please enter the ID of the collection you'd like to add games to: \t"))

        # Get the collection's name to display it for the User
        sql = "SELECT Collection_Name FROM COLLECTION WHERE collectionID = %s;"
        val = ([collection_id])
        cur.execute(sql, val)
        conn.commit()
        results = cur.fetchall()
        collection_name = results[0][0]

        # Call the looping portion for adding games to the collection
        add_to_collection_loop(conn, cur, user_id, collection_id, collection_name)
    
    except (Exception, psycopg2.Error) as error:
        print("Error: ", error)


"""
TODO: give a warning if the user tries to add a game that they don't own the platform for.
"""
def add_to_collection_loop(conn, cur, user_id, collection_id, collection_name):
    print()

    try:

        sql = "SELECT gameID, title, esrb_rating FROM videogame ORDER BY title ASC"
        cur.execute(sql)
        conn.commit()
        results = cur.fetchall()
        
        # Displaying the user's collections
        print("------ All Games ------")
        print("GameID:\t|\tTitle:")
        for row in results:
            print(row[0], "\t-\t", row[1])

        print()
        game_id = 1    # Init game_id to start while loop
        game_name = ""

        

        while True:
            print("**To exit this feature enter '-1'**")
            game_id = int(input("Enter a game's ID to add it to Collection '" + collection_name + "' : \t"))
            if game_id < 0:
                print()
                break

            sql = """SELECT
                        P.PlatformID
                    FROM PLATFORM AS P
                    LEFT JOIN AVAILABLE_ON AS A ON P.PlatformID = A.PlatformID
                    LEFT JOIN OWNS AS O ON A.PlatformID = O.PlatformID
                    WHERE
                        O.UserID = %s
                    AND A.GameID = %s;
                """
            val = (user_id, game_id)
            cur.execute(sql, val)
            conn.commit()
            results = cur.fetchall()
            check = (len(results))

            # Get the game's name to display it for the User
            sql = "SELECT title FROM videogame WHERE gameID = %s"
            val = ([game_id])
            cur.execute(sql, val)
            conn.commit()
            results = cur.fetchall()
            game_name = results[0][0]


            if check < 1:
                print("!! WARNING !! You do not own any platforms that runs this game !!")
                print("Would you still like to add ", game_name, " to Collection '", collection_name,"'?")
                yesNO = str(input("\t(Y/N)\t> "))
                if yesNO == 'N':
                    print("Game will not be added.")
                    print()
                    time.sleep(1)
                else:
                    sql = "INSERT INTO part_of_collection (gameID, collectionID) VALUES (%s, %s)"
                    val = (game_id, collection_id)
                    cur.execute(sql, val)
                    conn.commit()

                    print("Successfully added '" + game_name + "' to Collection '" + collection_name + "'")
                    print()
                    time.sleep(1)
            else:
                sql = "INSERT INTO part_of_collection (gameID, collectionID) VALUES (%s, %s)"
                val = (game_id, collection_id)
                cur.execute(sql, val)
                conn.commit()

                print("Successfully added '" + game_name + "' to Collection '" + collection_name + "'")
                print()
                time.sleep(1)

    except (Exception, psycopg2.Error) as error:
        print("Error: ", error)


"""
TODO: handle if the game is not in the collection.
"""
def remove_from_collection_start(conn, cur, user_id):

    try:
        # SQL query to retrieve collections associated with a user, ordered by name
        sql = "SELECT c.CollectionID, c.Collection_Name FROM COLLECTION c WHERE c.userID = %s ORDER BY c.Collection_Name ASC;"
        val = ([user_id])
        cur.execute(sql, val)
        results = cur.fetchall()
        
        # Displaying the user's collections
        print("\tYour collections:")
        for row in results:
            print("Collection ID: ", row[0], "\t Collection Name: ", row[1])
            print()

        # Prompt the user to select a collection by ID to remove games from it
        collection_id = int(input("Please enter the ID of the collection you'd like to remove games from: \t"))

        # Get the collection's name to display it for the User
        sql = "SELECT Collection_Name FROM COLLECTION WHERE collectionID = %s;"
        val = ([collection_id])
        cur.execute(sql, val)
        conn.commit()
        results = cur.fetchall()
        collection_name = results[0][0]

        # Call the looping portion for adding games to the collection
        remove_from_collection_loop(conn, cur, user_id, collection_id, collection_name)
    
    except (Exception, psycopg2.Error) as error:
        print("Error: ", error)



"""
TODO: handle if the game is not in the collection.
"""
def remove_from_collection_loop(conn, cur, user_id, collection_id, collection_name):

    try:

        game_id = 1    # Init game_id to start while loop
        game_name = ""

        while True:
            print()
            # 
            sql = "SELECT V.GameID, V.Title FROM VIDEOGAME V JOIN PART_OF_COLLECTION POC ON V.GameID = POC.GameID WHERE POC.CollectionID = %s"
            val = ((collection_id,))
            cur.execute(sql, val)
            conn.commit()
            results = cur.fetchall()

            # Displaying the games in the selected collection
            print("\tCollection :\t" + collection_name)
            for row in results:
                print("Game ID: ", row[0], "\t\t", row[1])

            print()
            print("**To exit this feature enter '-1'**")
            game_id = int(input("Enter a game's ID to add it to Collection '" + collection_name + "' : \t"))
            if game_id < 0:
                print()
                break

            # Get the game's name to display it for the User
            sql = "SELECT title FROM videogame WHERE gameID = %s"
            val = ([game_id])
            cur.execute(sql, val)
            conn.commit()
            results = cur.fetchall()
            game_name = results[0][0]

            sql = "DELETE FROM part_of_collection WHERE gameID = %s AND collectionID = %s"
            val = (game_id, collection_id)
            cur.execute(sql, val)
            conn.commit()

            # Confirmation message on removal from collection
            print("Successfully removed '" + game_name + "' from Collection '" + collection_name + "'")
    
    except (Exception, psycopg2.Error) as error:
        print("Error: ", error)



"""
TODO
Users will be to see the list of all their collections by name in ascending order. The list
must show the following information per collection:
– Collection’s name
– Number of video games in the collection
– Total play time of the video games (in hours:minutes) of video games in the
collection
"""

@dataclass
class collectionInfo:
    name: str
    games: int
    playtime: float

def display_user_collections(conn, cur, user_id):

    try:
        # SQL query to retrieve collections and their details
        sql_query = """
            SELECT
                c.collection_name,
                pc.gameid,
                COALESCE(SUM(EXTRACT(EPOCH FROM (p.end_play_time - p.start_play_date_time)) / 3600), 0) AS playtime_hours
            FROM collection c
            LEFT JOIN part_of_collection pc ON c.collectionid = pc.collectionid
            LEFT JOIN plays p ON pc.gameid = p.gameid AND p.userid = %s
            WHERE c.userid = %s
            GROUP BY c.collection_name, pc.gameid
            ORDER BY c.collection_name ASC, pc.gameid ASC;
        """
        
        # Execute the SQL query with the user_id as a parameter
        cur.execute(sql_query, (user_id,user_id,))
        
        # Fetch all rows and print the results
        collections = cur.fetchall()

        instance_list = []

        for result in collections:
            collection_name, _, playtime_hours = result
            if len(instance_list) == 0:
                instance_list.append(collectionInfo(collection_name, 1, playtime_hours))
            else:
                here = False
                for ins in instance_list:
                    if ins.name == collection_name:
                        here = True
                if here:
                    for ins in instance_list:
                        if collection_name == ins.name:
                            ins.games += 1
                            ins.playtime += playtime_hours
                else:
                    instance_list.append(collectionInfo(collection_name, 1, playtime_hours))

        # Display collection information
        output_list(instance_list)

    except (Exception, psycopg2.Error) as error:
        print("Error: ", error)



"""
Modify the name of a user's collection in the database.

This function displays the user's existing collections, prompts the user to select a collection
by its ID, and enter a new name for the selected collection. It then updates the collection's
name in the 'Collection' table in the database.
Args:
    conn: A database connection.
    cur: A database cursor.
    user_id: The ID of the user whose collections are being managed.
Returns:
    None
Raises:
    Exception: Any exceptions or errors that may occur during the process are handled
               and printed, primarily using the psycopg2.Error class for PostgreSQL database errors.
"""
def change_collection_name(conn, cur, user_id):
    try:
        # SQL query to retrieve collections associated with a user, ordered by name
        sql = "SELECT c.CollectionID, c.Collection_Name FROM COLLECTION c WHERE c.userID = %s ORDER BY c.Collection_Name ASC"
        val = ([user_id])
        cur.execute(sql, val)
        results = cur.fetchall()
        
        # Displaying the user's collections
        print("\tYour Collections:")
        for row in results:
            print("Collection ID: ", row[0], "\t Collection Name: ", row[1])
            print()
        
        # Prompt the user to select a collection by ID and enter a new name
        collection_id = int(input("Please enter the ID of the collection you'd like to change the name of: "))
        new_name = str(input("Please enter the new name for this collection: "))

        # SQL query to update the collection name
        sql = "UPDATE collection SET collection_name = %s WHERE collectionID = %s AND userID = %s"
        val = (new_name, collection_id, user_id)
        cur.execute(sql, val)
        conn.commit()

        # Confirmation message
        print("Collection ",collection_id," successfully changed to \"",new_name,"\"")

        return
    
    except (Exception, psycopg2.Error) as error:
        print("Error: ", error)


"""
Delete a user's collection from the database.

This function displays the user's existing collections, prompts the user to select a collection
by its ID for deletion. It then removes the association between the user and the collection
from the 'creates_collection' table and deletes the collection record from the 'collection' table in the database.
Args:
    conn: A database connection.
    cur: A database cursor.
    user_id: The ID of the user whose collections are being managed.
Returns:
    None
Raises:
    Exception: Any exceptions or errors that may occur during the process are handled
               and printed, primarily using the psycopg2.Error class for PostgreSQL database errors.
"""
def delete_collection(conn, cur, user_id):

    try:
        # SQL query to retrieve collections associated with a user, ordered by name
        sql = "SELECT c.CollectionID, c.Collection_Name FROM COLLECTION c WHERE c.userID = %s ORDER BY c.Collection_Name ASC;"
        val = ([user_id])
        cur.execute(sql, val)
        results = cur.fetchall()
        
        # Displaying the user's collections
        print("\tYour Collections:")
        for row in results:
            print("Collection ID: ", row[0], "\t Collection Name: ", row[1])
            print()

        # Prompt the user to select a collection by ID for deletion
        collection_id = int(input("Please enter the ID of the collection you'd like to delete: "))

        # SQL query to delete the association between the user and the collection
        sql = "DELETE FROM creates_collection WHERE CollectionID = %s AND userID = %s"
        val = (collection_id, user_id)
        cur.execute(sql, val)

        # SQL query to delete the collection record itself
        sql = "DELETE FROM collection WHERE CollectionID = %s"
        val = ([collection_id])
        cur.execute(sql, val)

        conn.commit()

        # Confirmation message
        print("Collection ",collection_id," successfully deleted.")

        return
    
    except (Exception, psycopg2.Error) as error:
        print("Error: ", error)

def output_list(game_list):

    separator = "+{:<32}+{:<22}+{:<27}+".format(
        "-" * 32, "-" * 22, "-" * 27
    )
    
    print(separator)

    # Define column headers
    header = "| {:<30} | {:<20} | {:<25} |".format(
        "Name of Collection", "Games in Collection", "Total Collection Playtime"
    )

    # Print the header
    print(header)

    # Print a separator line

    print(separator)

    # Print each game's information
    for game in game_list:
        hours = game.playtime
        minutes = hours * 60
        hours = minutes // 60
        minutes = minutes % 60
        game_info = "| {:<30} | {:<20} | {:<25} |".format(
            game.name, game.games, f"{hours:.0f}:{minutes:.0f}"
        )
        print(game_info)
    
    print(separator)