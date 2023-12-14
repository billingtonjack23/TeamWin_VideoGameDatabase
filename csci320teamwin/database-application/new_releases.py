#new_releases.py

import psycopg2

def news_releases(conn, cur, userid):
    try:
        sql = """
        SELECT
            v.gameid,
            v.title,
            SUM(EXTRACT(EPOCH FROM (p.end_play_time - p.start_play_date_time)) / 3600) AS playtime_hours,
            EXTRACT(YEAR from a.release_date) || '-' ||
            EXTRACT(MONTH from a.release_date) || '-' ||
            EXTRACT(DAY from a.release_date) as formatted_date
        FROM plays p 
        LEFT JOIN available_on a ON p.gameid = a.gameid
        LEFT JOIN videogame v ON p.gameid = v.gameid
        WHERE
            EXTRACT(Month from release_date) = EXTRACT(Month from CURRENT_DATE)
            AND
            EXTRACT(YEAR from release_date) = EXTRACT(YEAR from CURRENT_DATE)
        GROUP BY v.gameid, a.release_date 
        ORDER BY playtime_hours DESC
        LIMIT 5;
        """

        cur.execute(sql)
        conn.commit()
        results = cur.fetchall()
            
        counter = 1
        print("------ Top 5 New Games  ------")
        print("Top 5 Rank:\t|\tGame ID:\t|\tGame Title:\t|\tTotal Hours Played:\t|\tRelease Date:\t|")
        print("-----------------------------------------------------------------------------------------")
        for row in results:
            print(counter, "\t-", row[0], "\t-", row[1], "\t-", f"{row[2]:0f}", "\t-", row[3])
            counter = counter + 1
        
    except(Exception, psycopg2.Error) as error:
        print("Error: ", error)

