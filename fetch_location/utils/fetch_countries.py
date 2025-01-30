from app.db import get_db_connection

def fetch_countries():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "select country_name from geonames_schema.countries;"
        cursor.execute(query)
        
        countries = cursor.fetchall()
        return [row[0] for row in countries] 

    except Exception as e:
        print(f"Error in database: {e}")
        return []
    finally:
        cursor.close()
        conn.close()