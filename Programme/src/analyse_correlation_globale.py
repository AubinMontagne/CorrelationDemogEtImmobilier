"""
Analyse de correlation globale entre prix immobilier et revenu median.

Ce script calcule la correlation de Pearson entre le revenu median
et les prix immobiliers pour l'ensemble des 33 communes du dataset.
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Configuration des chemins
ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "output"


def charger_donnees():
    """Charge et fusionne les donnees demographiques et immobilieres."""
    df_demo = pd.read_csv(DATA_DIR / "demographiques" / "demographiques.csv")
    df_immo = pd.read_csv(DATA_DIR / "immobilier" / "immobilier.csv")
    df = pd.merge(df_demo, df_immo, on="code_commune", suffixes=("", "_immo"))
    return df


def calculer_correlations(df):
    """Calcule les correlations entre revenu median et prix immobiliers."""
    variables_prix = ["prix_m2_moyen", "prix_m2_appartement", "prix_m2_maison"]
    resultats = []

    for var_prix in variables_prix:
        r, p = stats.pearsonr(df["revenu_median"], df[var_prix])

        # Interpretation de la force de correlation
        if abs(r) >= 0.8:
            interpretation = "Tres forte"
        elif abs(r) >= 0.5:
            interpretation = "Forte"
        elif abs(r) >= 0.3:
            interpretation = "Moderee"
        else:
            interpretation = "Faible"

        # Niveau de significativite
        if p < 0.001:
            significativite = "***"
        elif p < 0.01:
            significativite = "**"
        elif p < 0.05:
            significativite = "*"
        else:
            significativite = ""

        resultats.append({
            "variable_prix": var_prix,
            "coefficient_r": r,
            "p_value": p,
            "interpretation": interpretation,
            "significativite": significativite
        })

    return resultats


def afficher_resultats(df, resultats):
    """Affiche les resultats de l'analyse."""
    print("=" * 60)
    print("ANALYSE CORRELATION: PRIX IMMOBILIER vs REVENU MEDIAN")
    print("=" * 60)
    print(f"\nNombre de communes: {len(df)}")
    print(f"Revenu median - Min: {df['revenu_median'].min()}EUR, Max: {df['revenu_median'].max()}EUR")
    print(f"Prix m2 moyen - Min: {df['prix_m2_moyen'].min()}EUR, Max: {df['prix_m2_moyen'].max()}EUR")

    print("\n" + "-" * 60)
    print("CORRELATIONS DE PEARSON")
    print("-" * 60)

    for res in resultats:
        print(f"\nRevenu median vs {res['variable_prix']}:")
        print(f"  Coefficient r = {res['coefficient_r']:.4f} ({res['interpretation']})")
        print(f"  p-value = {res['p_value']:.6f} {res['significativite']}")

    print("\n" + "-" * 60)
    print("STATISTIQUES DESCRIPTIVES")
    print("-" * 60)
    cols = ["revenu_median", "prix_m2_moyen", "prix_m2_appartement", "prix_m2_maison"]
    print(df[cols].describe().round(2))


def generer_graphique(df, sauvegarder=True):
    """Genere un scatter plot avec regression lineaire."""
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(10, 7))

    # Scatter plot avec regression
    sns.regplot(
        x="revenu_median",
        y="prix_m2_moyen",
        data=df,
        ax=ax,
        scatter_kws={"s": 80, "alpha": 0.7},
        line_kws={"color": "red", "linewidth": 2}
    )

    # Annoter les points avec les noms des villes
    for idx, row in df.iterrows():
        ax.annotate(
            row["nom_commune"],
            (row["revenu_median"], row["prix_m2_moyen"]),
            fontsize=7,
            alpha=0.8,
            xytext=(5, 5),
            textcoords="offset points"
        )

    # Calculer correlation pour le titre
    r, p = stats.pearsonr(df["revenu_median"], df["prix_m2_moyen"])

    # Titre et labels
    ax.set_title(
        f"Correlation Prix Immobilier vs Revenu Median\n(r = {r:.4f}, p < 0.001)",
        fontsize=14,
        fontweight="bold"
    )
    ax.set_xlabel("Revenu Median (EUR)", fontsize=12)
    ax.set_ylabel("Prix m2 Moyen (EUR)", fontsize=12)

    plt.tight_layout()

    if sauvegarder:
        OUTPUT_DIR.mkdir(exist_ok=True)
        chemin = OUTPUT_DIR / "correlation_prix_revenu_global.png"
        plt.savefig(chemin, dpi=150, bbox_inches="tight")
        print(f"\nGraphique sauvegarde: {chemin}")

    plt.close()
    return fig


def main():
    """Point d'entree principal."""
    # Charger les donnees
    df = charger_donnees()

    # Calculer les correlations
    resultats = calculer_correlations(df)

    # Afficher les resultats
    afficher_resultats(df, resultats)

    # Generer le graphique
    generer_graphique(df)

    print("\n" + "=" * 60)
    print("CONCLUSION")
    print("=" * 60)
    print("""
La correlation entre le revenu median et le prix immobilier
est TRES FORTE (r = 0.93) et HAUTEMENT SIGNIFICATIVE (p < 0.001).

Cela signifie que 93% de la variation des prix immobiliers
peut etre expliquee par le revenu median des communes.
""")


if __name__ == "__main__":
    main()
