"""
File: follows_top_20.py
Author: Team Win
"""

from dataclasses import dataclass
import psycopg2
import time


"""
This function gets the top 20 games played among the people you follow

Args:
    conn (psycopg2.connection): The database connection
    con (psycopg2.cursor): The database cursor
    user_id (int): The user's ID to tell which people they follow
Returns:
    None
Raises:
    psycopg2.Error: if there is an error during the database operation.

"""
def follows_top_20(conn, cur, user_id):


    try:
        

        sql_query = """
        SELECT
                p.gameid,
                v.title,
                COALESCE(SUM(EXTRACT(EPOCH FROM (p.end_play_time - p.start_play_date_time)) / 3600), 0) AS playtime_hours
            FROM videogame v
            LEFT JOIN plays p ON v.gameid = p.gameid
            LEFT JOIN follows f ON p.userid = f.followsid AND f.userid = %s
            WHERE
                f.userid = %s
            GROUP BY p.gameid, v.title
            ORDER BY playtime_hours DESC
            LIMIT 20;
        """

        val = (user_id, user_id)
        cur.execute(sql_query, val)
        conn.commit()

        results = cur.fetchall()

        for row in results:
            print("Game ID: ", row[0], "\t Game Title: ", row[1], "Playtime: ", row[2])
        
        return
    except (Exception, psycopg2.Error) as error:
        print("Error: ", error)