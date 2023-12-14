# filterSearch.py
import datetime
from decimal import Decimal
import sys
import time
import psycopg2

from dataclasses import dataclass

"""
Users will be able to search for video games by name, platform, release date, developers,
price, or genre. The resulting list of video games must show the video game’s name,
platforms, the developers, the publisher, the playtime and the ratings (age and user).
The list must be sorted alphabetically (ascending) by video game’s name and release
date. Users can sort the resulting list by: video game name, price, genre, and released
year (ascending and descending).
"""

@dataclass
class VideoGame:
    name: str
    platform: str
    release_date: datetime
    developer: str
    price: float
    genre: str

    publisher: str
    playtime: str
    esrb: str
    rating: float

"""
Args:
    conn (psycopg2.connection): The database connection.
    cur (psycopg2.cursor): The database cursor.
Returns:
    None
Raises:
    psycopg2.Error: If there is an error during the database operations.
"""
def filterSearch(conn, cur):
    try:
        valid_criteria = ["name", "platform", "release_date", "developer", "price", "genre"]
        result = []
        used_filters = []
        search_criteria = input("Enter which criterion you want to search by (ex: name, platform, release_date (by year), developer, price, genre): ").split(',')
        if len(search_criteria) == 0:
            print("No search criteria given!")
            filterSearch(conn, cur)

        for crit in search_criteria:
            if crit.strip() in valid_criteria and crit.strip() not in used_filters:
                used_filters.append(crit.strip())
            if crit.strip() not in valid_criteria:
                print(crit.strip(), "is not a valid search criteria, searching without", crit.strip())


        # Initialize an empty list to store the SQL conditions
        sql_conditions = []

        # Build the SQL conditions based on user input
        for crit in used_filters:
            if crit == "name":
                search_title = input("Title: ")
                sql_conditions.append(f"v.title ILIKE '%{search_title}%'")
            
            if crit == "platform":
                search_platform_name = input("Platform Name: ")
                sql_conditions.append(f"p.platform_name ILIKE '%{search_platform_name}%'")
            
            if crit == "release_date":
                search_release_date = input("Release date (year): ")
                while len(search_release_date) != 4:
                    search_release_date = input("Invalid Input - Release date (year): ")
                sql_conditions.append(f"EXTRACT(YEAR FROM a.release_date) = {search_release_date}")
            
            if crit == "developer":
                search_contributor_name = input("Contributor Name: ")
                sql_conditions.append(f"c1.contributor_name ILIKE '%{search_contributor_name}%'")
            
            if crit == "price":
                search_price = input("Price: ")
                while not isnum(search_price):
                    search_price = input("Invalid - enter a valid price: ")
                sql_conditions.append(f"a.price_per_platform <= {search_price}")
            
            if crit == "genre":
                search_genre_name = input("Genre Name: ")
                while search_genre_name.lower() not in ["fps", "rpg", "adventure", "simulation", "strategy", "sports",
                    "fitness", "fighting", "platformer", "survival", "horror", "stealth",
                    "puzzle", "party", "social deduction", "educational",
                    "augmented reality"]:
                    search_genre_name = input("Invalid genre, select from: 'fps', 'rpg', 'adventure', 'simulation', 'strategy', 'sports',"\
                        "'fitness', 'fighting', 'platformer', 'survival', 'horror', 'stealth',"\
                        "'puzzle', 'party', 'social deduction', 'educational',"\
                        "'augmented reality'")

                sql_conditions.append(f"g.genre_name ILIKE '%{search_genre_name}%'")

        # name, platforms, the developers, the publisher, the playtime and the ratings (age and user)
        # Construct the SQL query by joining the conditions with 'AND'
        sql_query = """
            SELECT
                v.title,
                p.platform_name,
                c1.contributor_name,
                a.price_per_platform,
                a.release_date,
                g.genre_name,
                c2.contributor_name,
                v.esrb_rating,
                COALESCE(AVG(r.star_rating), 0) AS user_rating,
                COALESCE(SUM(EXTRACT(EPOCH FROM (end_play_time - start_play_date_time)) / 3600), 0) AS playtime_hours
            FROM videogame v
            LEFT JOIN available_on a ON v.gameid = a.gameid
            LEFT JOIN platform p ON a.platformid = p.platformid
            LEFT JOIN develops d ON v.gameid = d.gameid
            LEFT JOIN publishes pu ON v.gameid = pu.gameid
            LEFT JOIN contributor c1 ON d.contributorid = c1.contributorid
            LEFT JOIN contributor c2 ON pu.contributorid = c2.contributorid
            LEFT JOIN video_game_genre vg ON v.gameid = vg.gameid
            LEFT JOIN genre g ON vg.genreid = g.genreid
            LEFT JOIN rates r ON v.gameid = r.gameid
            LEFT JOIN plays pl ON v.gameid = pl.gameid
            WHERE {}
            GROUP BY v.title, p.platform_name, g.genre_name, c1.contributor_name, c2.contributor_name, a.price_per_platform, a.release_date, v.esrb_rating
            ORDER BY v.title ASC
        """.format(" AND ".join(sql_conditions))

        # Execute the SQL query
        cur.execute(sql_query)
        

        # name, platform_name, developer, publisher, a.price_per_platform, release_date, esrb_rating
        # Fetch the results and print them
        rows = cur.fetchall()

        game_list = []

        for row in rows:
            video_game = VideoGame(
                name=row[0],
                platform=str(row[1]),
                developer=str(row[2]),
                price='{:.2f}'.format(float(row[3])),
                release_date=row[4],
                genre=str(row[5]),
                publisher=str(row[6]),
                esrb=str(row[7]),
                rating='{:.2f}'.format(float(row[8])),
                playtime=format_playtime(float(row[9]))
            )
            game_list.append(video_game)

        sort_loop(game_list, True, conn, cur)
    
    except (Exception, psycopg2.Error) as error:
        print("Error: ", error)

"""
Users can sort the resulting list by: video game name, price, genre, and released
year (ascending and descending)
"""
def sort_loop(game_list, relist, conn, cur):

    if relist:
        output_list(game_list)

    print("\nIn order to sort this list further, enter 'sort'")
    print("If you would like to start a new search, enter 'search'")
    print("If you would like to exit searching, enter 'return'")
    option = input()

    ascending = True
    if option == "sort":
        sort_by = input("\nIf you would like to sort by: \nVideo game name - 'name'\nPrice - 'price'\nGenre - 'genre' \nRelease Year - 'year'\nFollow this by if you want it in Ascending (a) or Descending (d) order, example input:    year, d\n")
        

        sort_by = sort_by.split(',')
        while len(sort_by) != 2:
            sort_by = input('Input must be two arguments (ex: year, a): ')
            sort_by = sort_by.split(',')

        
        sort_by[0] = sort_by[0].strip()
        sort_by[1] = sort_by[1].strip()
        
        while sort_by[1] != 'a' and sort_by[1] != 'd':
            sort_by[1] = input("Invalid order, please enter 'a' for ascending or 'd' for descending: ")

        if sort_by[1] == 'a':
            ascending = True
        if sort_by[1] == 'd':
            ascending = False
        
        while sort_by[0] != "name" and sort_by[0] != "price" and sort_by[0] != "genre" and sort_by[0] != "year":
            sort_by[0] = input("Invalid category, please enter by 'name', 'price', 'genre', or 'year")

        if sort_by[0] == "name":
            game_list = sorted(game_list, key=lambda game: game.name, reverse=not ascending)
        if sort_by[0] == "price":
            game_list = sorted(game_list, key=lambda game: game.price, reverse=not ascending)
        if sort_by[0] == "genre":
            game_list = sorted(game_list, key=lambda game: game.genre, reverse=not ascending)
        if sort_by[0] == "year":
            game_list = sorted(game_list, key=lambda game: game.release_date, reverse=not ascending)
        
        sort_loop(game_list, True, conn, cur)

    elif option == "search":
        filterSearch(conn, cur)
    elif option == "return":
        return
    else:
        print('\n', "Invalid input")
        sort_loop(game_list, False, conn, cur)

def output_list(game_list):
    # Define column headers
    header = "| {:<30} | {:<20} | {:<20} | {:<20} | {:<25} | {:<10} | {:<15} |".format(
        "Name", "Platform", "Developer", "Publisher", "Playtime", "ESRB Rating", "User Rating"
    )

    # Print the header
    print(header)

    # Print a separator line
    separator = "+{:<32}+{:<22}+{:<22}+{:<22}+{:<27}+{:<12}+{:<17}+".format(
        "-" * 30, "-" * 20, "-" * 20, "-" * 20, "-" * 10, "-" * 10, "-" * 15
    )
    print(separator)

    # Print each game's information
    for game in game_list:
        game_info = "| {:<30} | {:<20} | {:<20} | {:<20} | {:<25} | {:<10} | {:<15} |".format(
            game.name, game.platform, game.developer, game.publisher, game.playtime,
            game.esrb, game.rating
        )
        print(game_info)

def format_playtime(time):
        days = int(time // 24)
        hours = int(time % 24)
        return f"Days: {days}, Hours: {hours}"

def isnum(text):
    try:
        float(text)  # Try to convert the text to a floating-point number
        return True  # If successful, it's a valid number
    except ValueError:
        return False  # If a ValueError is raised, it's not a valid number
