# for_you.py

import psycopg2
from dataclasses import dataclass
from typing import List, Optional
import popular_20_last_90_days


# Assuming you have a Game data class
@dataclass
class Game:
    title: str
    gameid: int
    esrb_rating: str
    user_rating: Optional[float]
    platform_id: Optional[int]
    developer_id: Optional[int]
    genre_id: Optional[int]

@dataclass
class DisplayableGame:
	title: str
	genre: str
	rating: float
	platform: str
	developer: str
	esrb: str

# Main For You function call, gives recommendations based on user preferences and similar usersed
def for_you(conn, cur, user_id):
	user_games = get_user_games(conn, cur, user_id)
	
	print("--------------------------------------")
	print("Recommended based of your preferences:")
	print("--------------------------------------")

	# List to hold all recommended games
	rec_games = list()

	if len(rec_games) == 0:
		print("\nSince you haven't played any games yet...")
		print("Here's the top 20 games of the past 3 Months:\n")
		popular_20_last_90_days.most_popular_90_days(conn, cur, user_id)
	else:
		# Add games based off preferences to that list, call pref_recs()
		rec_games.extend(pref_recs(conn, cur, user_id, user_games))

		# Add games based off similar users to that list, call collection_recs()
		rec_games.extend(collection_recs(conn, cur, user_id, user_games))

		rec_games = sorted(rec_games, key=lambda x: x.rating, reverse=True)
		output_list(rec_games)

def get_user_games(conn, cur, user_id):
    try:
        sql_query = """
            SELECT DISTINCT
		vg.title,
		pl.gameid,
                vg.esrb_rating,
                r.star_rating AS user_rating,
                ao.platformid,
                d.contributorid AS developer_id,
                vgg.genreid
            FROM plays pl
            JOIN videogame vg ON pl.gameid = vg.gameid
            LEFT JOIN video_game_genre vgg ON vg.gameid = vgg.gameid
            LEFT JOIN develops d ON vg.gameid = d.gameid
            LEFT JOIN rates r ON pl.userid = r.userid AND pl.gameid = r.gameid
            LEFT JOIN available_on ao ON pl.gameid = ao.gameid
            WHERE pl.userid = %s;
        """
        cur.execute(sql_query, (user_id,))
        game_list = [Game(*row) for row in cur.fetchall()]
        return game_list
    
    except (Exception, psycopg2.Error) as error:
        print("Error: ", error)

def pref_recs(conn, cur, user_id, user_games):
	user_played_genres = set()
	user_played_platforms = set()
	user_played_ratings = set()
	user_played_developers = set()

	# Create parameters for next query by using sets
	for game in user_games:
		user_played_genres.add(game.genre_id)
		user_played_platforms.add(game.platform_id)
		user_played_ratings.add(game.esrb_rating)
		user_played_developers.add(game.developer_id)

	# All ratings under highest played rating
	user_played_ratings = rec_esrb(user_played_ratings)

	# Convert all sets to tuples for query to read
	user_played_genres = tuple(user_played_genres)
	user_played_platforms = tuple(user_played_platforms)
	user_played_ratings = tuple(user_played_ratings)
	user_played_developers = tuple(user_played_developers)

	try:
		sql_query = """
			SELECT
				vg.title,
				AVG(r.star_rating) AS average_user_rating,
				g.genre_name,
				c.contributor_name,
				p.platform_name,
				vg.esrb_rating
			FROM videogame vg
			LEFT JOIN video_game_genre vgg ON vg.gameid = vgg.gameid
			LEFT JOIN develops d ON vg.gameid = d.gameid
			LEFT JOIN rates r ON vg.gameid = r.gameid
			LEFT JOIN available_on ao ON vg.gameid = ao.gameid
			LEFT JOIN genre g ON vgg.genreid = g.genreid
			LEFT JOIN contributor c ON d.contributorid = c.contributorid
			LEFT JOIN platform p ON ao.platformid = p.platformid
			WHERE (vgg.genreid IN %s
				AND ao.platformid IN %s
				AND vg.esrb_rating IN %s
				AND vg.gameid NOT IN (
					SELECT pl.gameid
					FROM plays pl
					WHERE pl.userid = %s
				))
				OR (ao.platformid IN %s
				AND vg.esrb_rating IN %s
				AND d.contributorid IN %s
				AND vg.gameid NOT IN (
					SELECT pl.gameid
					FROM plays pl
					WHERE pl.userid = %s
				))
			GROUP BY vg.title, g.genre_name, c.contributor_name, p.platform_name, vg.esrb_rating
			ORDER BY average_user_rating DESC;

		"""
		cur.execute(sql_query, (user_played_genres, user_played_platforms,
			user_played_ratings, user_id, user_played_platforms,
			user_played_ratings, user_played_developers, user_id))
		
		recommended_games = cur.fetchall()
		final_recs = list()
		seen_game_plat = list() # holds tuples on if a game was already seen on the same platform
		for row in recommended_games:
			title, average_user_rating, genre, developer, platform, esrb = row
			game_plat = (title, platform)
			if game_plat in seen_game_plat:
				continue

			seen_game_plat.append(game_plat)

			if average_user_rating is None:
				average_user_rating = 2.80
			
			if developer is None:
				continue
			
			title_seen = False
			for game in final_recs:
				if game.title == title:
					game.platform += ", "
					game.platform += platform
					title_seen = True
					
			if not title_seen:	
				final_recs.append(DisplayableGame(title, genre, round(average_user_rating, 2), platform, developer, esrb))

		count = 0
		display_list = list()
		for row in final_recs:
			display_list.append(row)
			#count += 1
			#if count == 10:
			#	break
		
		return display_list
		
	except (Exception, psycopg2.Error) as error:
		print("Error: ", error)

            
# Find the max ESRB rating a user has played
# This is used so games that are rated 'M' won't be recommended
#	   to users who only play games rated 'E'...
def rec_esrb(ratings):
	rec_esrbs = set()

	for esrb in ratings:
		if esrb == "M":
			rec_esrbs.add("E")
			rec_esrbs.add("E10+")
			rec_esrbs.add("T")
			rec_esrbs.add("M")
			rec_esrbs.add("RP")

		elif esrb == "T":
			rec_esrbs.add("E")
			rec_esrbs.add("E10+")
			rec_esrbs.add("T")

		elif esrb == "E10+":
			rec_esrbs.add("E")
			rec_esrbs.add("E10+")

		elif esrb == "E":
			rec_esrbs.add("E")

	return rec_esrbs


def collection_recs(conn, cur, user_id, user_games):

	user_played_platforms = set()
	user_played_ratings = set()

	for game in user_games:
		user_played_platforms.add(game.platform_id)
		user_played_ratings.add(game.esrb_rating)

	# All ratings under highest played rating
	user_played_ratings = rec_esrb(user_played_ratings)

	# Convert all sets to tuples for query to read
	user_played_platforms = tuple(user_played_platforms)
	user_played_ratings = tuple(user_played_ratings)

	try:
		sql_query = """
			WITH UserCollections AS (
			SELECT DISTINCT pc.collectionid
			FROM part_of_collection pc
			JOIN plays p ON pc.gameid = p.gameid
			WHERE p.userid = %s
			GROUP BY pc.collectionid
			)
			, OtherCollections AS (
			SELECT DISTINCT pc.gameid
			FROM part_of_collection pc
			WHERE pc.collectionid IN (SELECT collectionid FROM UserCollections)
			AND pc.collectionid NOT IN (
				SELECT collectionid
				FROM creates_collection cc
				WHERE cc.userid = %s
			)
			)
			SELECT DISTINCT g.title, 
				AVG(r.star_rating) AS average_user_rating,
				ge.genre_name,
				c.contributor_name,
				p.platform_name,
				g.esrb_rating
			FROM videogame g
			LEFT JOIN video_game_genre vgg on g.gameid = vgg.gameid
			LEFT JOIN develops d ON g.gameid = d.gameid
			LEFT JOIN rates r ON g.gameid = r.gameid
			LEFT JOIN available_on ao ON g.gameid = ao.gameid
			LEFT JOIN genre ge ON vgg.genreid = ge.genreid
			LEFT JOIN contributor c ON d.contributorid = c.contributorid
			LEFT JOIN platform p ON ao.platformid = p.platformid
			WHERE g.gameid IN (SELECT gameid FROM OtherCollections)
			AND g.gameid NOT IN (
			SELECT pl.gameid
			FROM plays pl
			WHERE pl.userid = %s
			)
			AND ao.platformid IN %s
			AND g.esrb_rating IN %s 
			GROUP BY g.title, ge.genre_name, c.contributor_name, p.platform_name, g.esrb_rating
			ORDER BY average_user_rating DESC;
		"""

		cur.execute(sql_query, (user_id, user_id, user_id, user_played_platforms, user_played_ratings,))
		recommended_games = cur.fetchall()

		returned_games = list()
		for game in recommended_games:
			title, rating, genre, developer, platform, esrb = game
			title_seen = False
			if rating is None:
				rating = 3.00

			for check in returned_games:
				if check.title == title:
					check.platform += ", "
					check.platform += platform
					title_seen = True
			if not title_seen:
				returned_games.append(DisplayableGame(title, genre, round(rating, 2), platform, developer, esrb))
		
		return returned_games

	except (Exception, psycopg2.Error) as error:
		print("Error: ", error)
		
def output_list(game_list):
    # Define column headers
    header = "| {:<40} | {:<20} | {:<25} | {:<25} | {:<10} | {:<15} |".format(
        "Name", "Platform", "Developer", "Genre", "ESRB Rating", "Rating"
    )

    # Print the header
    print(header)

    # Print a separator line
    separator = "+{:<42}+{:<22}+{:<27}+{:<27}+{:<12}+{:<17}+".format(
        "-" * 40, "-" * 20, "-" * 25, "-" * 25, "-" * 10, "-" * 15
    )
    print(separator)

    # Print each game's information
    for game in game_list:
        game_info = "| {:<40} | {:<20} | {:<25} | {:<25} | {:<10} | {:<15} |".format(
            game.title, game.platform, game.developer, game.genre, game.esrb, game.rating
        )
        print(game_info)