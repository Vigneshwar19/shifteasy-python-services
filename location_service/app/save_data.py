from app.db import get_db_connection, create_schema_and_table

def save_geocode_data_to_db(address):
    create_schema_and_table()

    customer_id = address.get('customerId')
    latitude = address.get('latitude')
    longitude = address.get('longitude')

    road = address.get('road')
    neighbourhood = address.get('neighbourhood')
    suburb = address.get('suburb')
    city = address.get('city')
    state_district = address.get('state_district')
    state = address.get('state')
    iso3166_2_lvl4 = address.get('ISO3166-2-lvl4')
    postcode = address.get('postcode')
    country = address.get('country')
    country_code = address.get('country_code')

    connection = get_db_connection()
    cursor = connection.cursor()

    insert_query = """
        INSERT INTO location.address_details (
            customerId, latitude, longitude, road, neighbourhood, suburb, city, state_district,
            state, iso3166_2_lvl4, postcode, country, country_code
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """

    address_data = (
        customer_id, latitude, longitude, road, neighbourhood, suburb, city, state_district,
        state, iso3166_2_lvl4, postcode, country, country_code
    )

    cursor.execute(insert_query, address_data)

    connection.commit()
    cursor.close()
    connection.close()

    print("Data saved successfully!")
