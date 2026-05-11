import matplotlib.pyplot as plt


def plot_delays_by_region(df):
    data = df.groupby("region")["total_delays"].sum().sort_values(ascending=False)

    plt.figure(figsize=(10, 5))
    data.plot(kind="bar")
    plt.title("Retrasos por región")
    plt.xlabel("Región")
    plt.ylabel("Total de retrasos")
    plt.tight_layout()
    plt.savefig("data/processed/retrasos_por_region.png")
    plt.show()


def plot_delays_by_city(df):
    data = df.groupby("city")["total_delays"].sum().sort_values(ascending=False).head(10)

    plt.figure(figsize=(10, 5))
    data.plot(kind="bar")
    plt.title("Top 10 ciudades con más retrasos")
    plt.xlabel("Ciudad")
    plt.ylabel("Total de retrasos")
    plt.tight_layout()
    plt.savefig("data/processed/retrasos_por_ciudad.png")
    plt.show()


def plot_causes(df):
    data = df["probable_cause"].value_counts()

    plt.figure(figsize=(10, 5))
    data.plot(kind="bar")
    plt.title("Causas probables de retrasos")
    plt.xlabel("Causa probable")
    plt.ylabel("Cantidad de aeropuertos afectados")
    plt.tight_layout()
    plt.savefig("data/processed/causas_probables.png")
    plt.show()

def plot_environmental_risk_by_region(df):
    if "environmental_risk_score" not in df.columns:
        return

    data = df.groupby("region")["environmental_risk_score"].mean().sort_values(ascending=False)

    plt.figure(figsize=(10, 5))
    data.plot(kind="bar")
    plt.title("Riesgo ambiental promedio por región")
    plt.xlabel("Región")
    plt.ylabel("Índice de riesgo ambiental")
    plt.tight_layout()
    plt.savefig("data/processed/riesgo_ambiental_por_region.png")
    plt.show()


def plot_delay_severity_by_region(df):
    if "delay_severity_score" not in df.columns:
        return

    data = df.groupby("region")["delay_severity_score"].mean().sort_values(ascending=False)

    plt.figure(figsize=(10, 5))
    data.plot(kind="bar")
    plt.title("Severidad de retrasos por región")
    plt.xlabel("Región")
    plt.ylabel("Índice de severidad")
    plt.tight_layout()
    plt.savefig("data/processed/severidad_retrasos_por_region.png")
    plt.show()