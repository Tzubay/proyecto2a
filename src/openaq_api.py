BASE_URL = "https://api.openaq.org/v3/locations"


async def get_air_quality_nearby(session, lat, lon):
    params = {
        "coordinates": f"{lat},{lon}",
        "radius": 25000,
        "limit": 5
    }

    try:
        async with session.get(BASE_URL, params=params) as response:
            data = await response.json()
    except Exception:
        return {
            "pm25": 0,
            "pm10": 0
        }

    results = data.get("results", [])

    pm25 = 0
    pm10 = 0

    for location in results:
        parameters = location.get("parameters", [])

        for parameter in parameters:
            name = parameter.get("parameter", {}).get("name", "")

            if name == "pm25":
                pm25 = parameter.get("latest", {}).get("value", 0) or 0

            if name == "pm10":
                pm10 = parameter.get("latest", {}).get("value", 0) or 0

    return {
        "pm25": pm25,
        "pm10": pm10
    }
