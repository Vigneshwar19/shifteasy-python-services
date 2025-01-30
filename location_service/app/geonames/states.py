import requests
import os
from app.db import get_db_connection, create_schema_and_table_for_geonames
from dotenv import load_dotenv

load_dotenv()

username = os.getenv('GEONAMES_USERNAME')

def save_states_data_to_db(state_data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO geonames_schema.states (
            state_name, state_code, admin_name1, country_code, geoname_id, latitude, longitude, population, country_geoname_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (geoname_id) DO NOTHING;
        """

        for state in state_data['geonames']:
            cursor.execute(insert_query, (
                state['name'],
                state['adminCodes1']['ISO3166_2'],
                state['adminName1'],
                state['countryCode'],
                state['geonameId'],
                state['lat'],
                state['lng'],
                state['population'],
                state['countryId']
            ))

        conn.commit()
        cursor.close()
        conn.close()
        print("state data saved successfully!")

    except Exception as e:
        print(f"Error saving state data to database: {e}")

def get_all_country_codes():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "SELECT country_code FROM geonames_schema.countries;"
        cursor.execute(query)
        
        country_codes = cursor.fetchall()
        return [row[0] for row in country_codes] 

    except Exception as e:
        print(f"Error in database: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_geoname_id_by_country_code(country_code):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        find_query = """
        SELECT geoname_id FROM geonames_schema.countries WHERE country_code = %s LIMIT 1;
        """

        cursor.execute(find_query, (country_code,))

        result = cursor.fetchone()
        
        if result:
            return result[0]
        else:
            return None

    except Exception as e:
        print(f"Error in database: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def get_all_states(country_code):
    geoname_id = get_geoname_id_by_country_code(country_code)
    print("geoname_id: ", geoname_id)
    url = f"http://api.geonames.org/childrenJSON?geonameId={geoname_id}&username={username}"
    response = requests.get(url)
    print(f"respose for country code {country_code}: ", response.json())

    if response.status_code == 200:
        country_data = response.json()
        query = """
        CREATE TABLE IF NOT EXISTS geonames_schema.states (
            state_id SERIAL PRIMARY KEY,
            state_name VARCHAR(100),
            state_code VARCHAR(10),
            admin_name1 VARCHAR(100),
            country_code VARCHAR(10),
            geoname_id BIGINT UNIQUE NOT NULL,
            latitude DOUBLE PRECISION,
            longitude DOUBLE PRECISION,
            population BIGINT,
            country_geoname_id BIGINT,
            FOREIGN KEY (country_geoname_id) REFERENCES geonames_schema.countries(geoname_id) ON DELETE CASCADE
        );
        """
        create_schema_and_table_for_geonames(query)
        save_states_data_to_db(country_data)
        return country_data
    else:
        return {"error": f"Failed to fetch countries. Status code: {response.status_code}"}

def fetch_and_save_all_states():
    country_codes = get_all_country_codes()
    print('country_codes', country_codes, len(country_codes))
    
    error_occurred = False
    
    for country_code in country_codes:
        print(f"Fetching states for country code: {country_code}")
        country_data = get_all_states(country_code)
        
        if 'error' not in country_data:
            print(f"States for {country_code} saved successfully!")
            print("-" * 100)
        else:
            print(f"Error for {country_code}: {country_data['error']}")
            error_occurred = True

    if error_occurred:
        return {"status": "error", "message": "Some errors occurred while fetching state data."}
    else:
        return {"status": "success", "message": "All states data fetched and saved successfully!"}

