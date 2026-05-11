# -*- coding: utf-8 -*-
"""
Ejecución con MPI:
    mpiexec -n 4 python main.py
"""

import sys
import io
import asyncio
import aiohttp
import pandas as pd
import os

# Forzar UTF-8 en la consola de Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from src.flight_report    import build_flight_rows, summarize_flight_events
from src.airport_metadata import get_airport_metadata
from src.countries        import get_country_code
from src.airlabs_api      import (
    get_airports_by_country,
    get_delays_by_airport,
    get_schedules_by_airport,
)
from src.openweather_api import get_weather_by_coordinates
from src.openaq_api      import get_air_quality_nearby
from src.processor       import (
    build_airport_row,
    clean_dataframe,
    summarize_by_region,
    summarize_by_city,
    summarize_causes,
)
from src.visualization import (
    plot_delays_by_region,
    plot_delays_by_city,
    plot_causes,
    plot_environmental_risk_by_region,
    plot_delay_severity_by_region,
)
from src.gpu_analysis import apply_gpu_analysis

# Detección MPI
try:
    from mpi4py import MPI
    _MPI_COMM    = MPI.COMM_WORLD
    _MPI_RANK    = _MPI_COMM.Get_rank()
    _MPI_SIZE    = _MPI_COMM.Get_size()
    _MPI_AVAILABLE = True
except ImportError:
    _MPI_AVAILABLE = False
    _MPI_RANK = 0
    _MPI_SIZE = 1


# Análisis estándar por aeropuerto (asyncio)
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
        get_air_quality_nearby(session, lat, lon),
    )

    airport_row = build_airport_row(
        airport=airport, delays=delays,
        schedules=schedules, weather=weather, air_quality=air_quality,
    )

    metadata = get_airport_metadata(airport_iata)
    city = (
        airport.get("city") or airport.get("city_name")
        or metadata.get("city") or airport.get("name") or "Desconocida"
    )
    region = (
        airport.get("state") or airport.get("region")
        or metadata.get("region") or city
    )

    flight_rows = build_flight_rows(
        airport=airport, schedules=schedules,
        weather=weather, air_quality=air_quality,
        city=city, region=region,
    )

    return airport_row, flight_rows


# Main
async def main():
    os.makedirs("data/processed", exist_ok=True)

    # Proceso 0: pide input y obtiene aeropuertos
    # Los demás procesos esperan en silencio
    if _MPI_RANK == 0:
        country_name = input("Escribe el nombre completo del pais en espanol: ")
        country_code = get_country_code(country_name)

        if country_code is None:
            print("Pais no registrado. Agregalo en src/countries.py")
            if _MPI_AVAILABLE:
                _MPI_COMM.bcast(None, root=0)
            return

        print(f"Pais seleccionado : {country_name}")
        print(f"Codigo ISO        : {country_code}")

        async with aiohttp.ClientSession() as session:
            airports = await get_airports_by_country(session, country_code)

        if not airports:
            print("No se encontraron aeropuertos.")
            if _MPI_AVAILABLE:
                _MPI_COMM.bcast(None, root=0)
            return

        airports = airports[:20]
    else:
        airports    = None
        country_code = None

    # Compartir datos con todos los procesos
    if _MPI_AVAILABLE:
        airports = _MPI_COMM.bcast(airports, root=0)
        if airports is None:
            return

    # Modo MPI distribuido
    if _MPI_AVAILABLE and _MPI_SIZE > 1:
        if _MPI_RANK == 0:
            print(f"\n[MPI] Modo distribuido activado con {_MPI_SIZE} procesos.")

        from src.mpi_processor import run_mpi_analysis
        rows, flight_rows = run_mpi_analysis(airports)

        if _MPI_RANK != 0:
            return

    # GPU + análisis
    df = pd.DataFrame(rows)
    df = clean_dataframe(df)
    df = df[df["total_flights"] > 0]
    df = apply_gpu_analysis(df)

    output_path = "data/processed/analisis_retrasos_ambientales.csv"
    df.to_csv(output_path, index=False)

    df_flights         = pd.DataFrame(flight_rows)
    flight_output_path = "data/processed/vuelos_retrasados_cancelados.csv"

    if not df_flights.empty:
        df_flights.to_csv(flight_output_path, index=False)
        print("\nVuelos retrasados o cancelados:")
        pd.set_option("display.max_columns", None)
        pd.set_option("display.width", 200)
        print(df_flights[[
            "flight_iata", "airline_iata", "dep_iata", "arr_iata",
            "event_type", "delay_minutes", "status", "dep_time",
            "visibility", "wind_speed", "rain_1h", "weather_description",
            "city", "region", "probable_cause",
        ]])
        print("\nResumen de vuelos afectados por causa probable:")
        print(summarize_flight_events(df_flights))
        print(f"\nArchivo de vuelos generado: {flight_output_path}")
    else:
        print("\nNo se encontraron vuelos retrasados o cancelados.")

    print("\nDatos unificados:")
    print(df)

    print("\nResumen por region:")
    print(summarize_by_region(df))

    print("\nResumen por ciudad:")
    print(summarize_by_city(df))

    print("\nCausas probables:")
    print(summarize_causes(df))

    print(f"\nArchivo generado: {output_path}")

    plot_delays_by_region(df)
    plot_delays_by_city(df)
    plot_causes(df)
    plot_environmental_risk_by_region(df)
    plot_delay_severity_by_region(df)

    input("\nPresiona Enter para cerrar las graficas...")


if __name__ == "__main__":
    asyncio.run(main())