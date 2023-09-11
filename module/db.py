import psycopg2
from psycopg2 import Error
import os
from dotenv import load_dotenv
load_dotenv()

host = os.environ['POSTGRES_HOST']
database = os.environ['POSTGRES_DATABASE']
user = os.environ['POSTGRES_USER']
password = os.environ['POSTGRES_PASSWORD']

# Database connection details

def execute_sql_command(sql_command):
    cursor = None  # Initialize cursor to None

    connection = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password
    )

    try:
        cursor = connection.cursor()
        cursor.execute(sql_command)
        connection.commit()
        if cursor.description is None:
            return None
        columns = [desc[0] for desc in cursor.description]

        # Fetch the query result
        result = cursor.fetchall()
        # Convert the result to the desired format
        formatted_result = [{columns[i]: value for i, value in enumerate(row)} for row in result]

        return formatted_result

    except Error as e:
        # Handle the database error and return error message as response
        error_message = {"error": e.pgcode, "message": e.pgerror, "arg":e.args}
        raise Exception(error_message)

    finally:
        if cursor is not None:
            cursor.close()  # Close the cursor if it is not None

        if connection is not None:
            connection.close()  # Close the connection