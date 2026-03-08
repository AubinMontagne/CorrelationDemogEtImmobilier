"""
Module de chargement des données
Gère le chargement des fichiers CSV (démographiques et immobiliers)
"""
import pandas as pd
from pathlib import Path
from config import DEMO_DIR, IMMO_DIR, COLONNES_DEMO, COLONNES_IMMO


def charger_donnees_demographiques(fichier: str = "demographiques.csv") -> pd.DataFrame:
    """
    Charge les données démographiques depuis un fichier CSV.

    Args:
        fichier: Nom du fichier CSV dans le dossier data/demographiques

    Returns:
        DataFrame contenant les données démographiques
    """
    chemin = DEMO_DIR / fichier

    if not chemin.exists():
        raise FileNotFoundError(f"Fichier non trouvé: {chemin}")

    df = pd.read_csv(chemin, encoding="utf-8")
    return df


def charger_donnees_immobilieres(fichier: str = "immobilier.csv") -> pd.DataFrame:
    """
    Charge les données immobilières depuis un fichier CSV.

    Args:
        fichier: Nom du fichier CSV dans le dossier data/immobilier

    Returns:
        DataFrame contenant les données immobilières
    """
    chemin = IMMO_DIR / fichier

    if not chemin.exists():
        raise FileNotFoundError(f"Fichier non trouvé: {chemin}")

    df = pd.read_csv(chemin, encoding="utf-8")
    return df


def fusionner_donnees(df_demo: pd.DataFrame, df_immo: pd.DataFrame) -> pd.DataFrame:
    """
    Fusionne les données démographiques et immobilières sur le code commune.

    Args:
        df_demo: DataFrame des données démographiques
        df_immo: DataFrame des données immobilières

    Returns:
        DataFrame fusionné
    """
    # Fusion sur le code commune
    df_merged = pd.merge(
        df_demo,
        df_immo,
        on="code_commune",
        how="inner",
        suffixes=("_demo", "_immo")
    )

    # Nettoyage des colonnes nom_commune dupliquées
    if "nom_commune_demo" in df_merged.columns:
        df_merged["nom_commune"] = df_merged["nom_commune_demo"]
        df_merged.drop(columns=["nom_commune_demo", "nom_commune_immo"], inplace=True)

    return df_merged


def filtrer_par_categorie(df: pd.DataFrame, categorie: str,
                          mapping_villes: dict) -> pd.DataFrame:
    """
    Filtre le DataFrame pour ne garder que les villes d'une catégorie.

    Args:
        df: DataFrame complet
        categorie: Nom de la catégorie (ex: "bord_de_mer")
        mapping_villes: Dictionnaire catégorie -> liste de villes

    Returns:
        DataFrame filtré
    """
    if categorie not in mapping_villes:
        raise ValueError(f"Catégorie inconnue: {categorie}")

    villes = mapping_villes[categorie]
    return df[df["nom_commune"].isin(villes)].copy()


def charger_et_preparer_donnees(fichier_demo: str = "demographiques.csv",
                                 fichier_immo: str = "immobilier.csv") -> pd.DataFrame:
    """
    Fonction principale qui charge et fusionne toutes les données.

    Args:
        fichier_demo: Nom du fichier démographique
        fichier_immo: Nom du fichier immobilier

    Returns:
        DataFrame prêt pour l'analyse
    """
    df_demo = charger_donnees_demographiques(fichier_demo)
    df_immo = charger_donnees_immobilieres(fichier_immo)
    df_final = fusionner_donnees(df_demo, df_immo)

    print(f"Données chargées: {len(df_final)} communes")
    return df_final


if __name__ == "__main__":
    # Test du module
    try:
        df = charger_et_preparer_donnees()
        print(df.head())
    except FileNotFoundError as e:
        print(f"Erreur: {e}")
        print("Assurez-vous que les fichiers CSV sont présents dans data/")
