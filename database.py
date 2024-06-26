import mysql.connector
from mysql.connector import Error
import json

def create_connection():
    """Create a database connection and return the connection object."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Ldh@2073",
            database="wages"
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

        # Prepare data for insertion
        persons_json = json.dumps(persons)
        person_expenses_json = json.dumps(person_expenses)

        # Insert new record
        insert_query = """
        INSERT INTO trips (period, total_income, persons, payer, person_expenses, comment)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        insert_data = (period, total_income, persons_json, payer, person_expenses_json, comment)
        cursor.execute(insert_query, insert_data)
        print(f"Inserted data for period: {period}")

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
    query = "SELECT DISTINCT period FROM trips"
    results = fetch_query(query)
    if results:
        return [result['period'] for result in results]
    return []

def get_period(period):
    """Retrieve the most recent data for a specific period."""
    query = "SELECT * FROM trips WHERE period = %s ORDER BY id DESC LIMIT 1"
    result = fetch_query(query, (period,))
    if result:
        result = result[0]
        try:
            result['persons'] = json.loads(result['persons'])
            result['person_expenses'] = json.loads(result['person_expenses'])
        except KeyError as e:
            print(f"KeyError: {e}")
            print(f"Result data: {result}")
    return result

