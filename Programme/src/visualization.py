"""
Module de visualisation
Génère les graphiques de corrélation
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import List, Optional
from config import OUTPUT_DIR


# Configuration du style des graphiques
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")


def creer_scatter_correlation(df: pd.DataFrame,
                               col_x: str,
                               col_y: str,
                               titre: str = None,
                               categorie: str = None,
                               sauvegarder: bool = True) -> plt.Figure:
    """
    Crée un nuage de points avec ligne de régression.

    Args:
        df: DataFrame avec les données
        col_x: Colonne pour l'axe X (variable démographique)
        col_y: Colonne pour l'axe Y (prix immobilier)
        titre: Titre du graphique (optionnel)
        categorie: Nom de la catégorie pour le nom de fichier
        sauvegarder: Si True, sauvegarde le graphique

    Returns:
        Figure matplotlib
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Nuage de points
    ax.scatter(df[col_x], df[col_y], alpha=0.6, s=100, edgecolors='white')

    # Ligne de régression
    if len(df) >= 2:
        z = np.polyfit(df[col_x].dropna(), df[col_y].dropna(), 1)
        p = np.poly1d(z)
        x_line = np.linspace(df[col_x].min(), df[col_x].max(), 100)
        ax.plot(x_line, p(x_line), "r--", alpha=0.8, linewidth=2,
                label="Régression linéaire")

    # Labels
    ax.set_xlabel(col_x.replace("_", " ").title(), fontsize=12)
    ax.set_ylabel(col_y.replace("_", " ").title(), fontsize=12)

    if titre:
        ax.set_title(titre, fontsize=14, fontweight='bold')
    else:
        ax.set_title(f"Corrélation: {col_x} vs {col_y}", fontsize=14)

    # Annotations des villes
    if "nom_commune" in df.columns and len(df) <= 20:
        for idx, row in df.iterrows():
            ax.annotate(row["nom_commune"],
                       (row[col_x], row[col_y]),
                       fontsize=8,
                       alpha=0.7,
                       xytext=(5, 5),
                       textcoords='offset points')

    ax.legend()
    plt.tight_layout()

    if sauvegarder:
        nom_fichier = f"scatter_{col_x}_vs_{col_y}"
        if categorie:
            nom_fichier = f"{categorie}_{nom_fichier}"
        chemin = OUTPUT_DIR / f"{nom_fichier}.png"
        fig.savefig(chemin, dpi=150, bbox_inches='tight')
        print(f"Graphique sauvegardé: {chemin}")

    return fig


def creer_heatmap_correlations(matrice_corr: pd.DataFrame,
                                titre: str = "Matrice de corrélation",
                                categorie: str = None,
                                sauvegarder: bool = True) -> plt.Figure:
    """
    Crée une heatmap de la matrice de corrélation.

    Args:
        matrice_corr: DataFrame pivotée avec les corrélations
        titre: Titre du graphique
        categorie: Nom de la catégorie
        sauvegarder: Si True, sauvegarde le graphique

    Returns:
        Figure matplotlib
    """
    fig, ax = plt.subplots(figsize=(10, 8))

    # Création de la heatmap
    sns.heatmap(matrice_corr,
                annot=True,
                fmt=".2f",
                cmap="RdBu_r",
                center=0,
                vmin=-1,
                vmax=1,
                square=True,
                linewidths=0.5,
                ax=ax,
                cbar_kws={"label": "Coefficient de corrélation"})

    ax.set_title(titre, fontsize=14, fontweight='bold', pad=20)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)

    plt.tight_layout()

    if sauvegarder:
        nom_fichier = "heatmap_correlations"
        if categorie:
            nom_fichier = f"{categorie}_{nom_fichier}"
        chemin = OUTPUT_DIR / f"{nom_fichier}.png"
        fig.savefig(chemin, dpi=150, bbox_inches='tight')
        print(f"Heatmap sauvegardée: {chemin}")

    return fig


def creer_barplot_prix_par_categorie(df: pd.DataFrame,
                                      col_categorie: str,
                                      col_prix: str = "prix_m2_moyen",
                                      sauvegarder: bool = True) -> plt.Figure:
    """
    Crée un barplot des prix moyens par catégorie.

    Args:
        df: DataFrame avec les données
        col_categorie: Colonne contenant les catégories
        col_prix: Colonne des prix
        sauvegarder: Si True, sauvegarde le graphique

    Returns:
        Figure matplotlib
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    # Calcul des moyennes par catégorie
    moyennes = df.groupby(col_categorie)[col_prix].mean().sort_values(ascending=True)

    # Barplot horizontal
    colors = sns.color_palette("viridis", len(moyennes))
    bars = ax.barh(moyennes.index, moyennes.values, color=colors)

    # Ajout des valeurs sur les barres
    for bar, val in zip(bars, moyennes.values):
        ax.text(val + 50, bar.get_y() + bar.get_height()/2,
                f'{val:.0f} EUR/m²',
                va='center', fontsize=10)

    ax.set_xlabel("Prix moyen au m² (EUR)", fontsize=12)
    ax.set_ylabel("Catégorie de ville", fontsize=12)
    ax.set_title("Prix immobilier moyen par catégorie de ville",
                 fontsize=14, fontweight='bold')

    plt.tight_layout()

    if sauvegarder:
        chemin = OUTPUT_DIR / "barplot_prix_par_categorie.png"
        fig.savefig(chemin, dpi=150, bbox_inches='tight')
        print(f"Barplot sauvegardé: {chemin}")

    return fig


def creer_boxplot_comparaison(df: pd.DataFrame,
                               col_categorie: str,
                               col_valeur: str,
                               titre: str = None,
                               sauvegarder: bool = True) -> plt.Figure:
    """
    Crée un boxplot pour comparer les distributions par catégorie.

    Args:
        df: DataFrame avec les données
        col_categorie: Colonne des catégories
        col_valeur: Colonne des valeurs à comparer
        titre: Titre optionnel
        sauvegarder: Si True, sauvegarde le graphique

    Returns:
        Figure matplotlib
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    # Boxplot
    df.boxplot(column=col_valeur, by=col_categorie, ax=ax)

    if titre:
        ax.set_title(titre, fontsize=14, fontweight='bold')
    else:
        ax.set_title(f"Distribution de {col_valeur} par catégorie",
                     fontsize=14, fontweight='bold')

    plt.suptitle("")  # Supprime le titre automatique
    ax.set_xlabel("Catégorie", fontsize=12)
    ax.set_ylabel(col_valeur.replace("_", " ").title(), fontsize=12)

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    if sauvegarder:
        chemin = OUTPUT_DIR / f"boxplot_{col_valeur}.png"
        fig.savefig(chemin, dpi=150, bbox_inches='tight')
        print(f"Boxplot sauvegardé: {chemin}")

    return fig


def generer_rapport_graphique(df: pd.DataFrame,
                               resultats_correlation: dict,
                               categorie: str) -> List[plt.Figure]:
    """
    Génère tous les graphiques pour une catégorie.

    Args:
        df: DataFrame filtré pour la catégorie
        resultats_correlation: Résultats de l'analyse de corrélation
        categorie: Nom de la catégorie

    Returns:
        Liste des figures générées
    """
    figures = []

    # 1. Heatmap des corrélations
    matrice = resultats_correlation["matrice_complete"]
    if len(matrice) > 0:
        # Pivot pour créer la matrice
        pivot = matrice.pivot(
            index="variable_demo",
            columns="variable_prix",
            values="correlation"
        )
        fig_heat = creer_heatmap_correlations(
            pivot,
            titre=f"Corrélations - {categorie.replace('_', ' ').title()}",
            categorie=categorie
        )
        figures.append(fig_heat)

    # 2. Scatter plots pour les corrélations fortes
    for _, row in resultats_correlation["correlations_fortes"].head(3).iterrows():
        fig_scatter = creer_scatter_correlation(
            df,
            row["variable_demo"],
            row["variable_prix"],
            titre=f"{categorie.replace('_', ' ').title()}: {row['interpretation']}",
            categorie=categorie
        )
        figures.append(fig_scatter)

    return figures


if __name__ == "__main__":
    # Test avec données fictives
    np.random.seed(42)

    # Création de données de test
    data = {
        "nom_commune": ["Ville A", "Ville B", "Ville C", "Ville D", "Ville E"],
        "revenu_median": [25000, 30000, 35000, 28000, 32000],
        "prix_m2_moyen": [2500, 3200, 4000, 2800, 3500],
        "densite": [500, 1200, 800, 600, 1000]
    }
    df_test = pd.DataFrame(data)

    # Test scatter plot
    fig = creer_scatter_correlation(
        df_test,
        "revenu_median",
        "prix_m2_moyen",
        titre="Test: Revenu vs Prix",
        sauvegarder=False
    )
    plt.show()
