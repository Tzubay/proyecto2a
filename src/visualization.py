# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt

plt.rcParams["figure.facecolor"] = "#f9f9f9"
plt.rcParams["axes.facecolor"]   = "#ffffff"
plt.rcParams["axes.edgecolor"]   = "#cccccc"
plt.rcParams["axes.grid"]        = True
plt.rcParams["grid.alpha"]       = 0.4
plt.rcParams["font.size"]        = 11


def _save_and_show(path: str) -> None:
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.show(block=False)
    plt.pause(0.1)


def plot_delays_by_region(df):
    data = df.groupby("region")["total_delays"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(data.index, data.values, color="#4C72B0", edgecolor="white", linewidth=0.8)
    ax.bar_label(bars, padding=3, fontsize=10)
    ax.set_title("Retrasos por región", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Región", fontsize=12)
    ax.set_ylabel("Total de retrasos", fontsize=12)
    ax.set_xticks(range(len(data)))
    ax.set_xticklabels(data.index, rotation=25, ha="right", fontsize=10)
    _save_and_show("data/processed/retrasos_por_region.png")


def plot_delays_by_city(df):
    data = df.groupby("city")["total_delays"].sum().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(data.index, data.values, color="#DD8452", edgecolor="white", linewidth=0.8)
    ax.bar_label(bars, padding=3, fontsize=10)
    ax.set_title("Top 10 ciudades con más retrasos", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Ciudad", fontsize=12)
    ax.set_ylabel("Total de retrasos", fontsize=12)
    ax.set_xticks(range(len(data)))
    ax.set_xticklabels(data.index, rotation=25, ha="right", fontsize=10)
    _save_and_show("data/processed/retrasos_por_ciudad.png")


def plot_causes(df):
    data = df["probable_cause"].value_counts()
    short_labels = [
        label.replace("probablemente ", "").replace(" o no ambiental", "")
        for label in data.index
    ]
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(short_labels, data.values, color="#55A868", edgecolor="white", linewidth=0.8)
    ax.bar_label(bars, padding=3, fontsize=10)
    ax.set_title("Causas probables de retrasos", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Causa probable", fontsize=12)
    ax.set_ylabel("Cantidad de aeropuertos afectados", fontsize=12)
    ax.set_xticks(range(len(short_labels)))
    ax.set_xticklabels(short_labels, rotation=20, ha="right", fontsize=10)
    _save_and_show("data/processed/causas_probables.png")


def plot_environmental_risk_by_region(df):
    if "environmental_risk_score" not in df.columns:
        return
    data = df.groupby("region")["environmental_risk_score"].mean().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(data.index, data.values, color="#C44E52", edgecolor="white", linewidth=0.8)
    ax.bar_label(bars, fmt="%.1f", padding=3, fontsize=10)
    ax.set_title("Riesgo ambiental promedio por región", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Región", fontsize=12)
    ax.set_ylabel("Índice de riesgo ambiental", fontsize=12)
    ax.set_xticks(range(len(data)))
    ax.set_xticklabels(data.index, rotation=25, ha="right", fontsize=10)
    _save_and_show("data/processed/riesgo_ambiental_por_region.png")


def plot_delay_severity_by_region(df):
    if "delay_severity_score" not in df.columns:
        return
    data = df.groupby("region")["delay_severity_score"].mean().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(data.index, data.values, color="#8172B2", edgecolor="white", linewidth=0.8)
    ax.bar_label(bars, fmt="%.1f", padding=3, fontsize=10)
    ax.set_title("Severidad de retrasos por región", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Región", fontsize=12)
    ax.set_ylabel("Índice de severidad", fontsize=12)
    ax.set_xticks(range(len(data)))
    ax.set_xticklabels(data.index, rotation=25, ha="right", fontsize=10)
    _save_and_show("data/processed/severidad_retrasos_por_region.png")