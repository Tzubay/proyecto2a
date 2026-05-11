import numpy as np

try:
    import cupy as cp
    CUPY_AVAILABLE = True
except Exception:
    cp = None
    CUPY_AVAILABLE = False

try:
    from numba import cuda
    CUDA_AVAILABLE = cuda.is_available()
except Exception:
    cuda = None
    CUDA_AVAILABLE = False


def gpu_environment_available():
    return CUPY_AVAILABLE and CUDA_AVAILABLE


def calculate_environmental_risk_cupy(df):
    """
    Calcula un índice de riesgo ambiental usando CuPy en GPU.

    Variables usadas:
    - lluvia
    - visibilidad
    - viento
    - PM2.5
    - PM10

    Score:
    lluvia > 0          → +2
    visibilidad < 5000  → +3
    viento > 10         → +2
    PM2.5 > 35          → +1
    PM10 > 50           → +1
    """

    if not CUPY_AVAILABLE:
        raise RuntimeError("CuPy no está disponible.")

    rain = cp.asarray(df["rain_1h"].to_numpy(dtype=np.float32))
    visibility = cp.asarray(df["visibility"].to_numpy(dtype=np.float32))
    wind = cp.asarray(df["wind_speed"].to_numpy(dtype=np.float32))
    pm25 = cp.asarray(df["pm25"].to_numpy(dtype=np.float32))
    pm10 = cp.asarray(df["pm10"].to_numpy(dtype=np.float32))

    risk = cp.zeros(len(df), dtype=cp.float32)

    risk += cp.where(rain > 0, 2, 0)
    risk += cp.where(visibility < 5000, 3, 0)
    risk += cp.where(wind > 10, 2, 0)
    risk += cp.where(pm25 > 35, 1, 0)
    risk += cp.where(pm10 > 50, 1, 0)

    return cp.asnumpy(risk)


if CUDA_AVAILABLE:
    @cuda.jit
    def delay_classification_kernel(
        delay_percent,
        average_delay,
        environmental_risk,
        output
    ):
        idx = cuda.grid(1)

        if idx < delay_percent.size:
            score = 0

            if delay_percent[idx] >= 50:
                score += 3
            elif delay_percent[idx] >= 20:
                score += 2
            elif delay_percent[idx] > 0:
                score += 1

            if average_delay[idx] >= 60:
                score += 3
            elif average_delay[idx] >= 20:
                score += 2
            elif average_delay[idx] > 0:
                score += 1

            if environmental_risk[idx] >= 5:
                score += 3
            elif environmental_risk[idx] >= 3:
                score += 2
            elif environmental_risk[idx] > 0:
                score += 1

            output[idx] = score
else:
    delay_classification_kernel = None


def calculate_delay_severity_cuda(df):
    """
    Usa un kernel CUDA con Numba para calcular una severidad numérica.

    La severidad combina:
    - porcentaje de retrasos
    - retraso promedio
    - riesgo ambiental

    Devuelve un valor entero por aeropuerto:
    0-2   → bajo
    3-5   → medio
    6-9   → alto
    """

    if not CUDA_AVAILABLE:
        raise RuntimeError("CUDA no está disponible para Numba.")

    delay_percent = df["delay_percent"].to_numpy(dtype=np.float32)
    average_delay = df["average_delay_minutes"].to_numpy(dtype=np.float32)
    environmental_risk = df["environmental_risk_score"].to_numpy(dtype=np.float32)

    output = np.zeros(len(df), dtype=np.int32)

    d_delay_percent = cuda.to_device(delay_percent)
    d_average_delay = cuda.to_device(average_delay)
    d_environmental_risk = cuda.to_device(environmental_risk)
    d_output = cuda.to_device(output)

    threads_per_block = 128
    blocks_per_grid = (len(df) + threads_per_block - 1) // threads_per_block

    delay_classification_kernel[blocks_per_grid, threads_per_block](
        d_delay_percent,
        d_average_delay,
        d_environmental_risk,
        d_output
    )

    return d_output.copy_to_host()


def severity_label(score):
    if score >= 6:
        return "Alta"
    elif score >= 3:
        return "Media"
    else:
        return "Baja"


def apply_gpu_analysis(df):
    """
    Función principal para aplicar análisis GPU al DataFrame.

    Agrega:
    - environmental_risk_score
    - delay_severity_score
    - delay_severity_label
    - gpu_backend
    """

    if df.empty:
        df["environmental_risk_score"] = []
        df["delay_severity_score"] = []
        df["delay_severity_label"] = []
        df["gpu_backend"] = []
        return df

    try:
        df["environmental_risk_score"] = calculate_environmental_risk_cupy(df)
        df["delay_severity_score"] = calculate_delay_severity_cuda(df)
        df["delay_severity_label"] = df["delay_severity_score"].apply(severity_label)
        df["gpu_backend"] = "CuPy + Numba CUDA"

    except Exception as error:
        print("\nNo se pudo ejecutar GPU. Usando análisis en CPU.")
        print("Motivo:", error)

        df["environmental_risk_score"] = calculate_environmental_risk_cpu(df)
        df["delay_severity_score"] = calculate_delay_severity_cpu(df)
        df["delay_severity_label"] = df["delay_severity_score"].apply(severity_label)
        df["gpu_backend"] = "CPU fallback"

    return df


def calculate_environmental_risk_cpu(df):
    risk = np.zeros(len(df), dtype=np.float32)

    rain = df["rain_1h"].to_numpy(dtype=np.float32)
    visibility = df["visibility"].to_numpy(dtype=np.float32)
    wind = df["wind_speed"].to_numpy(dtype=np.float32)
    pm25 = df["pm25"].to_numpy(dtype=np.float32)
    pm10 = df["pm10"].to_numpy(dtype=np.float32)

    risk += np.where(rain > 0, 2, 0)
    risk += np.where(visibility < 5000, 3, 0)
    risk += np.where(wind > 10, 2, 0)
    risk += np.where(pm25 > 35, 1, 0)
    risk += np.where(pm10 > 50, 1, 0)

    return risk


def calculate_delay_severity_cpu(df):
    delay_percent = df["delay_percent"].to_numpy(dtype=np.float32)
    average_delay = df["average_delay_minutes"].to_numpy(dtype=np.float32)
    environmental_risk = df["environmental_risk_score"].to_numpy(dtype=np.float32)

    output = np.zeros(len(df), dtype=np.int32)

    for i in range(len(df)):
        score = 0

        if delay_percent[i] >= 50:
            score += 3
        elif delay_percent[i] >= 20:
            score += 2
        elif delay_percent[i] > 0:
            score += 1

        if average_delay[i] >= 60:
            score += 3
        elif average_delay[i] >= 20:
            score += 2
        elif average_delay[i] > 0:
            score += 1

        if environmental_risk[i] >= 5:
            score += 3
        elif environmental_risk[i] >= 3:
            score += 2
        elif environmental_risk[i] > 0:
            score += 1

        output[i] = score

    return output