import requests

username="shifteasy"

def search_location(country_name, query, max_rows=10):
    url = f"http://api.geonames.org/searchJSON?q={query}&maxRows={max_rows}&country={country_name}&username={username}"
    response = requests.get(url)
    return response.json()

def search_postal_code(postal_code, country):
    url = f"http://api.geonames.org/postalCodeSearchJSON?postalcode={postal_code}&country={country}&username={username}"
    response = requests.get(url)
    return response.json()

def get_country_info(country):
    url = f"http://api.geonames.org/countryInfoJSON?country={country}&username={username}"
    response = requests.get(url)
    return response.json()

def get_siblings(geoname_id):
    url = f"http://api.geonames.org/siblingsJSON?geonameId={geoname_id}&username={username}"
    response = requests.get(url)
    return response.json()

def search_districts_in_state(state_code, country_code):
    url = f"http://api.geonames.org/childrenJSON?geonameId={state_code}&country={country_code}&username={username}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to fetch districts. Status code: {response.status_code}"}

