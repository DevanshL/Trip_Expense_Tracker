import os
import psycopg2
from psycopg2 import Error

def create_connection():
    """Create a database connection and return the connection object."""
    try:
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        if connection:
            print("Connected to PostgreSQL database")
            return connection
        else:
            print("Failed to connect to PostgreSQL database")
    except Error as e:
        print(f"Error: {e}")
    return None

def create_table():
    create_table_query = """
    CREATE TABLE IF NOT EXISTS trip_expenses (
        id SERIAL PRIMARY KEY,
        period VARCHAR(255) NOT NULL,
        total_income INTEGER NOT NULL,
        name VARCHAR(255) NOT NULL,
        payer VARCHAR(255) NOT NULL,
        extra INTEGER DEFAULT 0,
        shopping INTEGER DEFAULT 0,
        transport INTEGER DEFAULT 0,
        accommodation INTEGER DEFAULT 0,
        entertainment INTEGER DEFAULT 0,
        miscellaneous INTEGER DEFAULT 0,
        food_drinks INTEGER DEFAULT 0,
        comment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute(create_table_query)
            connection.commit()
            cursor.close()
            connection.close()
            print("Table created successfully")
        except Error as e:
            print(f"Error: {e}")
            if connection:
                connection.rollback()
                cursor.close()
                connection.close()

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
    connection = create_connection()
    if connection is None:
        print("Failed to create database connection.")
        return None
    try:
        cursor = connection.cursor()
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
    query = "SELECT DISTINCT period FROM trip_expenses"
    results = fetch_query(query)
    if results:
        return [result[0] for result in results]
    return []

def get_period(period):
    query = "SELECT * FROM trip_expenses WHERE period = %s"
    result = fetch_query(query, (period,))
    return result

if __name__ == "__main__":
    os.environ["DB_HOST"] = "dpg-cpugl7dds78s73dsdg5g-a.oregon-postgres.render.com"
    os.environ["DB_NAME"] = "wages"
    os.environ["DB_USER"] = "wages_user"
    os.environ["DB_PASSWORD"] = "0pm7WU6IpCiqnOcCeZ95Vv3H8QUP1pK7"
    
    create_table()
