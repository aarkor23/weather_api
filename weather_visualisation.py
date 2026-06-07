from dotenv import load_dotenv
import os
import logging
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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
logger.info("Visualisation process starts...")

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


# Retrieve data from DB
load_weather_data = """
SELECT timestamp, city, temp, temp_min, temp_max, humidity, windspeed
FROM current_weather_2
ORDER BY timestamp DESC
"""

logger.info("Loading weather data into dataframe.")
df = pd.read_sql(load_weather_data, db_connect())

# Convert Unix data
logger.info("Converting timestamp into date object.")
df["time"] = pd.to_datetime(df["timestamp"], unit="s")

# Convert from Fahrenheit to Celsius
def temperature_conversion(data):
    temp_cols = data.filter(like="temp").columns
    data[temp_cols] = data[temp_cols] - 273.15
    logger.info("Temperature conversion from Kelvin to Celsius completed.")
    return data

temperature_conversion(df)

def plot_temperature(data):
    logger.info("Plotting temperature plot.")
    fig, ax = plt.subplots(figsize=(12,6))

    for city, group in data.groupby("city"):
        group = group.sort_values(by="time")
        line, =ax.plot(group["time"], group["temp"], marker="o", label=city)
        ax.fill_between(group["time"], group["temp_min"], group["temp_max"],color=line.get_color(), alpha=0.2)

    ax.set_title("Temperature over Time")
    ax.set_xlabel("Time")
    ax.set_ylabel("Temperature")
    ax.legend()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H:%M"))
    plt.show()

plot_temperature(df)






