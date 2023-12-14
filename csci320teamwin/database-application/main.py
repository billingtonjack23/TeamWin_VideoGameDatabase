import psycopg2
import time

import rates
import collectionsFeature
import login
import follow
import filter_search
import big_messages
import interface_messages
import add_videogame
import play_game
import own_platform
import recommendation_system
import view_profile

from sshtunnel import SSHTunnelForwarder

# Initiate the login for a user
big_messages.print_Login()
loginpy_lst = login.prompt_loop()
username = loginpy_lst[0]
#file1 = open("/Users/jayson/Desktop/PCS320/csci320teamwin/database-application/password.txt", "r")
password = "***"


dbName = "p320_01"


try:
    with SSHTunnelForwarder(('starbug.cs.rit.edu', 22),
                            ssh_username=username,
                            ssh_password=password,
                            remote_bind_address=('127.0.0.1', 5432)) as server:
        server.start()
        print("SSH tunnel established")
        params = {
            'database': dbName,
            'user': username,
            'password': password,
            'host': 'localhost',
            'port': server.local_bind_port
        }


        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        print("Database connection established")

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #DB work here....

        # For registering user into the database
        # If need to register
        if len(loginpy_lst) > 2:
           user_id = login.insert_user(conn, cur, loginpy_lst)
        # Else, login
        else:
           print(password)
           password = loginpy_lst[1]
           print(password)
           user_id = login.update_access_date(conn, cur, username, password)
            

        try:
            big_messages.print_Welcome()

            flag = True
            
            while flag == True:
                print()
                print("##################################################")
                input_command = interface_messages.print_all_commands()

                match input_command:
                    case -1:
                        break
                    case 1:
                        add_videogame.add_game_to_DB(conn, cur, user_id)
                    case 2:
                        collectionsFeature.create_collection(conn, cur, user_id)
                    case 3:
                        collectionsFeature.display_user_collections(conn, cur, user_id)
                    case 4:
                        collectionsFeature.add_to_collection_start(conn, cur, user_id)
                    case 5:
                        collectionsFeature.remove_from_collection_start(conn, cur, user_id)
                    case 6:
                        collectionsFeature.change_collection_name(conn, cur, user_id)
                    case 7:
                        filter_search.filterSearch(conn, cur)
                    case 8:
                        play_game.play_game_start(conn, cur, user_id)
                    case 9:
                        rates.rate_game(conn, cur, user_id)
                    case 10:
                        follow.follow_user(conn, cur, user_id)
                    case 11:
                        follow.unfollow_user(conn, cur, user_id)
                    case 12:
                        own_platform.own_platform_start(conn, cur, user_id)
                    case 13:
                        view_profile.view_profile(conn, cur, user_id)
                    case 14:
                        recommendation_system.recommendation_system(conn, cur, user_id)
                    case _:
                        print("!! You entered an invalid command number !!")
                        time.sleep(2)

        except (Exception, psycopg2.Error) as error:
            print("Error: ", error)

        cur.close()
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        conn.close()
        print("Database connection successfully closed.")
        big_messages.print_Exit()
except:
    print("Connection failed")
