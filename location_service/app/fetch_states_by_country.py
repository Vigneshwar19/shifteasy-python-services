from flask import jsonify
import pycountry

def fetch_states_by_country(country_name):
    country = pycountry.countries.get(name=country_name)
    if not country:
        return jsonify({"error": f"Country '{country_name}' not found."}), 404 

    subdivisions = pycountry.subdivisions.get(country_code=country.alpha_2)
    if not subdivisions:
        return jsonify({"error": f"No subdivisions found for country '{country_name}'."}), 404
    
    print(subdivisions)
    states_list = [subdivision.name for subdivision in subdivisions]
    return jsonify(states_list), 200  
