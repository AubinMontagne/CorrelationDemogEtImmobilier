"""
Module de calcul des corrélations
Implémente le coefficient de corrélation de Pearson
"""
import pandas as pd
import numpy as np
from scipy import stats
from typing import Tuple, Dict, List


def calculer_correlation_pearson(x: np.ndarray, y: np.ndarray) -> Tuple[float, float]:
    """
    Calcule le coefficient de corrélation de Pearson entre deux variables.

    Args:
        x: Premier tableau de valeurs
        y: Deuxième tableau de valeurs

    Returns:
        Tuple (coefficient de corrélation, p-value)
    """
    # Suppression des valeurs manquantes
    mask = ~(np.isnan(x) | np.isnan(y))
    x_clean = x[mask]
    y_clean = y[mask]

    if len(x_clean) < 3:
        return np.nan, np.nan

    correlation, p_value = stats.pearsonr(x_clean, y_clean)
    return correlation, p_value


def interpreter_correlation(coef: float) -> str:
    """
    Interprète la force de la corrélation.

    Args:
        coef: Coefficient de corrélation (-1 à 1)

    Returns:
        Interprétation textuelle
    """
    if np.isnan(coef):
        return "Indéterminé (données insuffisantes)"

    abs_coef = abs(coef)
    signe = "positive" if coef > 0 else "négative"

    if abs_coef >= 0.9:
        force = "très forte"
    elif abs_coef >= 0.7:
        force = "forte"
    elif abs_coef >= 0.5:
        force = "modérée"
    elif abs_coef >= 0.3:
        force = "faible"
    else:
        force = "très faible ou nulle"

    return f"Corrélation {signe} {force} ({coef:.3f})"


def matrice_correlation(df: pd.DataFrame,
                        colonnes_demo: List[str],
                        colonnes_prix: List[str]) -> pd.DataFrame:
    """
    Calcule la matrice de corrélation entre variables démographiques et prix.

    Args:
        df: DataFrame avec toutes les données
        colonnes_demo: Liste des colonnes démographiques à analyser
        colonnes_prix: Liste des colonnes de prix à analyser

    Returns:
        DataFrame contenant la matrice de corrélation
    """
    resultats = []

    for col_demo in colonnes_demo:
        if col_demo not in df.columns:
            continue

        for col_prix in colonnes_prix:
            if col_prix not in df.columns:
                continue

            coef, p_value = calculer_correlation_pearson(
                df[col_demo].values,
                df[col_prix].values
            )

            resultats.append({
                "variable_demo": col_demo,
                "variable_prix": col_prix,
                "correlation": coef,
                "p_value": p_value,
                "interpretation": interpreter_correlation(coef),
                "significatif": p_value < 0.05 if not np.isnan(p_value) else False
            })

    return pd.DataFrame(resultats)


def analyser_correlations_categorie(df: pd.DataFrame,
                                    nom_categorie: str) -> Dict:
    """
    Analyse les corrélations pour une catégorie de villes.

    Args:
        df: DataFrame filtré pour la catégorie
        nom_categorie: Nom de la catégorie

    Returns:
        Dictionnaire avec les résultats d'analyse
    """
    colonnes_demo = ["densite", "age_moyen", "taux_chomage",
                     "revenu_median", "taux_diplomes_sup", "taux_proprietaires"]
    colonnes_prix = ["prix_m2_moyen", "prix_m2_appartement", "prix_m2_maison"]

    colonnes_demo = [c for c in colonnes_demo if c in df.columns]
    colonnes_prix = [c for c in colonnes_prix if c in df.columns]

    matrice = matrice_correlation(df, colonnes_demo, colonnes_prix)

    correlations_fortes = matrice[
        (matrice["significatif"] == True) &
        (abs(matrice["correlation"]) >= 0.5)
    ].sort_values("correlation", key=abs, ascending=False)

    return {
        "categorie": nom_categorie,
        "nb_communes": len(df),
        "matrice_complete": matrice,
        "correlations_fortes": correlations_fortes,
        "colonnes_demo_analysees": colonnes_demo,
        "colonnes_prix_analysees": colonnes_prix
    }


def afficher_rapport_correlation(resultats: Dict) -> None:
    """
    Affiche un rapport lisible des résultats de corrélation.

    Args:
        resultats: Dictionnaire retourné par analyser_correlations_categorie
    """
    print("=" * 60)
    print(f"ANALYSE DE CORRÉLATION - {resultats['categorie'].upper()}")
    print("=" * 60)
    print(f"Nombre de communes analysées: {resultats['nb_communes']}")
    print()

    print("CORRÉLATIONS SIGNIFICATIVES (|r| >= 0.5, p < 0.05):")
    print("-" * 60)

    if len(resultats["correlations_fortes"]) == 0:
        print("Aucune corrélation forte significative détectée.")
    else:
        for _, row in resultats["correlations_fortes"].iterrows():
            print(f"  {row['variable_demo']} <-> {row['variable_prix']}")
            print(f"    {row['interpretation']}")
            print(f"    p-value: {row['p_value']:.4f}")
            print()

    print("=" * 60)


if __name__ == "__main__":
    # Test avec des données fictives
    np.random.seed(42)
    n = 50

    revenu = np.random.normal(30000, 5000, n)
    prix = revenu * 0.1 + np.random.normal(0, 500, n)  # Corrélation positive

    coef, p_val = calculer_correlation_pearson(revenu, prix)
    print(f"Test corrélation revenu-prix:")
    print(f"  Coefficient: {coef:.3f}")
    print(f"  P-value: {p_val:.4f}")
    print(f"  {interpreter_correlation(coef)}")
