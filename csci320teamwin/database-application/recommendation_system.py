# recommendation_system.py

import time
import popular_20_last_90_days
import follows_top_20
import new_releases
import for_you
import big_messages

import psycopg2
from dataclasses import dataclass
from typing import List, Optional

# Separate menu for all recommendation and top game options
def recommendation_system(conn, cur, user_id):

    big_messages.print_Recommendations()

    flag = True
            
    while flag == True:
        print()
        print("##################################################")
        input_command = print_all_commands()
        match input_command:
            case -1:
                break
            case 1:
                popular_20_last_90_days.most_popular_90_days(conn, cur, user_id)
            case 2:
                follows_top_20.follows_top_20(conn, cur, user_id)
            case 3:
                new_releases.news_releases(conn, cur, user_id)
            case 4:
                for_you.for_you(conn, cur, user_id)
            case _:
                print("!! You entered an invalid command number !!")
                time.sleep(2)


def print_all_commands():
    print("#\t|\tFeature")
    print("---------------------------------------")
    print("1\t-\tTop Games (Past 90 Days)")
    print("2\t-\tTop Games from People You Follow")
    print("3\t-\tTop 5 Releases of the Month")
    print("4\t-\tRecommendations FOR YOU")
    print()
    print("*Enter -1 to return to menu*")
    print()
    input_command = int(input("***\tEnter the number for what you would like to do:\t> "))
    return input_command

