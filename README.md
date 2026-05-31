# OpenWeather Data Pipeline

**Description:**
A Python project that fetches weather data from the [OpenWeather API](https://openweathermap.org/api), processes it, and stores it in a database. Designed to run as a scheduled cron job.

---

## **Features**
- Fetches current weather data for specified locations using OpenWeather API
- Processes and cleans the data
- Stores data in a MySQL database
- Logs errors and successful runs
- Ready for automation via cron

---

## **Project Structure**

## **Prerequisites**
- Python 3.8+
- OpenWeather API key (https://openweathermap.org/api))
- MySQL database
- Required Python packages:  `requests`, `dotenv`, `os`, `logging`, `mysql.connector`

---

## **Setup**
1. Clone the repository
2. Get API key from https://openweathermap.org/api
3. Create .env file to store API credentials and MySQL credentials
