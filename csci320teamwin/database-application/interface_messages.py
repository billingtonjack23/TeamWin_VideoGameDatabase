#interface_messages.py

import psycopg2

def print_all_commands():
    print("#\t|\tFeature")
    print("---------------------------------------")
    print("1\t-\tAdd a game to the database")
    print("2\t-\tCreate a collection of games")
    print("3\t-\tDisplay your collections")
    print("4\t-\tAdd games to your collections")
    print("5\t-\tRemove games from your collections")
    print("6\t-\tChange the name a collection")
    print("7\t-\tFiltered search for games")
    print("8\t-\tPlay a game")
    print("9\t-\tRate a game")
    print("10\t-\tFollow other players")
    print("11\t-\tUnfollow other players")
    print("12\t-\tDeclare a platform you own")
    print("13\t-\tView your profile stats")
    print("14\t-\tTrending and Recommended Games")
    print()
    print("*Enter -1 to exit the application*")
    print()
    input_command = int(input("***\tEnter the number for what you would like to do:\t> "))
    return input_command