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


def calculate_average_delay(delays):
    delay_values = []

    for delay in delays:
        dep_delay = delay.get("dep_delay")

        if dep_delay is not None:
            try:
                delay_values.append(float(dep_delay))
            except ValueError:
                pass

    if not delay_values:
        return 0

    return sum(delay_values) / len(delay_values)
