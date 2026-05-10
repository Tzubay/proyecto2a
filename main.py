import asyncio
import aiohttp
import pandas as pd
import os

from src.countries import get_country_code
from src.airlabs_api import (
    get_airports_by_country,
    get_delays_by_airport,
    get_schedules_by_airport
)
from src.openweather_api import get_weather_by_coordinates
from src.openaq_api import get_air_quality_nearby
from src.processor import (
    build_airport_row,
    clean_dataframe,
    summarize_by_region,
    summarize_by_city,
    summarize_causes
)
from src.visualization import (
    plot_delays_by_region,
    plot_delays_by_city,
    plot_causes
)


async def analyze_airport(session, airport):
    airport_iata = airport.get("iata_code")
    lat = airport.get("lat")
    lon = airport.get("lng")

    if not airport_iata or not lat or not lon:
        return None

    print(f"Analizando aeropuerto {airport_iata}...")

    delays_task = get_delays_by_airport(session, airport_iata)
    schedules_task = get_schedules_by_airport(session, airport_iata)
    weather_task = get_weather_by_coordinates(session, lat, lon)
    air_quality_task = get_air_quality_nearby(session, lat, lon)

    delays, schedules, weather, air_quality = await asyncio.gather(
        delays_task,
        schedules_task,
        weather_task,
        air_quality_task
    )

    row = build_airport_row(
        airport=airport,
        delays=delays,
        schedules=schedules,
        weather=weather,
        air_quality=air_quality
    )

    return row


async def main():
    os.makedirs("data/processed", exist_ok=True)

    country_name = input("Escribe el nombre completo del país en español: ")
    country_code = get_country_code(country_name)

    if country_code is None:
        print("País no registrado en el diccionario del proyecto.")
        print("Agrega el país en src/countries.py")
        return

    print(f"País seleccionado: {country_name}")
    print(f"Código ISO detectado: {country_code}")

    async with aiohttp.ClientSession() as session:
        airports = await get_airports_by_country(session, country_code)

        if not airports:
            print("No se encontraron aeropuertos para ese país.")
            return

        airports = airports[:20]

        tasks = []

        for airport in airports:
            tasks.append(analyze_airport(session, airport))

        rows = await asyncio.gather(*tasks)

    rows = [row for row in rows if row is not None]

    if not rows:
        print("No se pudieron procesar aeropuertos válidos.")
        return

    df = pd.DataFrame(rows)
    df = clean_dataframe(df)

    output_path = "data/processed/analisis_retrasos_ambientales.csv"
    df.to_csv(output_path, index=False)

    print("\nDatos unificados:")
    print(df)

    print("\nResumen por región:")
    region_summary = summarize_by_region(df)
    print(region_summary)

    print("\nResumen por ciudad:")
    city_summary = summarize_by_city(df)
    print(city_summary)

    print("\nCausas probables:")
    causes_summary = summarize_causes(df)
    print(causes_summary)

    plot_delays_by_region(df)
    plot_delays_by_city(df)
    plot_causes(df)

    print(f"\nArchivo generado: {output_path}")


if __name__ == "__main__":
    asyncio.run(main())
