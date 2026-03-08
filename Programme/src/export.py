"""
Module d'export des resultats
Permet d'exporter les analyses en format CSV
"""
import pandas as pd
from pathlib import Path
from typing import Dict
from config import OUTPUT_DIR


def exporter_resultats_csv(resultats_globaux: Dict, nom_fichier: str = "resultats_analyse.csv") -> Path:
    """
    Exporte les resultats de correlation en CSV.

    Args:
        resultats_globaux: Dictionnaire des resultats par categorie
        nom_fichier: Nom du fichier de sortie

    Returns:
        Chemin du fichier cree
    """
    lignes = []

    for categorie, resultats in resultats_globaux.items():
        matrice = resultats["matrice_complete"]

        for _, row in matrice.iterrows():
            lignes.append({
                "categorie": categorie,
                "nb_communes": resultats["nb_communes"],
                "variable_demo": row["variable_demo"],
                "variable_prix": row["variable_prix"],
                "correlation": row["correlation"],
                "p_value": row["p_value"],
                "significatif": row["significatif"],
                "interpretation": row["interpretation"]
            })

    df_export = pd.DataFrame(lignes)

    # Tri par categorie puis par correlation (valeur absolue)
    df_export["abs_correlation"] = df_export["correlation"].abs()
    df_export = df_export.sort_values(
        by=["categorie", "abs_correlation"],
        ascending=[True, False]
    )
    df_export.drop(columns=["abs_correlation"], inplace=True)

    chemin = OUTPUT_DIR / nom_fichier
    df_export.to_csv(chemin, index=False, encoding="utf-8-sig")

    return chemin


def exporter_synthese_csv(resultats_globaux: Dict, nom_fichier: str = "synthese_correlations.csv") -> Path:
    """
    Exporte une synthese des meilleures correlations par categorie.

    Args:
        resultats_globaux: Dictionnaire des resultats par categorie
        nom_fichier: Nom du fichier de sortie

    Returns:
        Chemin du fichier cree
    """
    synthese = []

    for categorie, resultats in resultats_globaux.items():
        corr_fortes = resultats["correlations_fortes"]

        if len(corr_fortes) > 0:
            # Meilleure correlation
            meilleure = corr_fortes.iloc[0]
            synthese.append({
                "categorie": categorie,
                "nb_communes": resultats["nb_communes"],
                "variable_demo": meilleure["variable_demo"],
                "variable_prix": meilleure["variable_prix"],
                "correlation": meilleure["correlation"],
                "p_value": meilleure["p_value"],
                "interpretation": meilleure["interpretation"]
            })
        else:
            synthese.append({
                "categorie": categorie,
                "nb_communes": resultats["nb_communes"],
                "variable_demo": "N/A",
                "variable_prix": "N/A",
                "correlation": None,
                "p_value": None,
                "interpretation": "Aucune correlation significative"
            })

    df_synthese = pd.DataFrame(synthese)
    chemin = OUTPUT_DIR / nom_fichier
    df_synthese.to_csv(chemin, index=False, encoding="utf-8-sig")

    return chemin
