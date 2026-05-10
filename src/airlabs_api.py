import aiohttp
from config import AIRLABS_API_KEY

BASE_URL = "https://airlabs.co/api/v9"


async def fetch_json(session, endpoint, params):
    url = f"{BASE_URL}/{endpoint}"

    params["api_key"] = AIRLABS_API_KEY

    async with session.get(url, params=params) as response:
        return await response.json()


async def get_airports_by_country(session, country_code):
    data = await fetch_json(
        session,
        "airports",
        {
            "country_code": country_code
        }
    )

    return data.get("response", [])


async def get_delays_by_airport(session, airport_iata):
    data = await fetch_json(
        session,
        "delays",
        {
            "dep_iata": airport_iata
        }
    )

    return data.get("response", [])


async def get_schedules_by_airport(session, airport_iata):
    data = await fetch_json(
        session,
        "schedules",
        {
            "dep_iata": airport_iata
        }
    )

    return data.get("response", [])
