import requests
import os
from app.db import get_db_connection, create_schema_and_table_for_geonames
from dotenv import load_dotenv

load_dotenv()

username = os.getenv('GEONAMES_USERNAME')

def save_districts_data_to_db(district_data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO geonames_schema.districts (
            district_name, state_code, admin_name1, admin_code1, admin_codes1_iso3166_2, 
            country_code, country_id, country_name, fcl, fcl_name, fcode, fcode_name, 
            geoname_id, latitude, longitude, population, toponym_name, country_geoname_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (geoname_id) DO NOTHING;  
        """

        for district in district_data['geonames']:
            cursor.execute(insert_query, (
                district['name'],                              
                district.get('adminCodes1', {}).get('ISO3166_2', None),  
                district['adminName1'],                        
                district['adminCode1'],                       
                district.get('adminCodes1', {}).get('ISO3166_2', None),  
                district['countryCode'],                       
                district['countryId'],                         
                district['countryName'],                       
                district['fcl'],                            
                district['fclName'],                          
                district['fcode'],                             
                district['fcodeName'],                       
                district['geonameId'],                        
                district['lat'],                               
                district['lng'],                               
                district['population'],                        
                district['toponymName'],                       
                district['countryId']                          
            ))

        conn.commit()
        cursor.close()
        conn.close()
        print("District data saved successfully!")

    except Exception as e:
        print(f"Error saving district data to database: {e}")

def fetch_all_states_with_countries():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        SELECT state_code, country_code FROM geonames_schema.states;
        """
        cursor.execute(query)
        
        state_country_data = cursor.fetchall()
        return [(row[0], row[1]) for row in state_country_data] 

    except Exception as e:
        print(f"Error in database: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_geoname_id_by_state_code(state_code, country_code):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        find_query = """
        SELECT geoname_id FROM geonames_schema.states WHERE state_code = %s AND country_code = %s LIMIT 1;
        """

        cursor.execute(find_query, (state_code, country_code,))

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

def get_all_districts(state_code, country_code):
    geoname_id = get_geoname_id_by_state_code(state_code, country_code)
    print("geoname_id: ", geoname_id)
    url = f"http://api.geonames.org/childrenJSON?geonameId={geoname_id}&country={country_code}&username={username}"
    response = requests.get(url)
    print(f"respose for state code {state_code} and country code {country_code}: ", response.json())

    if response.status_code == 200:
        country_data = response.json()
        query = """
        CREATE TABLE IF NOT EXISTS geonames_schema.districts (
            district_id SERIAL PRIMARY KEY,                  
            district_name VARCHAR(100),                    
            state_code VARCHAR(10),                         
            admin_name1 VARCHAR(100),                       
            admin_code1 VARCHAR(10),                       
            admin_codes1_iso3166_2 VARCHAR(10),         
            country_code VARCHAR(10),                     
            country_id BIGINT,                            
            country_name VARCHAR(100),                     
            fcl CHAR(1),                                    
            fcl_name VARCHAR(255),                          
            fcode VARCHAR(50),                              
            fcode_name VARCHAR(255),                        
            geoname_id BIGINT UNIQUE NOT NULL,              
            latitude DOUBLE PRECISION,                      
            longitude DOUBLE PRECISION,                     
            population BIGINT,                              
            toponym_name VARCHAR(100),                      
            country_geoname_id BIGINT,                      
            FOREIGN KEY (country_geoname_id) REFERENCES geonames_schema.countries(geoname_id) ON DELETE CASCADE
        );

        """
        create_schema_and_table_for_geonames(query)
        save_districts_data_to_db(country_data)
        return country_data
    else:
        return {"error": f"Failed to fetch countries. Status code: {response.status_code}"}

def fetch_and_save_all_districts():
    states_with_countries = fetch_all_states_with_countries()
    print('states and countries: ', states_with_countries, len(states_with_countries))

    error_occurred = False
    
    for state_code, country_code in states_with_countries:
        print(f"Fetching districts for state code and country code: {state_code} {country_code}")
        state_data = get_all_districts(state_code, country_code)
        
        if 'error' not in state_data:
            print(f"Districts for {state_code} saved successfully!")
            print("-" * 100)
        else:
            print(f"Error for {state_code}: {state_data['error']}")
            error_occurred = True

    if error_occurred:
        return {"status": "error", "message": "Some errors occurred while fetching district data."}
    else:
        return {"status": "success", "message": "All districts data fetched and saved successfully!"}

