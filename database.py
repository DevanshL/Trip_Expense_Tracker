import mysql.connector
from mysql.connector import Error
import os

def create_connection():
    """Create a database connection and return the connection object."""
    try:
        host = os.getenv('DB_HOST', 'default_host')
        user = os.getenv('DB_USER', 'default_user')
        password = os.getenv('DB_PASSWORD', 'default_password')
        database = os.getenv('DB_NAME', 'default_database')

        print(f"Connecting to database at {host} with user {user}")

        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            return connection
        else:
            print("Failed to connect to MySQL database")
    except Error as e:
        print(f"Error: {e}")
    return None

def execute_query(query, data=None):
    """Execute a single query."""
    connection = create_connection()
    if connection is None:
        print("Failed to create database connection.")
        return False
    try:
        cursor = connection.cursor()
        if data:
            cursor.execute(query, data)
        else:
            cursor.execute(query)
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except Error as e:
        print(f"Error: {e}")
        if connection:
            connection.rollback()
            cursor.close()
            connection.close()
        return False

def fetch_query(query, data=None):
    """Fetch data from the database."""
    connection = create_connection()
    if connection is None:
        print("Failed to create database connection.")
        return None
    try:
        cursor = connection.cursor(dictionary=True)
        if data:
            cursor.execute(query, data)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        return result
    except Error as e:
        print(f"Error: {e}")
        if connection:
            cursor.close()
            connection.close()
        return None

def insert_period(period, total_income, persons, payer, person_expenses, comment):
    """Insert data for a given period without deleting existing data."""
    connection = create_connection()
    if connection is None:
        print("Failed to create database connection.")
        return False
    
    try:
        cursor = connection.cursor()

        # Prepare and insert data for each person
        for person in persons:
            extra = person_expenses[person].get('extra', 0)
            shopping = person_expenses[person].get('Shopping', 0)
            transport = person_expenses[person].get('Transport', 0)
            accommodation = person_expenses[person].get('Accommodation', 0)
            entertainment = person_expenses[person].get('Entertainment', 0)
            miscellaneous = person_expenses[person].get('Miscellaneous', 0)
            food_drinks = person_expenses[person].get('Food and Drinks', 0)

            insert_query = """
            INSERT INTO trip_expenses (period, total_income, name, payer, extra, shopping, transport, accommodation, entertainment, miscellaneous, food_drinks, comment)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            insert_data = (period, total_income, person, payer, extra, shopping, transport, accommodation, entertainment, miscellaneous, food_drinks, comment)
            cursor.execute(insert_query, insert_data)
            print(f"Inserted data for person: {person}, period: {period}")

        connection.commit()
        cursor.close()
        connection.close()
        return True

    except Error as e:
        print(f"Error: {e}")
        if connection:
            connection.rollback()
            cursor.close()
            connection.close()
        return False

def get_all_periods():
    """Retrieve all periods from the database."""
    query = "SELECT DISTINCT period FROM trip_expenses"
    results = fetch_query(query)
    if results:
        return [result['period'] for result in results]
    return []

def get_period(period):
    """Retrieve data for a specific period."""
    query = "SELECT * FROM trip_expenses WHERE period = %s"
    result = fetch_query(query, (period,))
    return result

