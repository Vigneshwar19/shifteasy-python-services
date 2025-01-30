import requests
import concurrent.futures
from app.db import get_db_connection, create_schema_and_table_for_geonames
from utils.needs import get_next_username

def save_area_data_to_db_batch(area_data_list):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        insert_query = """
            INSERT INTO geonames_schema.areas (
                area_name, state_code, admin_name1, admin_name2, admin_name3,
                country_code, latitude, longitude, postal_code, nearby_name
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
        """
        cursor.executemany(insert_query, area_data_list)

        conn.commit()
        cursor.close()
        conn.close()
        print(f"{len(area_data_list)} rows saved successfully!")

    except Exception as e:
        print(f"Error saving state data to database: {e}")

def get_all_areas(nearby_name):

    while True:
        username = get_next_username()
        print(f"Username: {username}")
        url = f"http://api.geonames.org/postalCodeSearchJSON?placename={nearby_name}&username={username}"
        response = requests.get(url)
        print(f"Response for nearby name {nearby_name} using {username}: ", response.json())

        if response.status_code == 200:
            area_data = response.json()

            if "status" in area_data and "value" in area_data["status"] and area_data["status"]["value"] == 19:
                print(f"Hourly limit exceeded for username: {username}")
                continue 

            query = """
                CREATE TABLE IF NOT EXISTS geonames_schema.areas (
                    area_id SERIAL PRIMARY KEY,
                    area_name VARCHAR(100), 
                    state_code VARCHAR(10),                  
                    admin_name1 VARCHAR(100), 
                    admin_name2 VARCHAR(100), 
                    admin_name3 VARCHAR(100),         
                    country_code VARCHAR(10),             
                    latitude DOUBLE PRECISION,                      
                    longitude DOUBLE PRECISION,                             
                    postal_code VARCHAR(50),
                    nearby_name VARCHAR(100)                     
                );
            """
            create_schema_and_table_for_geonames(query)

            area_data_list = []
            for area in area_data.get('postalCodes', []):
                area_data_list.append((
                    area.get('placeName'),
                    area.get('ISO3166-2'),
                    area.get('adminName1'),
                    area.get('adminName2'),
                    area.get('adminName3'),
                    area.get('countryCode'),
                    area.get('lat'),
                    area.get('lng'),
                    area.get('postalCode'),
                    nearby_name
                ))
            
            save_area_data_to_db_batch(area_data_list)
            return area_data

        else:
            print(f"Failed to fetch area. Status code: {response.status_code}")
            return {"error": f"Failed to fetch area. Status code: {response.status_code}"}

def get_all_nearby_names():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT NEARBY_NAME
            FROM GEONAMES_SCHEMA.NEARBY
            WHERE STATE_CODE = 'WLS';
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

def fetch_and_save_area_data_for_nearby_names(nearby_name):
    try:
        area_data = get_all_areas(nearby_name)
        if 'error' not in area_data:
            print(f"Successfully saved data for nearby_name: {nearby_name}")
        else:
            print(f"Failed to save data for nearby_name: {nearby_name}")
    except Exception as e:
        print(f"Error fetching data for {nearby_name}: {e}")

def fetch_and_save_all_areas():
    nearby_names = get_all_nearby_names()
    print("nearby_names: ", len(nearby_names))
    futures = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(fetch_and_save_area_data_for_nearby_names, nearby_name) for nearby_name in nearby_names]
    
    for future in concurrent.futures.as_completed(futures):
        try:
            future.result()
        except Exception as e:
            print(f"An error occurred: {e}")
    
    return {"status": "success", "message": "Data fetching and saving process completed."}
