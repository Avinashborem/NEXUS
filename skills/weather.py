# skills/weather.py — Real Weather via OpenWeatherMap
import requests
from config import CITY

def get_weather(city=None):
    from config import OPENWEATHER_KEY
    try:
        target = city if city else CITY
        url = (f"https://api.openweathermap.org/data/2.5/weather"
               f"?q={target}&appid={OPENWEATHER_KEY}&units=metric")
        r = requests.get(url, timeout=5)
        data = r.json()
        if data.get("cod") != 200:
            return f"Couldn't get weather for {target}."
        temp     = round(data["main"]["temp"])
        feels    = round(data["main"]["feels_like"])
        humidity = data["main"]["humidity"]
        desc     = data["weather"][0]["description"]
        wind     = round(data["wind"]["speed"] * 3.6)
        name     = data["name"]
        return (f"Weather in {name}: {desc}. "
                f"{temp} degrees, feels like {feels}. "
                f"Humidity {humidity} percent, wind {wind} kilometers per hour.")
    except Exception as e:
        return f"Weather fetch failed: {e}"