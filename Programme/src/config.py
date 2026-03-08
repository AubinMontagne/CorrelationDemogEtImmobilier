"""
Configuration du projet - Chemins et constantes
"""
from pathlib import Path

# Chemins des dossiers
ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"
DEMO_DIR = DATA_DIR / "demographiques"
IMMO_DIR = DATA_DIR / "immobilier"
OUTPUT_DIR = ROOT_DIR / "output"

# Catégories de villes définies dans l'analyse
CATEGORIES_VILLES = {
    "frontiere": [
        "Annemasse", "Saint-Louis", "Thonon-les-Bains", "Menton", "Hendaye"
    ],
    "bord_de_mer": [
        "Toulon", "Le Havre", "Brest", "La Rochelle", "Lorient", "Cannes"
    ],
    "montagne": [
        "Grenoble", "Annecy", "Chambéry", "Pau", "Gap"
    ],
    "fort_ensoleillement": [
        "Nîmes", "Aix-en-Provence", "Perpignan", "Avignon", "Béziers", "Fréjus"
    ],
    "faible_ensoleillement": [
        "Amiens", "Metz", "Rouen", "Caen", "Nancy", "Dunkerque"
    ],
    "forte_densite": [
        "Boulogne-Billancourt", "Villeurbanne", "Saint-Denis",
        "Levallois-Perret", "Vincennes"
    ]
}

# Colonnes des données démographiques
COLONNES_DEMO = [
    "code_commune",
    "nom_commune",
    "population",
    "densite",
    "age_moyen",
    "taux_chomage",
    "revenu_median",
    "taux_diplomes_sup",
    "taux_proprietaires"
]

# Colonnes des données immobilières
COLONNES_IMMO = [
    "code_commune",
    "nom_commune",
    "prix_m2_moyen",
    "prix_m2_appartement",
    "prix_m2_maison",
    "nb_transactions"
]
