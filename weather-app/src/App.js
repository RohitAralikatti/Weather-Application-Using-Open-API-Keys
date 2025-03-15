import React, { useState } from "react";
import axios from "axios";
import "./App.css";
import GoogleMapComponent from "./GoogleMapComponent";

function App() {
  const [location, setLocation] = useState("");
  const [weatherData, setWeatherData] = useState(null);
  const [error, setError] = useState("");

  const fetchWeather = async () => {
    if (!location) {
      setError("Please enter a location.");
      return;
    }

    try {
      const response = await fetch(`http://127.0.0.1:5000/weather?location=${location}`);
      const data = await response.json();
      setWeatherData(data);
      setError("");
      console.log(data);
    } catch (err) {
      setError("Error fetching weather data. Please try again.");
      console.error(err);
    }
  };

  // Function to show PM Accelerator Info
  const showInfo = () => {
    alert("PM Accelerator helps aspiring and current product managers accelerate their careers. Learn more: https://www.linkedin.com/school/pmaccelerator/");
  };

  return (
    <div className="container">
      <h1>Weather App</h1>
      <p>Developed by <strong>Rohit Aralikatti</strong></p>
      
      <input
        type="text"
        placeholder="Enter city name"
        value={location}
        onChange={(e) => setLocation(e.target.value)}
      />
      <button onClick={fetchWeather}>Get Weather</button>
      <button className="info-button" onClick={showInfo}>Info</button>

      {error && <p className="error">{error}</p>}

      {weatherData && (
        <div className="weather-container">
          <h2>Current Weather in {weatherData.location}</h2>
          <p>Temperature: {weatherData.current_weather.temperature}°C</p>
          <p>Humidity: {weatherData.current_weather.humidity}%</p>
          <p>Wind Speed: {weatherData.current_weather.wind_speed} m/s</p>
          <p>Condition: {weatherData.current_weather.weather}</p>
          <img 
            src={`http://openweathermap.org/img/wn/${weatherData.current_weather.icon}.png`} 
            alt="Weather icon" 
          />
        </div>
      )}
    </div>
  );
}

export default App;
