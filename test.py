from flask import Flask, request, jsonify, render_template 
from bson.objectid import ObjectId
import requests
import pymongo
import os
from dotenv import load_dotenv
from loguru import logger


MONGO_URI = "mongodb://localhost:27017/weatherDB"
client = pymongo.MongoClient(MONGO_URI)
db = client.weatherDB
weather_collection = db.weather_searches

history = list(weather_collection.find())
history = history[0]
del history["_id"]
print(jsonify(history))