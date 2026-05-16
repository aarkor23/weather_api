import requests
from dotenv import load_dotenv
import os

load_dotenv()  # Loads the .env file


def get_geocoding(city, country_code, limit= 1):
    # Input validation
    if not city or not country_code:
        raise ValueError("City and country code must be provided")
    if not isinstance(limit, int) or limit <= 0:
        raise ValueError("Limit must be an integer greater than 0")

    # Loading API key
    api_key = os.getenv("api_key")
    if not api_key:
        raise ValueError("API key not found.")

    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city},{country_code}&limit={limit}&appid={api_key}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data:
            return data[0]['lat'], data[0]['lon']
        else:
            raise ValueError("No coordinates found.")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None



def get_weather(lat, lon):
    if not lat or not lon:
        raise ValueError("Latitude and longitude coordinates must be provided.")

        # Loading API key
    api_key = os.getenv("api_key")
    if not api_key:
        raise ValueError("API key not found.")

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None





