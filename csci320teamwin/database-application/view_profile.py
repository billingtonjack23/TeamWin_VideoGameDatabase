import psycopg2


def view_profile(conn, cur, userid):
    try:
        while True:   
             print("##################################################")        
             print("#\t|\tFeature")
             print("---------------------------------------")
             print("1\t-\tview number of collections")
             print("2\t-\tview number of followers")
             print("3\t-\tview number of following")
             print("4\t-\tview your top 10 games")

             print()
             print("*Enter -1 to exit the application*")
             print()
             input_command = (int(input("***\tEnter the number for what you would like to do:\t> ")))
             match input_command:
                    case -1:
                        break
            
                    case 1:
                        try:
                            # SQL query to retrieve all users from the database, ordered ascending by userid
                            sql = "SELECT count(collection_name) FROM collection WHERE userid = %s;"
                            cur.execute(sql, userid)
                            results = cur.fetchall()
                            # Displaying all the users in the database
                            print("number of collections: ", results[0][0])
                            print()
                        except (Exception, psycopg2.Error) as error:
                            print("Error: ", error)

                    case 2:
                        try:
                            sql = "SELECT userid FROM follows WHERE followsid = %s"
                            val = (userid)
                            cur.execute(sql, val)
                            conn.commit()
                            results = cur.fetchall()
                            print("Followers: ", len(results), " users")
                            for row in results:
                                print("\tUser ID: ", row[0])
                                conn.commit()
                        except (Exception, psycopg2.Error) as error:
                            print("Error: ", error)

                    case 3:
                        try:            
                            sql = "SELECT followsID FROM follows WHERE userid = %s"
                            val = (userid)
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
                    
                    case 4:
                        try:
                             sql_query = """
                             SELECT p.gameid, v.title, COALESCE(SUM(EXTRACT(EPOCH FROM (p.end_play_time - p.start_play_date_time)) / 3600), 0) 
                             AS playtime_hours FROM videogame v 
                             LEFT JOIN plays p ON v.gameid = p.gameid AND p.userID = %s 
                             WHERE p.userID = %s GROUP BY p.gameid, v.title 
                             ORDER BY playtime_hours DESC 
                             LIMIT 10;"""
                             val = (userid, userid)
                             counter = 1
                             cur.execute(sql_query, val)
                             conn.commit()
                             results = cur.fetchall()
                             print("Your top 10 most played games: ")
                             for row in results:
                                 print(f'{str(counter) + ":"}'.ljust(3), row[1].ljust(30), "Time played:" , f"{row[2]:.0f}")
                                 counter += 1
                        except (Exception, psycopg2.Error) as error:
                            print("Error: ", error)
    except (Exception, psycopg2.Error) as error:
        print("Error: ", error)