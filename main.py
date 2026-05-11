# -*- coding: utf-8 -*-
import asyncio
import aiohttp
import pandas as pd
import os
from src.flight_report import build_flight_rows, summarize_flight_events
from src.airport_metadata import get_airport_metadata
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
        return None, []

    print(f"Analizando aeropuerto {airport_iata}...")

    delays, schedules, weather, air_quality = await asyncio.gather(
        get_delays_by_airport(session, airport_iata),
        get_schedules_by_airport(session, airport_iata),
        get_weather_by_coordinates(session, lat, lon),
        get_air_quality_nearby(session, lat, lon)
    )

    airport_row = build_airport_row(
        airport=airport,
        delays=delays,
        schedules=schedules,
        weather=weather,
        air_quality=air_quality
    )

    metadata = get_airport_metadata(airport_iata)

    city = (
        airport.get("city")
        or airport.get("city_name")
        or metadata.get("city")
        or airport.get("name")
        or "Desconocida"
    )

    region = (
        airport.get("state")
        or airport.get("region")
        or metadata.get("region")
        or city
    )

    flight_rows = build_flight_rows(
        airport=airport,
        schedules=schedules,
        weather=weather,
        air_quality=air_quality,
        city=city,
        region=region
    )

    return airport_row, flight_rows


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

        results = await asyncio.gather(
            *[analyze_airport(session, airport) for airport in airports]
        )

    rows = []
    flight_rows = []

    for airport_row, airport_flight_rows in results:
        if airport_row is not None:
            rows.append(airport_row)
        flight_rows.extend(airport_flight_rows)

    if not rows:
        print("No se pudieron procesar aeropuertos válidos.")
        return

    df = pd.DataFrame(rows)
    df = clean_dataframe(df)
    df = df[df["total_flights"] > 0]

    output_path = "data/processed/analisis_retrasos_ambientales.csv"
    df.to_csv(output_path, index=False)

    df_flights = pd.DataFrame(flight_rows)
    flight_output_path = "data/processed/vuelos_retrasados_cancelados.csv"

    if not df_flights.empty:
        df_flights.to_csv(flight_output_path, index=False)

        print("\nVuelos retrasados o cancelados:")
        pd.set_option("display.max_columns", None)
        pd.set_option("display.width", 200)

        print(df_flights[[
            "flight_iata", "airline_iata", "dep_iata", "arr_iata",
            "event_type", "delay_minutes", "status", "dep_time",
            "dep_estimated", "dep_actual", "visibility", "wind_speed",
            "rain_1h", "weather_description", "city", "region", "probable_cause"
        ]])

        print("\nResumen de vuelos afectados por causa probable:")
        print(summarize_flight_events(df_flights))
        print(f"\nArchivo de vuelos generado: {flight_output_path}")
    else:
        print("\nNo se encontraron vuelos retrasados o cancelados en esta consulta.")

    print("\nDatos unificados:")
    print(df)

    print("\nResumen por región:")
    print(summarize_by_region(df))

    print("\nResumen por ciudad:")
    print(summarize_by_city(df))

    print("\nCausas probables:")
    print(summarize_causes(df))

    print(f"\nArchivo generado: {output_path}")

    plot_delays_by_region(df)
    plot_delays_by_city(df)
    plot_causes(df)

    input("\nPresiona Enter para cerrar las gráficas...")


if __name__ == "__main__":
    asyncio.run(main())