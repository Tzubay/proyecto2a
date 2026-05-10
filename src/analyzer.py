def estimate_delay_cause(row):
    causes = []

    if row["rain_1h"] > 0:
        causes.append("lluvia")

    if row["visibility"] < 5000:
        causes.append("baja visibilidad")

    if row["wind_speed"] > 10:
        causes.append("viento fuerte")

    if row["pm25"] > 35:
        causes.append("alta concentración de PM2.5")

    if row["pm10"] > 50:
        causes.append("alta concentración de PM10")

    if not causes:
        return "Retraso probablemente operativo o no ambiental"

    return "Retraso probablemente asociado a " + ", ".join(causes)


def extract_delay_minutes_from_flight(flight):
    possible_fields = [
        "dep_delay",
        "arr_delay",
        "delay",
        "delayed"
    ]

    for field in possible_fields:
        value = flight.get(field)

        if value is not None:
            try:
                return float(value)
            except (ValueError, TypeError):
                pass

    status = str(flight.get("status", "")).lower()

    if "delay" in status or "delayed" in status:
        return 1

    return 0


def count_delayed_flights(delays, schedules):
    delay_values = []

    # Primero usamos el endpoint de delays si trae algo
    for delay in delays:
        minutes = extract_delay_minutes_from_flight(delay)

        if minutes > 0:
            delay_values.append(minutes)

    # Después revisamos schedules, porque ahí también puede venir info útil
    for flight in schedules:
        minutes = extract_delay_minutes_from_flight(flight)

        if minutes > 0:
            delay_values.append(minutes)

    total_delayed = len(delay_values)

    if total_delayed == 0:
        return 0, 0

    average_delay = sum(delay_values) / total_delayed

    return total_delayed, average_delay