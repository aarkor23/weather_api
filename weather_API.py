import requests
from dotenv import load_dotenv
import os
import logging
import mysql.connector

# Loading .env file
load_dotenv()

# Basic configuration: log level, format, and output destination
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s', # Specifies the log message format.
    handlers=[
        logging.FileHandler("pipeline.log"),  # Log to a file named "pipeline.log"
        logging.StreamHandler()               # Log to console
    ]
)

logger = logging.getLogger(__name__) # creates a logger object unique to the current module.
logger.info("Pipeline starts...")

# function to retrieve coordinates
def get_geocoding(city, country_code, limit= 1):
    # Input validation
    if not city or not country_code:
        logger.info("City and country code are not provided.")
        raise ValueError("City and country code must be provided.")

    if not isinstance(limit, int) or limit <= 0:
        logger.info("Limit is not an integer greater than 0.")
        raise ValueError("Limit must be an integer greater than 0")

    logger.info(f"Fetching geocoding for city: {city}, country: {country_code}")

    # Loading API key
    api_key = os.getenv("api_key")
    if not api_key:
        logger.error("API key not found.")
        raise ValueError("API key not found.")

    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city},{country_code}&limit={limit}&appid={api_key}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data:
            return data[0]['lat'], data[0]['lon']
        else:
            logger.info("No coordinates found.")
            raise ValueError("No coordinates found.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error: {e}")
        print(f"Error: {e}")
        return None


# function to retrieve weather data
def get_weather(lat, lon):
    if not lat or not lon:
        raise ValueError("Latitude and longitude coordinates must be provided.")

        # Loading API key
    api_key = os.getenv("api_key")
    if not api_key:
        logger.error(f"API key not found.")
        raise ValueError("API key not found.")

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

lat, lon = get_geocoding("Auckland", "NZ")
weather_data = get_weather(lat, lon)


# function to get needed data from API call
def select_data(data):
    logger.info("Data is selected for import to database.")
    selected_data = {
        "id": data["id"],
        "timestamp": data["dt"],
        "timezone": data["timezone"],
        "windspeed": data["wind"]["speed"],
        "country": data["sys"]["country"],
        "city": data["name"],
        "humidity": data["main"]["humidity"],
        "pressure": data["main"]["pressure"],
        "temp": data["main"]["temp"],
        "temp_max": data["main"]["temp_max"],
        "temp_min": data["main"]["temp_min"]
    }
    return selected_data

extracted_data = select_data(weather_data)

# function to connect to database(MySQL)
def db_connect():
    # Load file with credentials to log into DB
    logger.info(f"Loading credentials for database.")
    load_dotenv()

    try:
        logger.info("Trying to connect to the database...")
        db = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        logger.info("Successfully connected to the database.")
    except mysql.connector.Error as err:
        logger.error(f"Database connection error: {err}")
        raise
    return db

def execute_query(db, query, params=None):
    try:
        with db.cursor() as cursor:
            logger.info(f"Executing query: {query}")
            cursor.execute(query, params or ())
            result = cursor.fetchall()
            logger.info(f"Query {query} executed successfully.")
            db.commit()
            logger.info("Query was committed successfully.")
            return result
    except mysql.connector.Error as err:
        logger.error(f"Database query error: {err}")
        raise


# SQL query to check if table exists
current_weather_table = """
    CREATE TABLE IF NOT EXISTS current_weather (
        id INTEGER,
        timestamp INTEGER,
        timezone INTEGER,
        windspeed FLOAT,
        country VARCHAR(50),
        city VARCHAR(50),
        humidity INTEGER,
        pressure INTEGER,
        temp FLOAT,
        temp_max FLOAT,
        temp_min FLOAT
)
"""
# SQL query to insert data
current_weather_insert = """
INSERT INTO current_weather (id, timestamp, timezone, windspeed, country, city, humidity, pressure, temp, temp_max, temp_min)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s)
"""

# extracting values
params = (
    extracted_data["id"],
    extracted_data["timestamp"],
    extracted_data["timezone"],
    extracted_data["windspeed"],
    extracted_data["country"],
    extracted_data["city"],
    extracted_data["humidity"],
    extracted_data["pressure"],
    extracted_data["temp"],
    extracted_data["temp_max"],
    extracted_data["temp_min"]
)

# Execute queries to load data
db = db_connect()
execute_query(db, current_weather_table)
execute_query(db, current_weather_insert, params)



