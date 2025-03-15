from flask import Flask, request, jsonify, render_template
from bson.objectid import ObjectId
import requests
import pymongo
import os
import json
import csv
import pdfkit
from dotenv import load_dotenv
from loguru import logger
from flask_cors import CORS


load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:10000"}}) 

logger.add("app.log", rotation="10MB", level="DEBUG")  #log file

# MongoDB Configuration
MONGO_URI = "mongodb://localhost:27017/weatherDB"
client = pymongo.MongoClient(MONGO_URI)
db = client.weatherDB
weather_collection = db.weather_searches

# OpenWeatherMap API Key
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")  # Stored in .env file

# Function to get latitude & longitude from city name
def get_lat_lon(city):
    geocode_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid=7dff46e67950916775740d2f068e79bc"
    response = requests.get(geocode_url)

    logger.debug(f"Geocode API Response for {city}: {response.json()}")

    if response.status_code != 200 or not response.json():
        logger.error(f"Invalid location: {city}")
        return None, None

    data = response.json()[0]
    return data["lat"], data["lon"]

@app.route("/")
def home():
    logger.info("Home page accessed")
    return render_template("index.html")

@app.route("/weather", methods=["GET"])
def get_weather():
    location = request.args.get("location")
    date_range = request.args.get("date_range", "latest")  #Allow date range input

    if not location:
        return jsonify({"error": "Location is required"}), 400

    lat, lon = get_lat_lon(location)
    if lat is None or lon is None:
        return jsonify({"error": "Invalid location"}), 400

    # Fetch Weather Data
    weather_url = f"http://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid=7dff46e67950916775740d2f068e79bc&units=metric"
    response = requests.get(weather_url)

    if response.status_code != 200:
        return jsonify({"error": "Failed to retrieve weather data"}), 400

    data = response.json()

    # Extracting the Weather Data
    weather_data = {
    "location": location,
    "date_range": date_range,
    "current_weather": {
        "temperature": data["current"]["temp"],
        "weather": data["current"]["weather"][0]["description"],
        "feels_like": data["current"]["feels_like"],
        "humidity": data["current"]["humidity"],
        "wind_speed": data["current"]["wind_speed"],
        "icon": data["current"]["weather"][0]["icon"],
    },
    # Hourly Forecast
    "hourly_forecast": [
        {
            "time": h["dt"],
            "temp": h["temp"],
            "icon": h["weather"][0]["icon"],  
            "weather": h["weather"][0]["description"], 
        }
        for h in data["hourly"][:5]
    ],
    # Fixed Daily Forecast
    "daily_forecast": [ 
        {
            "date": d["dt"],
            "min_temp": d["temp"]["min"],
            "max_temp": d["temp"]["max"],
            "icon": d["weather"][0]["icon"],  
            "weather": d["weather"][0]["description"],  
        }
        for d in data["daily"][:5]
    ],
}

    inserted_data = weather_collection.insert_one(weather_data)
    weather_data["_id"] = str(inserted_data.inserted_id)
    return jsonify(weather_data)

# UPDATE: Modify stored weather data
@app.route("/update", methods=["PUT"])
def update_weather():
    data = request.json
    record_id = data.get("_id")
    updated_data = data.get("updated_data")

    if not record_id or not updated_data:
        return jsonify({"error": "Missing record ID or data"}), 400

    weather_collection.update_one(
        {"_id": ObjectId(record_id)}, {"$set": updated_data}
    )
    return jsonify({"message": "Weather data updated successfully"}), 200

# DELETE: Remove a record
@app.route("/delete", methods=["DELETE"])
def delete_weather():
    record_id = request.args.get("_id")
    if not record_id:
        return jsonify({"error": "Missing record ID"}), 400

    weather_collection.delete_one({"_id": ObjectId(record_id)})
    return jsonify({"message": "Weather data deleted successfully"}), 200

# EXPORT: Convert stored data into JSON, CSV, or PDF
def clean_data(data):
    for record in data:
        record["_id"] = str(record["_id"])
    return data

@app.route("/export", methods=["GET"])
def export_data():
    export_format = request.args.get("format", "json").lower()
    history = list(weather_collection.find())

    if not history:
        return jsonify({"error": "No data found"}), 404

    history = clean_data(history)

    if export_format == "json":
        return jsonify(history)

    elif export_format == "csv":
        csv_filename = "weather_data.csv"
        with open(csv_filename, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=history[0].keys())
            writer.writeheader()
            writer.writerows(history)
        return send_file(csv_filename, as_attachment=True)

    elif export_format == "pdf":
        pdf_filename = "weather_data.pdf"
        pdfkit.from_string(json.dumps(history, indent=4), pdf_filename)
        return send_file(pdf_filename, as_attachment=True)

    else:
        return jsonify({"error": "Invalid format. Use json, csv, or pdf."}), 400
    
@app.route("/info", methods=["GET"])
def project_info():
    info = {
        "developer": "Rohit Aralikatti",
        "project": "Weather App with Google Maps & YouTube Integration",
        "description": "This project fetches live weather data, visualizes locations on Google Maps, and integrates YouTube for location-based videos.",
        "linkedin": "https://www.linkedin.com/school/pmaccelerator/"
    }
    return jsonify(info)



