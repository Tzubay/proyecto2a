from config import OPENWEATHER_API_KEY

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


async def get_weather_by_coordinates(session, lat, lon):
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
        "lang": "es"
    }

    async with session.get(BASE_URL, params=params) as response:
        data = await response.json()

    weather = data.get("weather", [{}])[0]
    main = data.get("main", {})
    wind = data.get("wind", {})
    rain = data.get("rain", {})

    return {
        "temperature": main.get("temp", 0),
        "humidity": main.get("humidity", 0),
        "pressure": main.get("pressure", 0),
        "visibility": data.get("visibility", 10000),
        "wind_speed": wind.get("speed", 0),
        "rain_1h": rain.get("1h", 0),
        "weather_description": weather.get("description", "sin datos")
    }
