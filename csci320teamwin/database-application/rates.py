# rates.py

import psycopg2

# Import the existing SSH tunnel and database connection parameters from your main file


def rate_game(conn, cur, user_id):

    try:

        sql = "SELECT gameID, title FROM videogame ORDER BY title ASC"
        cur.execute(sql)
        conn.commit()
        results = cur.fetchall()
        
        # Displaying every game
        print("------ All Games ------")
        print("GameID:\t|\tTitle:")
        for row in results:
            print(row[0], "\t-\t", row[1])

        print()
        game_id = int(input("Enter the Game ID you want to rate:\t> "))
        #rating = 0
        #while ( (rating < 1) & (rating > 5) ):
        print()
        rating = int(input("Enter your rating, must be between 1 and 5:\t> "))

        sql = "INSERT INTO rates (UserID, GameID, star_rating) VALUES (%s, %s, %s)"
        val = (user_id, game_id, rating)
        cur.execute(sql, val)
        conn.commit()


        return
    except (Exception, psycopg2.Error) as error:
        print("Error: ", error)