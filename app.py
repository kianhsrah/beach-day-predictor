from flask import Flask, render_template, request, url_for
import os
from dotenv import load_dotenv
from beach_day_predictor import get_zipcode, get_lat_lon, get_weather_data, get_uv_warning, check_beach_day, format_weather_data

app = Flask(__name__)
load_dotenv()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/weather', methods=['POST'])
def weather():
    city = request.form['city'].strip().title()
    state = request.form['state'].strip().upper()
    weather_api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    geocoding_api_key = os.getenv("OPENCAGE_API_KEY")
    zip_codes = get_zipcode(city, state)
    
    if isinstance(zip_codes, list):
        first_zip_code = zip_codes[0]
        lat, lon = get_lat_lon(first_zip_code, geocoding_api_key)
        
        if lat is not None and lon is not None:
            weather_data = get_weather_data(lat, lon, weather_api_key)
            if isinstance(weather_data, tuple):
                current_weather_data, next_day_weather_data = weather_data
                
                formatted_current_weather_data = format_weather_data(current_weather_data)
                uv_warning_today = get_uv_warning(current_weather_data['UV Index'])
                stars_today = check_beach_day(current_weather_data)
                
                formatted_next_day_weather_data = format_weather_data(next_day_weather_data)
                uv_warning_tomorrow = get_uv_warning(next_day_weather_data['UV Index'])
                stars_tomorrow = check_beach_day(next_day_weather_data)
                
                return render_template('result.html', city=city, state=state, current_weather=formatted_current_weather_data,
                                       uv_today=uv_warning_today, stars_today=stars_today, next_weather=formatted_next_day_weather_data,
                                       uv_tomorrow=uv_warning_tomorrow, stars_tomorrow=stars_tomorrow)
            else:
                return render_template('error.html', message=weather_data)
        else:
            return render_template('error.html', message=f"Error fetching latitude and longitude for ZIP code {first_zip_code}")
    else:
        return render_template('error.html', message=zip_codes)

if __name__ == "__main__":
    app.run(debug=True)
