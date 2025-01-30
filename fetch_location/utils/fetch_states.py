from app.db import get_db_connection

def country_code_from_country_name(country):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            select country_code from geonames_schema.countries
            where UPPER(country_name) = %s LIMIT 1;
        """
        cursor.execute(query, (country.upper(),))
        
        country_code = cursor.fetchone()

        if country_code:
            return country_code[0]
        else:
            return None

    except Exception as e:
        print(f"Error in database: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def fetch_states(country):
    try:
        country_code = country_code_from_country_name(country)
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "select state_name from geonames_schema.states where UPPER(country_code) = %s;"
        cursor.execute(query, (country_code.upper(),))
        
        states = cursor.fetchall()
        return [row[0] for row in states] 

    except Exception as e:
        print(f"Error in database: {e}")
        return []
    finally:
        cursor.close()
        conn.close()