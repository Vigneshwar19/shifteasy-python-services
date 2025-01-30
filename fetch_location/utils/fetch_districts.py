from app.db import get_db_connection
from utils.fetch_states import country_code_from_country_name

def state_code_from_state_name(state):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        SELECT state_code 
        FROM geonames_schema.states
        WHERE UPPER(state_name) = %s 
        LIMIT 1;
        """
        cursor.execute(query, (state.upper(),))
        
        state_code = cursor.fetchone()

        if state_code:
            return state_code[0]
        else:
            return None

    except Exception as e:
        print(f"Error in database: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def fetch_districts(state, country):
    try:
        state_code = state_code_from_state_name(state)
        country_code = country_code_from_country_name(country)
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT NEARBY_NAME AS LOCATION_NAME
            FROM GEONAMES_SCHEMA.NEARBY
            WHERE COUNTRY_CODE = %s
            AND STATE_CODE = %s

            UNION

            SELECT DISTRICT_NAME AS LOCATION_NAME
            FROM GEONAMES_SCHEMA.DISTRICTS
            WHERE COUNTRY_CODE = %s
            AND STATE_CODE = %s

            UNION

            SELECT AREA_NAME AS LOCATION_NAME
            FROM GEONAMES_SCHEMA.AREAS
            WHERE COUNTRY_CODE = %s
            AND STATE_CODE = %s

            ORDER BY LOCATION_NAME ASC;
        """
        cursor.execute(query, (country_code.upper(), state_code.upper(), country_code.upper(), state_code.upper(), country_code.upper(), state_code.upper(),))
        
        states = cursor.fetchall()
        return [row[0] for row in states] 

    except Exception as e:
        print(f"Error in database: {e}")
        return []
    finally:
        cursor.close()
        conn.close()