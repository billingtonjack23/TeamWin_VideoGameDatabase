#play_game.py

import datetime as dt
import time
import psycopg2
import random

# Import the existing SSH tunnel and database connection parameters from your main file

"""

"""
def play_game_start(conn, cur, user_id):


    try:
        
        randomFlag = str(input("Would you like to play a random game?\t(Y/N)\n\tIf 'N' you'll get to choose a game.\t> "))

        # SQL query to retrieve collections associated with a user, ordered by name
        sql = "SELECT c.CollectionID, c.Collection_Name FROM COLLECTION c WHERE c.userID = %s ORDER BY c.Collection_Name ASC;"
        val = ([user_id])
        cur.execute(sql, val)
        results = cur.fetchall()

        # Displaying the user's collections
        print("------ Your collections: ------")
        print("Collection ID:\t|\tCollection Name:")
        for row in results:
            print(row[0], "\t\t-\t", row[1])
        
        print()

        # Prompt the user to select a collection by ID to add games to it
        collection_id = int(input("Please enter the ID of the collection you'd like to play a game from:\t> "))

        # Get the collection's name to display it for the User
        sql = "SELECT Collection_Name FROM COLLECTION WHERE collectionID = %s;"
        val = ([collection_id])
        cur.execute(sql, val)
        conn.commit()
        results = cur.fetchall()
        collection_name = results[0][0]

        if randomFlag == 'Y':
            play_random_game(conn, cur, user_id, collection_id, collection_name)
        else:
            play_specific_game(conn, cur, user_id, collection_id, collection_name)

        return
    except (Exception, psycopg2.Error) as error:
        print("Error: ", error)


"""
TODO
"""
def play_specific_game(conn, cur, user_id, collection_id, collection_name):   

    try:
        # 
        sql = "SELECT V.GameID, V.Title FROM VIDEOGAME V JOIN PART_OF_COLLECTION POC ON V.GameID = POC.GameID WHERE POC.CollectionID = %s"
        val = ((collection_id,))
        cur.execute(sql, val)
        conn.commit()
        results = cur.fetchall()

        # Displaying the games in the selected collection
        print("------ Collection :\t" + collection_name + " ------")
        print("Game ID:\t|\tGame Title:")
        for row in results:
            print(row[0], "\t\t-\t", row[1])
        
        print()

        game_id = int(input("Enter a game's ID that you'd like to play!:\t> "))
        print()

        results = datetime_input_helper()
        start_play_date_time = results[0]
        end_play_date_time = results[1]

        sql = "INSERT INTO plays (userID, gameID, start_play_date_time, end_play_time) VALUES (%s, %s, %s, %s)"
        val = (user_id, game_id, start_play_date_time, end_play_date_time)
        cur.execute(sql, val)
        conn.commit()

        # Get the game's title based on the game_id
        game_name = fetch_game_title(conn, cur, game_id)

        timeDiff = end_play_date_time - start_play_date_time
        timeDiff = int(timeDiff.total_seconds() / 60)
        print_picture()
        print("You played ",game_name," for ", timeDiff," minutes!")

        return
    except (Exception, psycopg2.Error) as error:
        print("Error: ", error)


"""
TODO
"""
def play_random_game(conn, cur, user_id, collection_id, collection_name):
    try:
        # 
        sql = "SELECT V.GameID FROM VIDEOGAME V JOIN PART_OF_COLLECTION POC ON V.GameID = POC.GameID WHERE POC.CollectionID = %s"
        val = ((collection_id,))
        cur.execute(sql, val)
        conn.commit()
        results = cur.fetchall()

        idList = []
        for row in results:
            idList.append(row[0])
        
        # Simulate time passing to add effect
        print()
        print("Choosing a game")
        time.sleep(1)
        print(".")
        time.sleep(1)
        print(".")
        time.sleep(1)
        print(".")
        time.sleep(1)
        print("■")

        # Randomly choose a game_id from the possible video games
        game_id = random.choice(idList)

        # Get the game's title based on the game_id
        game_name = fetch_game_title(conn, cur, game_id)
        print("You'll be playing " + game_name + "!")
        print()

        # 
        results = datetime_input_helper()
        start_play_date_time = results[0]
        end_play_date_time = results[1]

        #
        sql = "INSERT INTO plays (userID, gameID, start_play_date_time, end_play_time) VALUES (%s, %s, %s, %s)"
        val = (user_id, game_id, start_play_date_time, end_play_date_time)
        cur.execute(sql, val)
        conn.commit()

        timeDiff = end_play_date_time - start_play_date_time
        timeDiff = int(timeDiff.total_seconds() / 60)
        print_picture()
        print("You played ",game_name," for ", timeDiff," minutes!")
        print()

        return
    except (Exception, psycopg2.Error) as error:
        print("Error: ", error)


"""

"""
def datetime_input_helper():
    enter_date = str(input("Enter play START date\t(yyyy-mm-dd):\t> "))
    year, month, day = map(int, enter_date.split('-'))
    input_start_date = dt.date(year, month, day)

    enter_time = str(input("Enter play START time\t(hh:mm):\t> "))
    hours, minutes = map(int, enter_time.split(':'))
    input_start_time = dt.time(hours, minutes, second=0)
    
    start_play_date_time = dt.datetime.combine(input_start_date, input_start_time)
    print()
    
    enter_date = str(input("Enter play END date\t(yyyy-mm-dd):\t> "))
    year, month, day = map(int, enter_date.split('-'))
    input_end_date = dt.date(year, month, day)

    enter_time = str(input("Enter play END time\t(hh:mm):\t> "))
    hours, minutes = map(int, enter_time.split(':'))
    input_end_time = dt.time(hours, minutes, second=0)
    
    end_play_date_time = dt.datetime.combine(input_end_date, input_end_time)
    print()
    
    dateList = [start_play_date_time, end_play_date_time]
    return dateList



"""
"""
def fetch_game_title(conn, cur, game_id):
    # Get the game's name to display it for the User
    sql = "SELECT title FROM videogame WHERE gameID = %s"
    val = ([game_id])
    cur.execute(sql, val)
    conn.commit()
    results = cur.fetchall()
    game_name = results[0][0]
    return game_name


"""

"""
def print_picture():
    print()
    numList = [1, 2]
    flag = random.choice(numList)
    print("▒▒▒▒▒▒▒▒▒▄▄▄▄▒▒▒▒▒▒▒")
    print("▒▒▒▒▒▒▄▀▀▓▓▓▀█▒▒▒▒▒▒")
    print("▒▒▒▒▄▀▓▓▄██████▄▒▒▒▒")
    print("▒▒▒▄█▄█▀░░▄░▄░█▀▒▒▒▒")
    print("▒▒▄▀░██▄░░▀░▀░▀▄▒▒▒▒")
    print("▒▒▀▄░░▀░▄█▄▄░░▄█▄▒▒▒")
    print("▒▒▒▒▀█▄▄░░▀▀▀█▀▒▒▒▒▒")
    print("▒▒▒▄▀▓▓▓▀██▀▀█▄▀▀▄▒▒")
    print("▒▒█▓▓▄▀▀▀▄█▄▓▓▀█░█▒▒")
    print("▒▒▀▄█░░░░░█▀▀▄▄▀█▒▒▒")
    print("▒▒▒▄▀▀▄▄▄██▄▄█▀▓▓█▒▒")
    print("▒▒█▀▓█████████▓▓▓█▒▒")
    print("▒▒█▓▓██▀▀▀▒▒▒▀▄▄█▀▒▒")
    print("▒▒▒▀▀▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒")
    print()