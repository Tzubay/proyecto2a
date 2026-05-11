# -*- coding: utf-8 -*-
"""
src/mpi_processor.py
====================
Distribución del procesamiento de aeropuertos usando MPI4Py.

Ejecución:
    mpiexec -n 4 python main.py
"""

import asyncio
import aiohttp
import threading

from mpi4py import MPI


def scatter_airports(airports: list, comm) -> list:
    rank = comm.Get_rank()
    size = comm.Get_size()

    if rank == 0:
        chunks = [[] for _ in range(size)]
        for i, airport in enumerate(airports):
            chunks[i % size].append(airport)
        print(f"\n[MPI] Distribuyendo {len(airports)} aeropuertos entre {size} procesos.")
        for i, chunk in enumerate(chunks):
            print(f"  Proceso {i}: {len(chunk)} aeropuertos")
    else:
        chunks = None

    return comm.scatter(chunks, root=0)


def gather_results(local_rows: list, local_flight_rows: list, comm) -> tuple:
    all_rows        = comm.gather(local_rows, root=0)
    all_flight_rows = comm.gather(local_flight_rows, root=0)

    if comm.Get_rank() == 0:
        rows        = [r for sublist in all_rows        for r in sublist if r is not None]
        flight_rows = [r for sublist in all_flight_rows for r in sublist]
        return rows, flight_rows
    return [], []


async def analyze_airports_local(airports: list, rank: int) -> tuple:
    from src.airlabs_api      import get_delays_by_airport, get_schedules_by_airport
    from src.openweather_api  import get_weather_by_coordinates
    from src.openaq_api       import get_air_quality_nearby
    from src.processor        import build_airport_row
    from src.airport_metadata import get_airport_metadata
    from src.flight_report    import build_flight_rows

    rows        = []
    flight_rows = []

    async with aiohttp.ClientSession() as session:
        for airport in airports:
            airport_iata = airport.get("iata_code")
            lat          = airport.get("lat")
            lon          = airport.get("lng")

            if not airport_iata or not lat or not lon:
                continue

            print(f"  [Proceso {rank}] Analizando {airport_iata}...")

            try:
                delays, schedules, weather, air_quality = await asyncio.gather(
                    get_delays_by_airport(session, airport_iata),
                    get_schedules_by_airport(session, airport_iata),
                    get_weather_by_coordinates(session, lat, lon),
                    get_air_quality_nearby(session, lat, lon),
                )

                airport_row = build_airport_row(
                    airport=airport,
                    delays=delays,
                    schedules=schedules,
                    weather=weather,
                    air_quality=air_quality,
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

                flight_rows_local = build_flight_rows(
                    airport=airport,
                    schedules=schedules,
                    weather=weather,
                    air_quality=air_quality,
                    city=city,
                    region=region,
                )

                if airport_row:
                    rows.append(airport_row)
                flight_rows.extend(flight_rows_local)

            except Exception as e:
                print(f"  [Proceso {rank}] Error en {airport_iata}: {e}")

    return rows, flight_rows


def _run_in_thread(airports: list, rank: int) -> tuple:
    """
    Corre el análisis asyncio en un hilo separado para evitar
    conflicto con el event loop del proceso principal.
    """
    result = {}

    def thread_target():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result["rows"], result["flight_rows"] = loop.run_until_complete(
                analyze_airports_local(airports, rank)
            )
        finally:
            loop.close()

    t = threading.Thread(target=thread_target)
    t.start()
    t.join()

    return result.get("rows", []), result.get("flight_rows", [])


def run_mpi_analysis(airports: list) -> tuple:
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    local_airports = scatter_airports(airports, comm)

    # Correr asyncio en hilo separado para no conflictuar con el loop principal
    local_rows, local_flight_rows = _run_in_thread(local_airports, rank)

    comm.Barrier()

    rows, flight_rows = gather_results(local_rows, local_flight_rows, comm)

    if rank == 0:
        print(f"\n[MPI] Procesamiento distribuido completado.")
        print(f"[MPI] Total aeropuertos procesados: {len(rows)}")

    return rows, flight_rows