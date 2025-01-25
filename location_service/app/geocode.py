import requests
from app.config import Config

def fetch_address_from_geocode(latitude, longitude, customerId):
    try:
        params = {
            "lat": latitude,
            "lon": longitude,
            "format": "json"
        }
        headers = {"User-Agent": "location/1.0 (location@gmail.com)"}

        response = requests.get(Config.NOMINATIM_URL, params=params, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        address = data.get("address")
        address['latitude'] = latitude
        address['longitude'] = longitude
        address['customerId'] = customerId
        return address
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return {"error": "Error fetching address"}
