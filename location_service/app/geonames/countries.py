import requests
import os
from app.db import get_db_connection, create_schema_and_table_for_geonames
from dotenv import load_dotenv

load_dotenv()

username = os.getenv('GEONAMES_USERNAME')

def save_country_data_to_db(country_data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO geonames_schema.countries (
            country_name, capital, continent, country_code, currency_code, population, 
            area_in_sq_km, postal_code_format, languages, north, south, east, west, geoname_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (geoname_id) DO NOTHING; 
        """

        for country in country_data['geonames']:
            cursor.execute(insert_query, (
                country['countryName'],
                country['capital'],
                country['continentName'],
                country['countryCode'],
                country['currencyCode'],
                country['population'],
                country['areaInSqKm'],
                country['postalCodeFormat'],
                country['languages'],
                country['north'],
                country['south'],
                country['east'],
                country['west'],
                country['geonameId']
            ))

        conn.commit()
        cursor.close()
        conn.close()
        print("Data saved successfully!")

    except Exception as e:
        print(f"Error saving data to database: {e}")

def get_all_countries():
    url = f"http://api.geonames.org/countryInfoJSON?username={username}"
    response = requests.get(url)

    if response.status_code == 200:
        country_data = response.json()
        query = """
        CREATE TABLE IF NOT EXISTS geonames_schema.countries (
            country_id SERIAL PRIMARY KEY,
            country_name VARCHAR(100),
            capital VARCHAR(100),
            continent VARCHAR(255),
            country_code VARCHAR(10),
            currency_code VARCHAR(10),
            population BIGINT,
            area_in_sq_km FLOAT,
            postal_code_format VARCHAR(255),
            languages VARCHAR(255),
            north DOUBLE PRECISION,
            south DOUBLE PRECISION,
            east DOUBLE PRECISION,
            west DOUBLE PRECISION,
            geoname_id BIGINT UNIQUE NOT NULL
        );
        """
        create_schema_and_table_for_geonames(query)
        save_country_data_to_db(country_data)
        return country_data
    else:
        return {"error": f"Failed to fetch countries. Status code: {response.status_code}"}
