
import requests

def get_iss_location():
    """
    Fetches the current location of the International Space Station.
    Returns a dictionary with latitude, longitude, and other data.
    """

    url = "http://api.open-notify.org/iss-now.json"

    try:

        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        location = {
            "latitude": float(data["iss_position"]["latitude"]),
            "longitude": float(data["iss_position"]["longitude"]),
            "timestamp": data["timestamp"]
        }
        return location

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def format_location_string():
    """
    Returns a formatted string of the ISS's current location.
    """
    location = get_iss_location()
    if location:
        return (f"The ISS is currently located at:\n"
                f"Latitude: {location['latitude']}\n"
                f"Longitude: {location['longitude']}")
    return "Could not retrieve ISS location."