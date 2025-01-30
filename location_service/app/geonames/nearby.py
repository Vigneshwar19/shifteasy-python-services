import requests
import concurrent.futures
from app.db import get_db_connection, create_schema_and_table_for_geonames
from utils.needs import get_next_username

def save_nearby_data_to_db_batch(nearby_data_list):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO geonames_schema.nearby (
            nearby_name, state_code, admin_name1, admin_code1, admin_codes1_iso3166_2, 
            country_code, country_id, country_name, fcl, fcl_name, fcode, fcode_name, 
            geoname_id, latitude, longitude, population, toponym_name, country_geoname_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (geoname_id) DO NOTHING;
        """
        cursor.executemany(insert_query, nearby_data_list)

        conn.commit()
        cursor.close()
        conn.close()
        print(f"{len(nearby_data_list)} rows saved successfully!")

    except Exception as e:
        print(f"Error saving state data to database: {e}")

def get_geoname_id_by_district_name(district_name):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        find_query = """
        SELECT geoname_id FROM geonames_schema.districts WHERE district_name = %s LIMIT 1;
        """

        cursor.execute(find_query, (district_name,))

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

def get_all_nearby(district_name):
    geoname_id = get_geoname_id_by_district_name(district_name)
    print("geoname_id: ", geoname_id)

    while True:
        username = get_next_username()
        print(f"Username: {username}")
        url = f"http://api.geonames.org/childrenJSON?geonameId={geoname_id}&username={username}"
        response = requests.get(url)
        print(f"Response for district name {district_name} using {username}: ", response.json())

        if response.status_code == 200:
            nearby_data = response.json()

            if "status" in nearby_data and "value" in nearby_data["status"] and nearby_data["status"]["value"] == 19:
                print(f"Hourly limit exceeded for username: {username}")
                continue 

            query = """
            CREATE TABLE IF NOT EXISTS geonames_schema.nearby (
                nearby_id SERIAL PRIMARY KEY,
                nearby_name VARCHAR(100), 
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

            nearby_data_list = []
            for nearby in nearby_data['geonames']:
                nearby_data_list.append((
                    nearby['name'],
                    nearby.get('adminCodes1', {}).get('ISO3166_2', None),
                    nearby['adminName1'],
                    nearby['adminCode1'],
                    nearby.get('adminCodes1', {}).get('ISO3166_2', None),
                    nearby['countryCode'],
                    nearby['countryId'],
                    nearby['countryName'],
                    nearby['fcl'],
                    nearby['fclName'],
                    nearby['fcode'],
                    nearby['fcodeName'],
                    nearby['geonameId'],
                    nearby['lat'],
                    nearby['lng'],
                    nearby['population'],
                    nearby['toponymName'],
                    nearby['countryId']
                ))

            save_nearby_data_to_db_batch(nearby_data_list)
            return nearby_data

        else:
            print(f"Failed to fetch nearby. Status code: {response.status_code}")
            return {"error": f"Failed to fetch nearby. Status code: {response.status_code}"}

def get_all_district_names():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT DISTRICT_NAME 
            FROM GEONAMES_SCHEMA.DISTRICTS
            WHERE COUNTRY_CODE NOT IN (
                SELECT DISTINCT COUNTRY_CODE 
                FROM GEONAMES_SCHEMA.NEARBY
            );
        """
        cursor.execute(query)
        
        district_names = cursor.fetchall()
        return [row[0] for row in district_names] 

    except Exception as e:
        print(f"Error in database: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def fetch_and_save_nearby_data_for_district(district_name):
    try:
        nearby_data = get_all_nearby(district_name)
        if 'error' not in nearby_data:
            print(f"Successfully saved data for district: {district_name}")
        else:
            print(f"Failed to save data for district: {district_name}")
    except Exception as e:
        print(f"Error fetching data for {district_name}: {e}")

def fetch_and_save_all_nearby():
    district_names = get_all_district_names()

    futures = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(fetch_and_save_nearby_data_for_district, district_name) for district_name in district_names]
    
    for future in concurrent.futures.as_completed(futures):
        try:
            future.result()
        except Exception as e:
            print(f"An error occurred: {e}")
    
    return {"status": "success", "message": "Data fetching and saving process completed."}

