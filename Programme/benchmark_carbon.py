"""
Benchmark d'empreinte carbone de l'application
Projet R6.05 - BUT3 Informatique
"""
import time
import sys
import psutil
import os
from pathlib import Path

# Ajout du dossier src au path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from codecarbon import EmissionsTracker
import pandas as pd

from config import CATEGORIES_VILLES, OUTPUT_DIR
from data_loader import charger_et_preparer_donnees
from correlation import analyser_correlations_categorie
from visualization import generer_rapport_graphique


def benchmark_application():
    """Execute le benchmark complet de l'application."""

    print("=" * 70)
    print("BENCHMARK EMPREINTE CARBONE - Projet Immobilier/Demographie")
    print("=" * 70)

    # Informations systeme
    print("\n1. INFORMATIONS SYSTEME")
    print("-" * 50)
    print(f"   CPU: {psutil.cpu_count(logical=False)} coeurs physiques, {psutil.cpu_count()} threads")
    print(f"   RAM: {psutil.virtual_memory().total / (1024**3):.1f} Go")
    print(f"   Python: {sys.version.split()[0]}")

    # Demarrage du tracker
    tracker = EmissionsTracker(
        project_name="projet-immo-r605",
        measure_power_secs=0.5,
        save_to_file=True,
        output_dir=str(OUTPUT_DIR),
        log_level="warning"
    )

    print("\n2. MESURE DE L'EXECUTION")
    print("-" * 50)

    # Mesure memoire initiale
    process = psutil.Process(os.getpid())
    mem_avant = process.memory_info().rss / (1024 * 1024)

    tracker.start()
    temps_debut = time.time()

    # --- EXECUTION DE L'APPLICATION ---

    # Chargement des donnees
    t1 = time.time()
    df = charger_et_preparer_donnees()
    temps_chargement = time.time() - t1

    # Analyse de toutes les categories
    resultats_globaux = {}
    temps_analyses = {}

    for categorie, villes in CATEGORIES_VILLES.items():
        t_cat = time.time()
        df_cat = df[df["nom_commune"].isin(villes)].copy()

        if len(df_cat) > 0:
            resultats = analyser_correlations_categorie(df_cat, categorie)
            resultats_globaux[categorie] = resultats

            # Generation des graphiques (sans affichage)
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            generer_rapport_graphique(df_cat, resultats, categorie)
            plt.close('all')

        temps_analyses[categorie] = time.time() - t_cat

    # --- FIN EXECUTION ---

    temps_total = time.time() - temps_debut
    emissions = tracker.stop()

    # Mesure memoire finale
    mem_apres = process.memory_info().rss / (1024 * 1024)

    # Affichage des resultats
    print(f"\n   Temps total d'execution: {temps_total:.3f} secondes")
    print(f"   - Chargement donnees: {temps_chargement:.3f} s")
    for cat, t in temps_analyses.items():
        print(f"   - Analyse {cat}: {t:.3f} s")

    print(f"\n   Memoire utilisee: {mem_apres - mem_avant:.1f} Mo (delta)")
    print(f"   Memoire pic: {mem_apres:.1f} Mo")

    print("\n3. EMPREINTE CARBONE")
    print("-" * 50)

    if emissions:
        # Conversion en unites comprehensibles
        emissions_mg = emissions * 1_000_000  # kg -> mg

        print(f"   Emissions CO2: {emissions_mg:.4f} mg")
        print(f"   Equivalent: {emissions * 1000:.6f} g CO2")

        # Equivalences
        print("\n   EQUIVALENCES:")
        # 1 email = ~4g CO2, 1 recherche Google = ~0.2g CO2
        # 1 km en voiture = ~120g CO2
        emails_equiv = (emissions * 1000) / 4
        google_equiv = (emissions * 1000) / 0.2
        km_voiture = (emissions * 1000) / 120

        print(f"   - {emails_equiv:.4f} emails envoyes")
        print(f"   - {google_equiv:.4f} recherches Google")
        print(f"   - {km_voiture:.6f} km en voiture")

        # Estimation annuelle (1000 executions/an)
        emissions_annuelles = emissions * 1000 * 1000  # g/an
        print(f"\n   Si 1000 executions/an: {emissions_annuelles:.2f} g CO2/an")
    else:
        print("   Emissions non mesurees (tracker non disponible)")

    print("\n4. ANALYSE PAR COMPOSANT")
    print("-" * 50)

    # Estimation de la repartition
    total_analyse = sum(temps_analyses.values())
    print(f"   Chargement CSV: {(temps_chargement/temps_total)*100:.1f}%")
    print(f"   Calculs Pearson: {(total_analyse*0.3/temps_total)*100:.1f}%")
    print(f"   Generation graphiques: {(total_analyse*0.7/temps_total)*100:.1f}%")

    print("\n5. OPTIMISATIONS POSSIBLES")
    print("-" * 50)
    print("   - Mise en cache des donnees chargees")
    print("   - Generation graphiques a la demande (lazy)")
    print("   - Utilisation de formats binaires (Parquet vs CSV)")
    print("   - Reduction resolution graphiques pour usage web")

    print("\n" + "=" * 70)
    print("Rapport sauvegarde dans: output/emissions.csv")
    print("=" * 70)

    return emissions, temps_total, mem_apres - mem_avant


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    benchmark_application()
