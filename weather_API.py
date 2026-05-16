import requests
from dotenv import load_dotenv
import os


def get_weather(city,country_code, limit):
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city},{country_code}&limit={limit}&appid={api_key}"