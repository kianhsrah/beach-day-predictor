import requests
from pyzipcode import ZipCodeDatabase
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def get_zipcode(city, state):
    zcdb = ZipCodeDatabase()
    formatted_city = city.replace(" ", "_")
    results = zcdb.find_zip(city=formatted_city, state=state)
    
    if results:
        zip_codes = [result.zip for result in results]
        return zip_codes
    else:
        return f"No ZIP code found for {city}, {state}"

def get_lat_lon(zip_code, geocoding_api_key):
    base_url = "https://api.opencagedata.com/geocode/v1/json"
    params = {
        'q': zip_code,
        'key': geocoding_api_key
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    
    if response.status_code == 200 and data['results']:
        location = data['results'][0]['geometry']
        return location['lat'], location['lng']
    else:
        return None, None

def get_weather_data(lat, lon, weather_api_key):
    base_url = "http://api.openweathermap.org/data/3.0/onecall"
    params = {
        'lat': lat,
        'lon': lon,
        'exclude': 'minutely,hourly',
        'appid': weather_api_key,
        'units': 'imperial'
    }
    response = requests.get(base_url, params=params)
    weather = response.json()
    
    if response.status_code == 200:
        current_weather_info = {
            'Description': weather['current']['weather'][0]['description'],
            'Temp': weather['current']['temp'],
            'Feels Like': weather['current']['feels_like'],
            'Humidity': weather['current']['humidity'],
            'Speed': weather['current']['wind_speed'],
            'UV Index': weather['current']['uvi'],
            'Precipitation Probability': weather['daily'][0]['pop'] * 100
        }
        
        next_day_weather_info = {
            'Description': weather['daily'][1]['weather'][0]['description'],
            'Temp': weather['daily'][1]['temp']['day'],
            'Feels Like': weather['daily'][1]['feels_like']['day'],
            'Humidity': weather['daily'][1]['humidity'],
            'Speed': weather['daily'][1]['wind_speed'],
            'UV Index': weather['daily'][1]['uvi'],
            'Precipitation Probability': weather['daily'][1]['pop'] * 100
        }
        
        return current_weather_info, next_day_weather_info
    else:
        return f"Error fetching weather data: {weather.get('message', 'Unknown error')}"

def get_uv_warning(uv_index):
    if uv_index <= 2:
        return f"{uv_index} - Low Danger, No Protection Required"
    elif 3 <= uv_index <= 5:
        return f"{uv_index} - Medium Danger, Some Protection Required"
    elif 6 <= uv_index <= 7:
        return f"{uv_index} - High Danger, Some Protection Required"
    elif 8 <= uv_index <= 10:
        return f"{uv_index} - Very High Danger, Extra Protection Required"
    else:
        return f"{uv_index} - Extreme Danger, Be Well Protected!"

def check_beach_day(weather_info):
    stars = ""
    
    if 75 <= weather_info['Temp'] <= 90:
        stars += "⭐"
    if abs(weather_info['Temp'] - weather_info['Feels Like']) <= 5:
        stars += "⭐"
    if 0 <= weather_info['Speed'] <= 10:
        stars += "⭐"
    if 20 <= weather_info['Humidity'] <= 60:
        stars += "⭐"
    if weather_info['Precipitation Probability'] < 20:
        stars += "⭐"
        
    return stars

def format_weather_data(weather_info):
    return (
        f"Sky forecast: {weather_info['Description']}\n"
        f"Temperature: {weather_info['Temp']} Fº\n"
        f"Feels Like: {weather_info['Feels Like']} Fº\n"
        f"Humidity: {weather_info['Humidity']}%\n"
        f"Wind Speed: {weather_info['Speed']} MPH\n"
        f"Precipitation Probability: {weather_info['Precipitation Probability']}%\n"
    )

if __name__ == "__main__":
    city = input("Enter the city: ").strip().title()
    state = input("Enter the state abbreviation (ex. 'NJ' for New Jersey): ").strip().upper()
    weather_api_key = os.getenv("OPENWEATHERMAP_API_KEY")  # Load API key from environment variable
    geocoding_api_key = os.getenv("OPENCAGE_API_KEY")  # Load geocoding API key from environment variable
    zip_codes = get_zipcode(city, state)
    
    if isinstance(zip_codes, list):
        first_zip_code = zip_codes[0]
        lat, lon = get_lat_lon(first_zip_code, geocoding_api_key)
        
        if lat is not None and lon is not None:
            weather_data = get_weather_data(lat, lon, weather_api_key)
            if isinstance(weather_data, tuple):
                current_weather_data, next_day_weather_data = weather_data
                
                formatted_current_weather_data = format_weather_data(current_weather_data)
                print(f"Weather data for ZIP code {first_zip_code} (Today):\n\n{formatted_current_weather_data}")
                
                uv_warning_today = get_uv_warning(current_weather_data['UV Index'])
                stars_today = check_beach_day(current_weather_data)
                print(f"Beach day rating for {city}, {state} (Today):\nUV Index: {uv_warning_today}\n{stars_today} / ⭐⭐⭐⭐⭐")
                
                if len(stars_today) >= 5:
                    print("Yay beach day today!")
                elif len(stars_today) == 4:
                    print("Maybe beach day today.")
                else:
                    print("No beach day today...")
                
                formatted_next_day_weather_data = format_weather_data(next_day_weather_data)
                print(f"\nWeather data for ZIP code {first_zip_code} (Tomorrow):\n\n{formatted_next_day_weather_data}")
                
                uv_warning_tomorrow = get_uv_warning(next_day_weather_data['UV Index'])
                stars_tomorrow = check_beach_day(next_day_weather_data)
                print(f"Beach day rating for {city}, {state} (Tomorrow):\nUV Index: {uv_warning_tomorrow}\n{stars_tomorrow} / ⭐⭐⭐⭐⭐")
                
                if len(stars_tomorrow) >= 5:
                    print("Yay beach day tomorrow!\n")
                elif len(stars_tomorrow) == 4:
                    print("Maybe beach day tomorrow.\n")
                else:
                    print("No beach day tomorrow...\n")
            else:
                print(weather_data)  # Print the error message
        else:
            print(f"Error fetching latitude and longitude for ZIP code {first_zip_code}")
    else:
        print(zip_codes)
