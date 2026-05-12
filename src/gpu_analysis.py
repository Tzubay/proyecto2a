# -*- coding: utf-8 -*-
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


def get_gpu_name():
    # detecta el nombre real de la GPU en lugar de hardcodearlo
    try:
        name = cp.cuda.runtime.getDeviceProperties(0)['name']
        return name.decode() if isinstance(name, bytes) else name
    except Exception:
        return "GPU NVIDIA"


def gpu_environment_available():
    return CUPY_AVAILABLE and CUDA_AVAILABLE


def calculate_environmental_risk_cupy(df):
    if not CUPY_AVAILABLE:
        raise RuntimeError("CuPy no esta disponible.")

    rain       = cp.asarray(df["rain_1h"].to_numpy(dtype=np.float32))
    visibility = cp.asarray(df["visibility"].to_numpy(dtype=np.float32))
    wind       = cp.asarray(df["wind_speed"].to_numpy(dtype=np.float32))
    pm25       = cp.asarray(df["pm25"].to_numpy(dtype=np.float32))
    pm10       = cp.asarray(df["pm10"].to_numpy(dtype=np.float32))

    risk = cp.zeros(len(df), dtype=cp.float32)
    risk += cp.where(rain > 0,          2.0, 0.0)
    risk += cp.where(visibility < 5000, 3.0, 0.0)
    risk += cp.where(wind > 10,         2.0, 0.0)
    risk += cp.where(pm25 > 35,         1.0, 0.0)
    risk += cp.where(pm10 > 50,         1.0, 0.0)

    return cp.asnumpy(risk)


def calculate_delay_severity_cupy(df):
    if not CUPY_AVAILABLE:
        raise RuntimeError("CuPy no esta disponible.")

    delay_percent      = cp.asarray(df["delay_percent"].to_numpy(dtype=np.float32))
    average_delay      = cp.asarray(df["average_delay_minutes"].to_numpy(dtype=np.float32))
    environmental_risk = cp.asarray(df["environmental_risk_score"].to_numpy(dtype=np.float32))

    score = cp.zeros(len(df), dtype=cp.float32)

    score += cp.where(delay_percent >= 50, 3.0,
             cp.where(delay_percent >= 20, 2.0,
             cp.where(delay_percent >  0,  1.0, 0.0)))

    score += cp.where(average_delay >= 60, 3.0,
             cp.where(average_delay >= 20, 2.0,
             cp.where(average_delay >  0,  1.0, 0.0)))

    score += cp.where(environmental_risk >= 5, 3.0,
             cp.where(environmental_risk >= 3, 2.0,
             cp.where(environmental_risk >  0, 1.0, 0.0)))

    return cp.asnumpy(score)


def severity_label(score):
    if score >= 6:
        return "Alta"
    elif score >= 3:
        return "Media"
    else:
        return "Baja"


def apply_gpu_analysis(df):
    if df.empty:
        df["environmental_risk_score"] = []
        df["delay_severity_score"]     = []
        df["delay_severity_label"]     = []
        df["gpu_backend"]              = []
        return df

    try:
        gpu_name = get_gpu_name()

        df["environmental_risk_score"] = calculate_environmental_risk_cupy(df)
        df["delay_severity_score"]     = calculate_delay_severity_cupy(df)
        df["delay_severity_label"]     = df["delay_severity_score"].apply(severity_label)
        df["gpu_backend"]              = f"CuPy + Numba CUDA ({gpu_name})"
        print(f"\n[GPU] Analisis ejecutado con {gpu_name} - CuPy + Numba CUDA OK")

    except Exception as error:
        print("\nNo se pudo ejecutar GPU. Usando analisis en CPU.")
        print("Motivo:", error)

        df["environmental_risk_score"] = calculate_environmental_risk_cpu(df)
        df["delay_severity_score"]     = calculate_delay_severity_cpu(df)
        df["delay_severity_label"]     = df["delay_severity_score"].apply(severity_label)
        df["gpu_backend"]              = "CPU fallback"

    return df


def calculate_environmental_risk_cpu(df):
    risk       = np.zeros(len(df), dtype=np.float32)
    rain       = df["rain_1h"].to_numpy(dtype=np.float32)
    visibility = df["visibility"].to_numpy(dtype=np.float32)
    wind       = df["wind_speed"].to_numpy(dtype=np.float32)
    pm25       = df["pm25"].to_numpy(dtype=np.float32)
    pm10       = df["pm10"].to_numpy(dtype=np.float32)

    risk += np.where(rain > 0,          2.0, 0.0)
    risk += np.where(visibility < 5000, 3.0, 0.0)
    risk += np.where(wind > 10,         2.0, 0.0)
    risk += np.where(pm25 > 35,         1.0, 0.0)
    risk += np.where(pm10 > 50,         1.0, 0.0)

    return risk


def calculate_delay_severity_cpu(df):
    delay_percent      = df["delay_percent"].to_numpy(dtype=np.float32)
    average_delay      = df["average_delay_minutes"].to_numpy(dtype=np.float32)
    environmental_risk = df["environmental_risk_score"].to_numpy(dtype=np.float32)
    output             = np.zeros(len(df), dtype=np.float32)

    for i in range(len(df)):
        score = 0.0

        if delay_percent[i] >= 50:    score += 3.0
        elif delay_percent[i] >= 20:  score += 2.0
        elif delay_percent[i] > 0:    score += 1.0

        if average_delay[i] >= 60:    score += 3.0
        elif average_delay[i] >= 20:  score += 2.0
        elif average_delay[i] > 0:    score += 1.0

        if environmental_risk[i] >= 5:  score += 3.0
        elif environmental_risk[i] >= 3: score += 2.0
        elif environmental_risk[i] > 0:  score += 1.0

        output[i] = score

    return output