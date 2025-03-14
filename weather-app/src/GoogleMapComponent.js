import React from "react";
import { GoogleMap, LoadScript, Marker } from "@react-google-maps/api";

const containerStyle = {
  width: "100%",
  height: "400px",
};

const center = {
  lat: 40.7128, // Default latitude (New York)
  lng: -74.0060, // Default longitude (New York)
};

const GoogleMapComponent = ({ location }) => {
  return (
    <LoadScript googleMapsApiKey="AIzaSyA7kRlDE5MT82rep9q2UuRBXnX_m31zDVw">
      <GoogleMap mapContainerStyle={containerStyle} center={center} zoom={10}>
        {location && <Marker position={location} />}
      </GoogleMap>
    </LoadScript>
  );
};

export default GoogleMapComponent;
