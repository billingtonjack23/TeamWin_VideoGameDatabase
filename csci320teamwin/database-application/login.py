"""
@Filename: login.py
@Author: Team Win
"""
from datetime import date
import psycopg2

"""
Updates the Last_access_time field in the player table

Args:
    conn: The database connection
    cur: The database cursor
    username: username of user that just logged in
    password: password of user that just logged in

Return:
    userID: the userID of the player to use in the main file
"""
def update_access_date(conn, cur, username, password):
    try:
        #Find a userID using username and password
        sql = "SELECT userID from PLAYER WHERE username = %s AND password = %s"
        val = (username, password)
        cur.execute(sql, val)
        sql_call = cur.fetchall()
        userID = sql_call[0]

        #Updates Last_access_date to reflect last access
        sql = "UPDATE player SET Last_access_date = NOW() WHERE userID = %s"
        val = (userID)
        cur.execute(sql, val)
        conn.commit()

        return userID
    
    except (Exception, psycopg2.Error) as error:
        print("Error: ", error)

"""
Inserts a user and all fields into the player table

Args:
    conn: The database connection
    cur: The database cursor
    user_fields: all fields to be inserted already filled by user

Return:
    userID: the userID of the player to use in the main file
"""
def insert_user(conn, cur, user_fields):

    try:
        #Create a new and unique ID
        sql = "SELECT max(UserID)+1 FROM player"
        cur.execute(sql)
        sql_call = cur.fetchall()
        userID = sql_call[0]

        #Insert a player into the table

        #cur.execute("INSERT INTO player (UserID, Username, FirstName, 
        # LastName, Password, Last_access_date, Creation_date, Email) VALUES 
        # (%s, %s, %s)", (userID ,user_fields[0], user_fields[2], user_fields[3], "password_test",
        #  user_fields[6]))
        
        #cur.execute("INSERT INTO player (UserID, Username, FirstName, LastName, 
        # Password, Last_access_date, Creation_date, Email) VALUES "(userID ,user_fields[0], 
        # user_fields[2], user_fields[3], s"user_fields[1]", user_fields[6]))

        sql = "INSERT INTO player (UserID, Username, FirstName, LastName, Password, Last_access_date, Creation_date, Email) VALUES (%s, %s, %s, %s, %s, NOW(), NOW(), %s)"
        val = (userID ,user_fields[0], user_fields[2], user_fields[3], user_fields[1], user_fields[6])
        cur.execute(sql, val)
        conn.commit()

        return userID
    
    except (Exception, psycopg2.Error) as error:
        print("Error: ", error)


"""
If the user does not already exist, then register a new account and 
save the credentials in credentials.json

Args:
    n/a

Return:
    player_obj: a list that returns all credentials for a 
    user for a user in SQL
"""
def register_usr():

    #All inputs for creating a player in table
    username = input("Enter a username: ")
    password = input("Enter a password: ")
    firstname = input("Enter your first name: ")
    lastName = input("Enter a last name: ")
    email = input("Enter your email address: ")

    player_obj = [
        username, password, firstname, lastName, 
        str(date.today()), str(date.today()), email
    ]

    return player_obj


"""
Prompts the user for input to log them into the database or register
themselves as a user for the database

Args:
    n/a

Return:
    ret_lst: a list that returns the username and password to login
"""
def prompt_loop():
    while(True):            #Will always be true but return out in conditionals             

        #Prompt for login or register
        init_question = input("Do you already have an existing account? (Y/N): ")
        if init_question == "Y":                    #Login
            username = input("Enter username: ")
            password = input("Enter password: ")
            ret_lst = [username, password]
            return ret_lst
        elif init_question == "N":                  #Register
            player_obj = register_usr()
            return player_obj
        else:                                       #Loop until 'Y' or 'N'
            print("Please enter a valid option")    

