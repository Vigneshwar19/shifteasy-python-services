from app.geocode import fetch_address_from_geocode
from app.save_data import save_geocode_data_to_db

def handle_geocode_request(latitude, longitude, customerId):
    address = fetch_address_from_geocode(latitude, longitude, customerId)
    print(address)
    if address:
        print("address available")
        save_geocode_data_to_db(address)
        return address
    else:
        print("Failed to fetch address, not saving to database.")
