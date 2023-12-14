#20_popular_last_90_days.py

from dataclasses import dataclass
import psycopg2
import time


"""
C

Args:
    conn (psycopg2.connection): The database connection.
    cur (psycopg2.cursor): The database cursor.
    user_id (int): The user's ID for whom the collection is being created.
Returns:
    None
Raises:
    psycopg2.Error: If there is an error during the database operations.
"""
@dataclass
class collectionInfo:
    gameiD: int
    title: str
    playtime: float
    playerCount: int

def most_popular_90_days(conn, cur, user_id):

    try:
        # SQL query to retrieve collections and their details
        sql_query = """
            SELECT
                p.gameid,
                v.title,
                COALESCE(SUM(EXTRACT(EPOCH FROM (p.end_play_time - p.start_play_date_time)) / 3600), 0) AS playtime_hours,
                COUNT(p.userID) AS player_count
            FROM plays p
            LEFT JOIN videogame v ON v.gameid = p.gameid
            WHERE
                start_play_date_time >= CURRENT_DATE -90
                AND
                        end_play_time >= CURRENT_DATE -90
            GROUP BY p.gameid, v.title
            ORDER BY playtime_hours DESC
            LIMIT 20;
        """

        
        # Execute the SQL query with the user_id as a parameter
        cur.execute(sql_query)
        conn.commit()
        
        # Fetch all rows and print the results
        results = cur.fetchall()

        instance_list = []

        counter = 1

        print("------ Top 20 Games in the past 90 Days ------")
        print("Top 20 Rank:\t|\tGame ID:\t|\tGame Title:\t|\tTotal Hours Played:\t|\tPlayer Count:")
        print("-----------------------------------------------------------------------------------------")
        for row in results:
            print(counter, "\t-", row[0], "\t-", row[1], "\t-", round(row[2],2), "\t-", row[3])
            counter = counter + 1

    except (Exception, psycopg2.Error) as error:
        print("Error: ", error)


"""

"""
def output_20_list(game_list):

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