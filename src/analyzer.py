def get_flight_delay_minutes(flight):
    possible_fields = [
        "dep_delayed",
        "arr_delayed",
        "delayed",
        "dep_delay",
        "arr_delay",
        "delay"
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


def estimate_delay_cause(row):
    if row["total_delays"] <= 0:
        return "Sin retrasos detectados"

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


def count_delayed_flights(delays, schedules):
    delay_values = []

    # Primero usamos el endpoint de delays si trae algo
    for delay in delays:
        minutes = get_flight_delay_minutes(delay)

        if minutes > 0:
            delay_values.append(minutes)

    # Después revisamos schedules, porque ahí también puede venir información útil
    for flight in schedules:
        minutes = get_flight_delay_minutes(flight)

        if minutes > 0:
            delay_values.append(minutes)

    total_delayed = len(delay_values)

    if total_delayed == 0:
        return 0, 0

    average_delay = sum(delay_values) / total_delayed

    return total_delayed, average_delay


def estimate_flight_cause(flight, weather, air_quality):
    status = str(flight.get("status", "")).lower()
    delay_minutes = get_flight_delay_minutes(flight)

    is_cancelled = status in ["cancelled", "canceled"]
    is_delayed = delay_minutes > 0 or "delay" in status

    if not is_cancelled and not is_delayed:
        return "Vuelo sin retraso o cancelación detectada"

    causes = []

    rain_1h = weather.get("rain_1h", 0) or 0
    visibility = weather.get("visibility", 10000) or 10000
    wind_speed = weather.get("wind_speed", 0) or 0
    pm25 = air_quality.get("pm25", 0) or 0
    pm10 = air_quality.get("pm10", 0) or 0

    if rain_1h > 0:
        causes.append("lluvia")

    if visibility < 5000:
        causes.append("baja visibilidad")

    if wind_speed > 10:
        causes.append("viento fuerte")

    if pm25 > 35:
        causes.append("alta concentración de PM2.5")

    if pm10 > 50:
        causes.append("alta concentración de PM10")

    if causes:
        if is_cancelled:
            return "Cancelación probablemente asociada a " + ", ".join(causes)

        return "Retraso probablemente asociado a " + ", ".join(causes)

    if is_cancelled:
        return "Cancelación probablemente operativa o no ambiental"

    return "Retraso probablemente operativo o no ambiental"


def get_flight_event_type(flight):
    status = str(flight.get("status", "")).lower()
    delay_minutes = get_flight_delay_minutes(flight)

    if status in ["cancelled", "canceled"]:
        return "Cancelado"
    
  #  if "cancel" in status:
  #      return "Cancelado"

    if delay_minutes > 0 or "delay" in status:
        return "Retrasado"

    return "Normal"