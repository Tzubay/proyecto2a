import pandas as pd
from datetime import datetime
from src.analyzer import estimate_delay_cause, count_delayed_flights
from src.airport_metadata import get_airport_metadata


def build_airport_row(airport, delays, schedules, weather, air_quality):
    airport_iata = airport.get("iata_code")
    metadata = get_airport_metadata(airport_iata)

    airport_name = airport.get("name") or airport_iata

    city = (
        airport.get("city")
        or airport.get("city_name")
        or metadata.get("city")
        or airport_name
        or "Desconocida"
    )

    region = (
        airport.get("state")
        or airport.get("region")
        or metadata.get("region")
        or city
    )

    total_flights = len(schedules)
    total_delays, average_delay = count_delayed_flights(delays, schedules)

    delay_percent = 0

    if total_flights > 0:
        delay_percent = (total_delays / total_flights) * 100

    row = {
        "timestamp": datetime.now(),
        "airport_iata": airport_iata,
        "airport_name": airport_name,
        "region": region,
        "city": city,
        "total_flights": total_flights,
        "total_delays": total_delays,
        "average_delay_minutes": average_delay,
        "delay_percent": delay_percent,
        "temperature": weather["temperature"],
        "humidity": weather["humidity"],
        "pressure": weather["pressure"],
        "visibility": weather["visibility"],
        "wind_speed": weather["wind_speed"],
        "rain_1h": weather["rain_1h"],
        "weather_description": weather["weather_description"],
        "pm25": air_quality["pm25"],
        "pm10": air_quality["pm10"]
    }

    row["probable_cause"] = estimate_delay_cause(row)

    return row


def clean_dataframe(df):
    numeric_columns = [
        "total_flights",
        "total_delays",
        "average_delay_minutes",
        "delay_percent",
        "temperature",
        "humidity",
        "pressure",
        "visibility",
        "wind_speed",
        "rain_1h",
        "pm25",
        "pm10"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df = df.fillna(0)

    return df


def summarize_by_region(df):
    return df.groupby("region").agg({
        "total_flights": "sum",
        "total_delays": "sum",
        "average_delay_minutes": "mean",
        "delay_percent": "mean"
    }).sort_values("total_delays", ascending=False)


def summarize_by_city(df):
    return df.groupby("city").agg({
        "total_flights": "sum",
        "total_delays": "sum",
        "average_delay_minutes": "mean",
        "delay_percent": "mean"
    }).sort_values("total_delays", ascending=False)


def summarize_causes(df):
    return df["probable_cause"].value_counts()
