# Trip Expense Tracker

This project is a Trip Expense Tracker application built using Streamlit for the front end, PostgreSQL for the database, and Python for backend processing.

## Setup and Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/DevanshL/Trip_Expense_Tracker.git
    cd Trip_Expense_Tracker
    ```

2. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Configure database connection**:
    Update the database connection details in `database.py`:
    ```python
    import psycopg2
    from psycopg2 import Error

    def create_connection():
        """Create a database connection and return the connection object."""
        try:
            connection = psycopg2.connect(
                host="dpg-cpugl7dds78s73dsdg5g-a.oregon-postgres.render.com",
                database="wages",
                user="wages_user",
                password="0pm7WU6IpCiqnOcCeZ95Vv3H8QUP1pK7"
            )
            if connection:
                print("Connected to PostgreSQL database")
                return connection
            else:
                print("Failed to connect to PostgreSQL database")
        except Error as e:
            print(f"Error: {e}")
        return None
    ```

4. **Create the database table**:
    Run the `database.py` script to create the necessary tables in your PostgreSQL database:
    ```bash
    python database.py
    ```
    This will connect to your PostgreSQL database and create the `trip_expenses` table.

5. **Run the Streamlit app**:
    ```bash
    streamlit run app.py
    ```

## Usage

- **Data Entry**: Enter trip details, including total income, number of persons, their names, and expenses for each category.
- **Data Visualization**: View a summary of the trip expenses, including a Sankey chart for visual representation of the data.

## Database Structure

The `trip_expenses` table is structured as follows:
- `period`: VARCHAR
- `total_income`: INTEGER
- `name`: VARCHAR
- `payer`: VARCHAR
- `extra`: INTEGER
- `shopping`: INTEGER
- `transport`: INTEGER
- `accommodation`: INTEGER
- `entertainment`: INTEGER
- `miscellaneous`: INTEGER
- `food_drinks`: INTEGER
- `comment`: TEXT

## Screenshots

1. **Data Entry**:
   ![1](https://github.com/DevanshL/Trip_Expense_Tracker/blob/main/Images/1.png?raw=true)
   ![2](https://github.com/DevanshL/Trip_Expense_Tracker/blob/main/Images/2.png?raw=true)
   ![3](https://github.com/DevanshL/Trip_Expense_Tracker/blob/main/Images/3.png?raw=true)
   ![4](https://github.com/DevanshL/Trip_Expense_Tracker/blob/main/Images/4.png?raw=true)

3. **SQL Connection and Database**:
   ![SQL Connection](https://github.com/DevanshL/Trip_Expense_Tracker/blob/main/Images/connection.png?raw=true)
   ![Database Result](https://github.com/DevanshL/Trip_Expense_Tracker/blob/main/Images/sql.png?raw=true)

   - **Database of Hosted Website**:
   - ![Hosted SQL Connection](https://github.com/DevanshL/Trip_Expense_Tracker/blob/main/Images/onlin_sql_connection.png?raw=true)
   - ![Hosted Database Result](https://github.com/DevanshL/Trip_Expense_Tracker/blob/main/Images/hosted_database.png?raw=true)

5. **Data Visualization**:
   ![Data Visualization](https://github.com/DevanshL/Trip_Expense_Tracker/blob/main/Images/plot_of_expenses.png?raw=true)

## SQL Connection in Local Terminal

To connect to your PostgreSQL database from your local terminal, use the following command:
```bash
PGPASSWORD=0pm7WU6IpCiqnOcCeZ95Vv3H8QUP1pK7 psql -h dpg-cpugl7dds78s73dsdg5g-a.oregon-postgres.render.com -U wages_user wages
```

## PostgreSQL Connection Steps

- Open your terminal.
- Run the following command:
  ```PGPASSWORD=0pm7WU6IpCiqnOcCeZ95Vv3H8QUP1pK7 psql -h dpg-cpugl7dds78s73dsdg5g-a.oregon-postgres.render.com -U wages_user wages```
- You should see a connection established:
  ![Sample Connection](https://github.com/DevanshL/Trip_Expense_Tracker/blob/main/Images/sample_connection.png?raw=true)

## Hosted Website
You can access the hosted version of the Trip Expense Tracker at the following link:
[hosted link](https://trip-expense-tracker-7.onrender.com/)

## License
This project is licensed under the MIT License.
