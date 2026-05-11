import pandas as pd
from src.analyzer import (
    get_flight_delay_minutes,
    estimate_flight_cause,
    get_flight_event_type
)
def calculate_environmental_risk_for_flight(weather, air_quality):
    score = 0

    rain_1h = weather.get("rain_1h", 0) or 0
    visibility = weather.get("visibility", 10000) or 10000
    wind_speed = weather.get("wind_speed", 0) or 0
    pm25 = air_quality.get("pm25", 0) or 0
    pm10 = air_quality.get("pm10", 0) or 0

    if rain_1h > 0:
        score += 2

    if visibility < 5000:
        score += 3

    if wind_speed > 10:
        score += 2

    if pm25 > 35:
        score += 1

    if pm10 > 50:
        score += 1

    return score

def build_flight_rows(airport, schedules, weather, air_quality, city, region):
    rows = []

    airport_iata = airport.get("iata_code")
    airport_name = airport.get("name") or airport_iata

    for flight in schedules:
        event_type = get_flight_event_type(flight)
        delay_minutes = get_flight_delay_minutes(flight)

        # Solo guardamos vuelos retrasados o cancelados
        if event_type == "Normal":
            continue

        row = {
            "airport_iata": airport_iata,
            "airport_name": airport_name,
            "city": city,
            "region": region,

            "flight_iata": flight.get("flight_iata"),
            "airline_iata": flight.get("airline_iata"),
            "dep_iata": flight.get("dep_iata"),
            "arr_iata": flight.get("arr_iata"),

            "dep_time": flight.get("dep_time"),
            "dep_estimated": flight.get("dep_estimated"),
            "dep_actual": flight.get("dep_actual"),

            "arr_time": flight.get("arr_time"),
            "arr_estimated": flight.get("arr_estimated"),
            "arr_actual": flight.get("arr_actual"),

            "status": flight.get("status"),
            "event_type": event_type,
            "delay_minutes": delay_minutes,

            "temperature": weather.get("temperature"),
            "humidity": weather.get("humidity"),
            "pressure": weather.get("pressure"),
            "visibility": weather.get("visibility"),
            "wind_speed": weather.get("wind_speed"),
            "rain_1h": weather.get("rain_1h"),
            "weather_description": weather.get("weather_description"),

            "pm25": air_quality.get("pm25"),
            "pm10": air_quality.get("pm10"),

            "environmental_risk_score": calculate_environmental_risk_for_flight(weather, air_quality),
            
            "probable_cause": estimate_flight_cause(
                flight=flight,
                weather=weather,
                air_quality=air_quality
            )
            
        }

        rows.append(row)

    return rows


def summarize_flight_events(df_flights):
    if df_flights.empty:
        return pd.DataFrame()

    return df_flights.groupby(
        ["region", "city", "event_type", "probable_cause"]
    ).size().reset_index(name="total")