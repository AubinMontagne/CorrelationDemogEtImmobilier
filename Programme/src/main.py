"""
Application principale - Analyse de corrélation immobilier/démographie
Projet R6.05 - BUT3 Informatique

Usage:
    python main.py                      # Analyse complète
    python main.py --categorie montagne # Analyse d'une catégorie spécifique
    python main.py --liste              # Liste les catégories disponibles
    python main.py --export-csv         # Analyse + export CSV des résultats
    python main.py --interactif         # Mode interactif
"""
import argparse
import sys
from pathlib import Path

# Ajout du dossier src au path
sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
import matplotlib.pyplot as plt

from config import CATEGORIES_VILLES, OUTPUT_DIR
from data_loader import charger_et_preparer_donnees, filtrer_par_categorie
from correlation import analyser_correlations_categorie, afficher_rapport_correlation
from visualization import (
    generer_rapport_graphique,
    creer_heatmap_correlations,
    creer_barplot_prix_par_categorie
)
from export import exporter_resultats_csv, exporter_synthese_csv


def analyser_categorie(df: pd.DataFrame, categorie: str) -> dict:
    """
    Analyse complète d'une catégorie de villes.

    Args:
        df: DataFrame complet
        categorie: Nom de la catégorie

    Returns:
        Résultats de l'analyse
    """
    print(f"\n{'='*60}")
    print(f"Analyse de la catégorie: {categorie.upper()}")
    print('='*60)

    # Filtrage des données
    try:
        df_categorie = filtrer_par_categorie(df, categorie, CATEGORIES_VILLES)
    except ValueError as e:
        print(f"Erreur: {e}")
        return None

    if len(df_categorie) == 0:
        print(f"Aucune donnée trouvée pour la catégorie '{categorie}'")
        return None

    print(f"Communes trouvées: {len(df_categorie)}")
    print(f"Villes: {', '.join(df_categorie['nom_commune'].tolist())}")

    # Analyse des corrélations
    resultats = analyser_correlations_categorie(df_categorie, categorie)
    afficher_rapport_correlation(resultats)

    # Génération des graphiques
    print("\nGénération des graphiques...")
    generer_rapport_graphique(df_categorie, resultats, categorie)

    return resultats


def analyser_toutes_categories(df: pd.DataFrame) -> dict:
    """
    Analyse toutes les catégories de villes.

    Args:
        df: DataFrame complet

    Returns:
        Dictionnaire avec tous les résultats
    """
    resultats_globaux = {}

    for categorie in CATEGORIES_VILLES.keys():
        resultats = analyser_categorie(df, categorie)
        if resultats:
            resultats_globaux[categorie] = resultats

    return resultats_globaux


def generer_synthese(resultats_globaux: dict, export_csv: bool = False) -> None:
    """
    Génère une synthèse comparative des catégories.

    Args:
        resultats_globaux: Résultats de toutes les analyses
        export_csv: Si True, exporte les résultats en CSV
    """
    print("\n" + "="*60)
    print("SYNTHÈSE GLOBALE")
    print("="*60)

    # Compilation des corrélations fortes par catégorie
    synthese = []
    for categorie, resultats in resultats_globaux.items():
        corr_fortes = resultats["correlations_fortes"]
        if len(corr_fortes) > 0:
            meilleure = corr_fortes.iloc[0]
            synthese.append({
                "categorie": categorie,
                "nb_communes": resultats["nb_communes"],
                "meilleure_correlation": f"{meilleure['variable_demo']} <-> {meilleure['variable_prix']}",
                "coefficient": meilleure["correlation"]
            })

    if synthese:
        df_synthese = pd.DataFrame(synthese)
        print("\nMeilleures corrélations par catégorie:")
        print("-"*60)
        for _, row in df_synthese.iterrows():
            print(f"  {row['categorie']}: {row['meilleure_correlation']}")
            print(f"    Coefficient: {row['coefficient']:.3f} ({row['nb_communes']} communes)")
    else:
        print("Aucune corrélation significative trouvée.")

    # Export CSV si demandé
    if export_csv:
        print("\nExport des résultats en CSV...")
        chemin_complet = exporter_resultats_csv(resultats_globaux)
        print(f"  Résultats complets: {chemin_complet}")
        chemin_synthese = exporter_synthese_csv(resultats_globaux)
        print(f"  Synthèse: {chemin_synthese}")


def lister_categories() -> None:
    """Affiche la liste des catégories disponibles."""
    print("\nCatégories de villes disponibles:")
    print("-"*40)
    for categorie, villes in CATEGORIES_VILLES.items():
        print(f"\n  {categorie}:")
        for ville in villes:
            print(f"    - {ville}")


def mode_interactif(df: pd.DataFrame) -> None:
    """
    Mode interactif permettant de choisir les analyses à effectuer.

    Args:
        df: DataFrame avec les données chargées
    """
    categories = list(CATEGORIES_VILLES.keys())

    while True:
        print("\n" + "="*60)
        print("MODE INTERACTIF")
        print("="*60)
        print("\nOptions disponibles:")
        print("  1. Analyser toutes les catégories")
        print("  2. Analyser une catégorie spécifique")
        print("  3. Lister les catégories")
        print("  4. Exporter les résultats en CSV")
        print("  0. Quitter")
        print()

        choix = input("Votre choix (0-4): ").strip()

        if choix == "0":
            print("Au revoir!")
            break
        elif choix == "1":
            resultats = analyser_toutes_categories(df)
            generer_synthese(resultats)
        elif choix == "2":
            print("\nCatégories disponibles:")
            for i, cat in enumerate(categories, 1):
                print(f"  {i}. {cat}")
            try:
                num = int(input("\nNuméro de la catégorie: ").strip())
                if 1 <= num <= len(categories):
                    analyser_categorie(df, categories[num - 1])
                else:
                    print("Numéro invalide.")
            except ValueError:
                print("Veuillez entrer un numéro valide.")
        elif choix == "3":
            lister_categories()
        elif choix == "4":
            print("\nAnalyse en cours pour export...")
            resultats = analyser_toutes_categories(df)
            generer_synthese(resultats, export_csv=True)
        else:
            print("Option non reconnue.")


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(
        description="Analyse de corrélation entre données démographiques et prix immobiliers"
    )
    parser.add_argument(
        "--categorie", "-c",
        type=str,
        help="Analyser une catégorie spécifique"
    )
    parser.add_argument(
        "--liste", "-l",
        action="store_true",
        help="Lister les catégories disponibles"
    )
    parser.add_argument(
        "--fichier-demo",
        type=str,
        default="demographiques.csv",
        help="Fichier de données démographiques"
    )
    parser.add_argument(
        "--fichier-immo",
        type=str,
        default="immobilier.csv",
        help="Fichier de données immobilières"
    )
    parser.add_argument(
        "--export-csv",
        action="store_true",
        help="Exporter les résultats en CSV"
    )
    parser.add_argument(
        "--interactif", "-i",
        action="store_true",
        help="Lancer le mode interactif"
    )

    args = parser.parse_args()

    # Affichage de la liste des catégories
    if args.liste:
        lister_categories()
        return

    # Création du dossier output si nécessaire
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("="*60)
    print("ANALYSE CORRÉLATION IMMOBILIER / DÉMOGRAPHIE")
    print("Projet R6.05 - BUT3 Informatique")
    print("="*60)

    # Chargement des données
    try:
        df = charger_et_preparer_donnees(args.fichier_demo, args.fichier_immo)
    except FileNotFoundError as e:
        print(f"\nErreur: {e}")
        print("\nAssurez-vous que les fichiers CSV sont présents:")
        print(f"  - data/demographiques/{args.fichier_demo}")
        print(f"  - data/immobilier/{args.fichier_immo}")
        return

    # Mode interactif
    if args.interactif:
        mode_interactif(df)
        return

    # Analyse
    if args.categorie:
        # Analyse d'une seule catégorie
        analyser_categorie(df, args.categorie)
    else:
        # Analyse de toutes les catégories
        resultats = analyser_toutes_categories(df)
        generer_synthese(resultats, export_csv=args.export_csv)

    print(f"\nGraphiques sauvegardés dans: {OUTPUT_DIR}")
    print("\nAnalyse terminée.")


if __name__ == "__main__":
    main()
