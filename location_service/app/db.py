import psycopg2
from app.config import Config

def get_db_connection():
    try:
        print(Config.DB_NAME, Config.DB_USER, Config.DB_PASSWORD, Config.DB_HOST, Config.DB_PORT)
        connection = psycopg2.connect(
            dbname=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            host=Config.DB_HOST,
            port=Config.DB_PORT
        )
        print("Database connection successful")
        return connection
    except Exception as e:
        print(f"Error while connecting to PostgreSQL: {e}")
        return None
    
def create_schema_and_table_for_geonames(query):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        create_schema_query = """
        CREATE SCHEMA IF NOT EXISTS geonames_schema;
        """
        cursor.execute(create_schema_query)

        create_table_query = query

        cursor.execute(create_table_query)

        connection.commit()
        cursor.close()
        connection.close()
        print("Schema and table are ready!")

    except Exception as e:
        print(f"Error creating schema and table: {e}")

def create_schema_and_table():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE SCHEMA IF NOT EXISTS location;

        CREATE TABLE IF NOT EXISTS location.address_details (
            id SERIAL PRIMARY KEY,
            customerId BIGINT,
            latitude DOUBLE PRECISION NOT NULL,
            longitude DOUBLE PRECISION NOT NULL,
            road VARCHAR(255),
            neighbourhood VARCHAR(255),
            suburb VARCHAR(255),
            city VARCHAR(255),
            state_district VARCHAR(255),
            state VARCHAR(255),
            iso3166_2_lvl4 VARCHAR(10),
            postcode VARCHAR(20),
            country VARCHAR(255),
            country_code VARCHAR(10)
        );
    """)

    connection.commit()
    cursor.close()
    connection.close()
