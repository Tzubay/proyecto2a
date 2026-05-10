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
