from app.db import get_db_connection
from flask import jsonify

def fetch_area(latitude, longitude):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT 
                n.nearby_name, 
                n.state_code, 
                s.state_name,
                d.district_name,
                n.country_code, 
                n.country_name, 
                n.toponym_name, 
                n.population,
                ( 6371 * acos( cos( radians(%s) ) * cos( radians( n.latitude ) ) 
                * cos( radians( n.longitude ) - radians(%s) ) 
                + sin( radians(%s) ) * sin( radians( n.latitude ) ) ) ) AS distance_nearby,
                ( 6371 * acos( cos( radians(%s) ) * cos( radians( d.latitude ) ) 
                * cos( radians( d.longitude ) - radians(%s) ) 
                + sin( radians(%s) ) * sin( radians( d.latitude ) ) ) ) AS distance_district
            FROM geonames_schema.nearby n
            JOIN geonames_schema.states s 
                ON n.state_code = s.state_code
                AND n.country_code = s.country_code
            JOIN geonames_schema.districts d
                ON ( 6371 * acos( cos( radians(%s) ) * cos( radians( d.latitude ) ) 
                * cos( radians( d.longitude ) - radians(%s) ) 
                + sin( radians(%s) ) * sin( radians( d.latitude ) ) ) ) < 50
            WHERE 
                ( 6371 * acos( cos( radians(%s) ) * cos( radians( n.latitude ) ) 
                * cos( radians( n.longitude ) - radians(%s) ) 
                + sin( radians(%s) ) * sin( radians( n.latitude ) ) ) ) < 50
            ORDER BY distance_district, distance_nearby
            LIMIT 1;
        """
        # Haversine formula

        cursor.execute(query, (latitude, longitude, latitude, latitude, longitude, latitude, latitude, longitude, latitude, latitude, longitude, latitude))

        result = cursor.fetchone()

        print(result)
        
        if result:
            response = {
                "nearbyName": result[0],
                "stateCode": result[1],
                "stateName": result[2],
                "district": result[3],
                "countryCode": result[4],
                "country": result[5],
                "toponymName": result[6],
                "population": result[7]
            }

            return jsonify(response)

        else:
            return jsonify({"message": "No area found within the specified radius."}), 404

    except Exception as e:
        print(f"Error in database: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()
