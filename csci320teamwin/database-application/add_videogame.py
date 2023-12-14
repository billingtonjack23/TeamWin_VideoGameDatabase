#add_videogame.py

import psycopg2
import datetime as dt

# Import the existing SSH tunnel and database connection parameters from your main file

"""

"""
def add_game_to_DB(conn, cur, user_id):

    try:
        # Get input from user for the title of the game
        game_title = str(input("Enter the title for the game:\t> "))

        # Get input from user for the title of the game
        print("Enter the ESRB rating for the game:")
        esrb_rating = str(input("Please choose from:\t'E', 'E10+', 'T', 'M', 'Ao', 'RP'\t> "))

        # Set the new collection's ID to the current MAX(CollectionID) value plus 1
        sql = "SELECT max(gameID)+1 FROM videogame"
        cur.execute(sql)
        conn.commit()
        results = cur.fetchall()
        game_id = results[0]



        sql = "SELECT genreID, genre_name FROM genre ORDER BY genreID ASC"
        cur.execute(sql)
        conn.commit()
        results = cur.fetchall()
        
        # Displaying the Platforms for games
        print("------ All Genres ------")
        print("Genre ID\t|\tGenre Name:")
        for row in results:
            print(row[0], "\t\t-\t", row[1])

        print()
        # Get input from user for the title of the game
        genre_id = str(input("Enter the ID for the genre of the game:\t> "))



        sql = "SELECT platformID, platform_name FROM platform ORDER BY platform_name ASC"
        cur.execute(sql)
        conn.commit()
        results = cur.fetchall()
        
        # Displaying the Platforms for games
        print("------ All Platforms ------")
        print("Platform ID\t|\tPlatform Name:")
        for row in results:
            print(row[0], "\t-\t", row[1])

        print()
        # Get input from user for the title of the game
        platform_id = str(input("Enter the ID for the platform of the game:\t> "))


        print()
        game_price = float(input("Enter the price of the game:\t##.##\t> "))

        print()
        release_date = str(input("Enter the game's release date\t(yyyy-mm-dd):\t> "))
        year, month, day = map(int, release_date.split('-'))
        game_release_date = dt.date(year, month, day)

        # Add new row to the 'videogame' table
        sql = "INSERT INTO videogame (gameID, title, esrb_rating) VALUES (%s, %s, %s)"
        val = (game_id, game_title, esrb_rating)
        cur.execute(sql, val)

        # Add new row to the 'available_on' table
        sql = "INSERT INTO available_on (gameID, platformID, price_per_platform, release_date) VALUES (%s, %s, %s, %s)"
        val = (game_id, platform_id, game_price, game_release_date)
        cur.execute(sql, val)

        # Add new row to the 'video_game_genre' table
        sql = "INSERT INTO video_game_genre (gameID, genreID) VALUES (%s, %s)"
        val = (game_id, genre_id)
        cur.execute(sql, val)
        conn.commit()

        # Confirmation message
        print("Game " + game_title + " successfully created!")
        print()
        return
    
    except (Exception, psycopg2.Error) as error:
        print("Error: ", error)